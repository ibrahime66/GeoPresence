from datetime import timedelta

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import IntegrityError, connection, transaction
from django.db.models import Count, Q, Sum
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from apps.absences.models import Absence
from apps.accounts.mixins import RoleRequiredMixin
from apps.agencies.models import Agency
from apps.announcements import services as announcement_services
from apps.attendance import services as attendance_services
from apps.attendance.models import Attendance
from apps.employees.models import Employee
from apps.employees.services import get_active_employee
from apps.leaves.models import Leave
from apps.schedules.models import Schedule
from apps.tenants.org_settings import get_org_setting

DEFAULT_PAGE_SIZE = 25


def paginate_queryset(request, queryset, page_size=DEFAULT_PAGE_SIZE):
    """Pagination manuelle pour les TemplateView qui construisent leur contexte
    à la main (pas de ListView) — mêmes noms de contexte (`page_obj`,
    `is_paginated`) que Django's MultipleObjectMixin, pour rester compatible
    avec templates/_pagination.html."""
    page_obj = Paginator(queryset, page_size).get_page(request.GET.get("page"))
    return {"page_obj": page_obj, "is_paginated": page_obj.has_other_pages()}


def health_check(request):
    """Endpoint public sans authentification (pas de tenant à résoudre) —
    utilisé par Nginx/Uptime Robot pour vérifier que la base et le cache
    répondent. Ne jamais exposer d'information interne dans la réponse."""
    checks = {}
    overall_ok = True

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"
        overall_ok = False

    try:
        cache.set("health_check", "ok", 5)
        checks["cache"] = "ok" if cache.get("health_check") == "ok" else "error"
        if checks["cache"] != "ok":
            overall_ok = False
    except Exception:
        checks["cache"] = "error"
        overall_ok = False

    status = "healthy" if overall_ok else "unhealthy"
    return JsonResponse({"status": status, "checks": checks}, status=200 if overall_ok else 503)


class ServiceWorkerView(View):
    """Sert service-worker.js à la racine du domaine (pas sous /static/) —
    la portée maximale d'un Service Worker est son propre répertoire de
    service ; le servir depuis /static/ limiterait son contrôle aux seules
    URLs /static/*, hors de portée du reste de l'application (CDC §4.4)."""

    def get(self, request):
        content = (settings.BASE_DIR / "static" / "service-worker.js").read_text(encoding="utf-8")
        response = HttpResponse(content, content_type="application/javascript")
        response["Service-Worker-Allowed"] = "/"
        response["Cache-Control"] = "no-cache"
        return response


class RobotsTxtView(View):
    """robots.txt à la racine du domaine — autorise l'indexation des pages
    publiques et pointe les moteurs de recherche vers le sitemap (référencement
    du nom "GeoPresence")."""

    def get(self, request):
        lines = [
            "User-agent: *",
            "Allow: /$",
            "Allow: /confidentialite/",
            "Allow: /conditions-utilisation/",
            "Allow: /faq/",
            "Allow: /accounts/login/",
            "Disallow: /dashboard/",
            "Disallow: /admin/",
            f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
        ]
        return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


class GoogleSiteVerificationView(View):
    """Fichier de vérification de propriété Google Search Console — le contenu
    doit correspondre exactement à celui fourni par Google pour ce site."""

    def get(self, request):
        return HttpResponse("google-site-verification: google11cfdbf23fe92380.html", content_type="text/html")


class SitemapXmlView(View):
    """Sitemap minimal des pages publiques (peu de pages, pas besoin du
    framework django.contrib.sitemaps)."""

    def get(self, request):
        from apps.core.sector_content import SECTORS

        base = f"{request.scheme}://{request.get_host()}"
        pages = [
            ("", "1.0"),
            ("faq/", "0.6"),
            ("confidentialite/", "0.3"),
            ("conditions-utilisation/", "0.3"),
            ("accounts/login/", "0.5"),
        ]
        pages += [(f"secteurs/{slug}/", "0.7") for slug in SECTORS]
        urls = "\n".join(
            f"  <url><loc>{base}/{path}</loc><priority>{priority}</priority></url>"
            for path, priority in pages
        )
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n"
            "</urlset>\n"
        )
        return HttpResponse(xml, content_type="application/xml")


class HomeView(TemplateView):
    """Page d'accueil publique (site vitrine). Un utilisateur déjà connecté est
    renvoyé directement à son tableau de bord plutôt que de revoir la vitrine."""

    template_name = "core/home.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:dashboard")
        return super().get(request, *args, **kwargs)


class SectorLandingView(TemplateView):
    """Page publique par secteur d'activité (référencement) — contenu défini
    dans apps.core.sector_content.SECTORS, indexé par le slug d'URL."""

    template_name = "core/sector.html"

    def get_context_data(self, **kwargs):
        from apps.core.sector_content import SECTORS

        sector = SECTORS.get(kwargs["slug"])
        if sector is None:
            raise Http404
        return super().get_context_data(sector=sector, all_sectors=SECTORS, **kwargs)


class PrivacyView(TemplateView):
    template_name = "core/privacy.html"


class TermsView(TemplateView):
    template_name = "core/terms.html"


class FaqView(TemplateView):
    template_name = "core/faq.html"


class DashboardPlaceholderView(LoginRequiredMixin, TemplateView):
    """Point d'atterrissage post-login. Le Super Admin n'appartenant à aucun
    tenant (CDC §2.3.3), il est redirigé vers sa propre console — évite de
    dupliquer la logique de redirection dans chaque vue qui pointe vers
    "core:dashboard" (login, changement de mot de passe, page d'accueil...).
    Admin et Employé/Manager reçoivent chacun un vrai tableau de bord
    (CDC §16.2/§16.4) plutôt qu'une page générique."""

    def get(self, request, *args, **kwargs):
        if request.user.role == request.user.Role.SUPER_ADMIN:
            return redirect("superadmin:dashboard")
        return super().get(request, *args, **kwargs)

    MANAGER_ROLES = ("MANAGER",)

    def get_template_names(self):
        if self.request.user.role == self.request.user.Role.ADMIN:
            return ["core/admin_dashboard.html"]
        if self.request.user.role in self.MANAGER_ROLES:
            return ["core/manager_dashboard.html"]
        return ["core/employee_dashboard.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.role == user.Role.ADMIN:
            context.update(self._admin_context(user.tenant))
        elif user.role in self.MANAGER_ROLES:
            # CDC §16.3 : un Manager reste aussi un employé (il pointe lui-même) —
            # son tableau de bord combine sa vue personnelle et celle de son équipe.
            context.update(self._employee_context(user))
            context.update(self._manager_context(user))
        else:
            context.update(self._employee_context(user))
        return context

    def _manager_context(self, user):
        today = timezone.localdate()

        # CDC §3.3 : un Manager est strictement limité à ses rapports directs.
        team_qs = Employee.objects.all_tenants().filter(
            tenant=user.tenant, status=Employee.Status.ACTIVE, manager=user,
        ).select_related("user", "department", "primary_agency").order_by("user__first_name")
        team_ids = list(team_qs.values_list("id", flat=True))
        total_team = len(team_ids)

        today_arrivals = {
            a.employee_id: a
            for a in Attendance.objects.all_tenants().filter(
                employee_id__in=team_ids, clock_date=today, clock_type=Attendance.ClockType.ARRIVAL
            )
        }
        late_today = sum(1 for a in today_arrivals.values() if a.status == Attendance.Status.LATE)
        on_leave_team_today = self._on_leave_count(user.tenant, today, employee_ids=team_ids) if total_team else 0
        # Même base de calcul que _presence_rate (date d'entrée / fin de
        # contrat) pour que "absents" et "taux de présence" restent cohérents
        # entre eux — sans ça, un employé pas encore réellement entré en poste
        # ou dont le contrat est déjà terminé pouvait être compté dans l'un et
        # pas dans l'autre.
        expected_team_today = self._expected_headcount(user.tenant, today, employee_ids=team_ids)
        team_on_leave_today, team_absent_today = (
            self._who_is_out_today(user.tenant, employee_ids=team_ids) if total_team else ([], [])
        )

        trend_labels, trend_values = [], []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            trend_labels.append(d.strftime("%d/%m"))
            trend_values.append(
                self._presence_rate(user.tenant, d, employee_ids=team_ids) if total_team else 0.0
            )

        pending_leaves_qs = Leave.objects.all_tenants().filter(
            tenant=user.tenant, status=Leave.Status.PENDING, employee__manager=user,
        )
        pending_absences_qs = Absence.objects.all_tenants().filter(
            tenant=user.tenant, status=Absence.Status.PENDING_REVIEW, employee__manager=user,
        )

        team_rows = []
        for employee in team_qs:
            arrival = today_arrivals.get(employee.id)
            team_rows.append({
                "employee": employee,
                "arrival": arrival,
                "status": arrival.status if arrival else None,
            })

        return {
            "team_rows": team_rows,
            "total_team": total_team,
            "present_team_today": len(today_arrivals),
            "on_leave_team_today": on_leave_team_today,
            "absent_team_today": max(expected_team_today - on_leave_team_today - len(today_arrivals), 0),
            "employees_on_leave_today": team_on_leave_today,
            "employees_absent_today": team_absent_today,
            "late_team_today": late_today,
            "team_trend_labels": trend_labels,
            "team_trend_values": trend_values,
            "team_pending_leaves": pending_leaves_qs.count(),
            "team_pending_absences": pending_absences_qs.count(),
        }

    @staticmethod
    def _on_leave_count(tenant, date, employee_ids=None):
        """Employés en congé approuvé couvrant `date` — ni présents, ni
        absents à proprement parler : ils ne sont pas attendus au travail ce
        jour-là, donc exclus du dénominateur du taux de présence (sans quoi
        chaque congé approuvé fait mécaniquement baisser le taux et gonfle le
        nombre d'« absents », alors que ce n'est pas une absence).
        `employee_ids` restreint le décompte à une équipe (vue Manager)."""
        qs = Leave.objects.all_tenants().filter(
            tenant=tenant, status=Leave.Status.APPROVED, start_date__lte=date, end_date__gte=date
        )
        if employee_ids is not None:
            qs = qs.filter(employee_id__in=employee_ids)
        return qs.values("employee_id").distinct().count()

    @staticmethod
    def _expected_employees_qs(tenant, date, employee_ids=None):
        """Employés attendus à `date` — le statut actuel (Actif/Suspendu/
        Archivé...) n'est pas historisé (pas de date de changement de statut
        en base), donc pour une date passée on ne peut se fier qu'à la date
        d'entrée et la date de fin de contrat : un employé pas encore
        embauché ou dont le contrat était déjà terminé à `date` est exclu. Le
        statut courant n'est appliqué que pour la date du jour, seul instant
        où il reflète vraiment la réalité — sans quoi le taux d'un jour passé
        (ex. tendance sur 30 jours) était calculé avec l'effectif *actuel* au
        lieu de l'effectif réel de ce jour-là (faussé pour toute organisation
        en croissance ou en décroissance)."""
        qs = Employee.objects.all_tenants().filter(tenant=tenant, hire_date__lte=date).filter(
            Q(contract_end_date__isnull=True) | Q(contract_end_date__gte=date)
        )
        if date >= timezone.localdate():
            qs = qs.filter(status=Employee.Status.ACTIVE)
        if employee_ids is not None:
            qs = qs.filter(id__in=employee_ids)
        return qs

    @classmethod
    def _expected_headcount(cls, tenant, date, employee_ids=None):
        """Utilisé comme dénominateur du taux de présence — cf.
        `_expected_employees_qs` pour la définition de "attendu"."""
        return cls._expected_employees_qs(tenant, date, employee_ids=employee_ids).count()

    @classmethod
    def _who_is_out_today(cls, tenant, employee_ids=None):
        """Widget « qui est en congé / absent aujourd'hui » — mêmes règles
        d'effectif attendu que `_expected_headcount`/`_presence_rate`, pour
        que les noms listés ici correspondent exactement aux compteurs
        affichés à côté (ex. « absent_today »). Renvoie (en_congé, absents),
        deux listes d'Employee — un absent est un employé attendu, pas en
        congé approuvé, sans pointage d'arrivée aujourd'hui."""
        today = timezone.localdate()
        expected = cls._expected_employees_qs(tenant, today, employee_ids=employee_ids).select_related("user")

        on_leave_ids = set(
            Leave.objects.all_tenants()
            .filter(tenant=tenant, status=Leave.Status.APPROVED, start_date__lte=today, end_date__gte=today)
            .values_list("employee_id", flat=True)
        )
        present_ids = set(
            Attendance.objects.all_tenants()
            .filter(tenant=tenant, clock_date=today, clock_type=Attendance.ClockType.ARRIVAL)
            .values_list("employee_id", flat=True)
        )

        on_leave, absent = [], []
        for employee in expected.order_by("user__first_name", "user__last_name"):
            if employee.id in on_leave_ids:
                on_leave.append(employee)
            elif employee.id not in present_ids:
                absent.append(employee)
        return on_leave, absent

    @classmethod
    def _presence_rate(cls, tenant, date, employee_ids=None):
        """`employee_ids` restreint le calcul à une équipe (vue Manager) — sans
        ça, le nombre de présents portait sur tout le tenant tandis que le
        dénominateur ne portait que sur l'équipe, ce qui pouvait afficher un
        taux de présence d'équipe supérieur à 100 %."""
        headcount = cls._expected_headcount(tenant, date, employee_ids=employee_ids)
        expected = max(headcount - cls._on_leave_count(tenant, date, employee_ids=employee_ids), 0)
        if expected == 0:
            return 0.0
        present_qs = Attendance.objects.all_tenants().filter(
            tenant=tenant, clock_date=date, clock_type=Attendance.ClockType.ARRIVAL
        )
        if employee_ids is not None:
            present_qs = present_qs.filter(employee_id__in=employee_ids)
        present = present_qs.values("employee_id").distinct().count()
        return round(present / expected * 100, 1)

    @staticmethod
    def _onboarding_steps(tenant):
        """Check-list affichée à un Admin tant que l'organisation n'a pas les
        trois briques de base : sans agence, aucun pointage n'est possible ;
        sans horaire, un pointage est enregistré "hors horaire" ; sans
        employé, il n'y a personne à faire pointer. Masquée automatiquement
        dès que les trois sont là — pas besoin d'un drapeau "terminé" en base,
        seul un "masquer" explicite (onboarding_dismissed) est persisté."""
        return [
            {
                "label": "Créer une agence",
                "detail": "Le site où vos employés pointent, avec sa zone GPS autorisée.",
                "done": Agency.objects.all_tenants().filter(tenant=tenant).exists(),
                "url_name": "agencies:create",
            },
            {
                "label": "Configurer un horaire",
                "detail": "Les plages de travail à affecter à vos employés.",
                "done": Schedule.objects.all_tenants().filter(tenant=tenant).exists(),
                "url_name": "schedules:create",
            },
            {
                "label": "Ajouter un employé",
                "detail": "Crée son compte et lui envoie ses accès par e-mail.",
                "done": Employee.objects.all_tenants().filter(tenant=tenant).exists(),
                "url_name": "employees:create",
            },
        ]

    @classmethod
    def _onboarding_context(cls, tenant):
        steps = cls._onboarding_steps(tenant)
        done_count = sum(1 for s in steps if s["done"])
        complete = done_count == len(steps)
        return {
            "onboarding_steps": steps,
            "onboarding_done_count": done_count,
            # Auto-masquée dès que tout est fait ; sinon respecte un "masquer"
            # explicite (persisté par org, cf. OnboardingDismissView — pas par
            # navigateur, pour qu'un second Admin de la même organisation ne
            # revoie pas la check-list qu'un collègue a déjà fermée).
            "show_onboarding": not complete and not get_org_setting(tenant, "onboarding_dismissed"),
        }

    def _admin_context(self, tenant):
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)
        month_start = today.replace(day=1)

        total_employees = Employee.objects.all_tenants().filter(tenant=tenant, status=Employee.Status.ACTIVE).count()

        present_today = (
            Attendance.objects.all_tenants()
            .filter(tenant=tenant, clock_date=today, clock_type=Attendance.ClockType.ARRIVAL)
            .values("employee_id")
            .distinct()
            .count()
        )
        late_today = Attendance.objects.all_tenants().filter(
            tenant=tenant, clock_date=today, clock_type=Attendance.ClockType.ARRIVAL, status=Attendance.Status.LATE
        ).count()
        on_leave_today = self._on_leave_count(tenant, today)
        expected_today = self._expected_headcount(tenant, today)
        employees_on_leave_today, employees_absent_today = self._who_is_out_today(tenant)

        trend_labels, trend_values = [], []
        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            trend_labels.append(d.strftime("%d/%m"))
            trend_values.append(self._presence_rate(tenant, d))

        reasons_qs = (
            Absence.objects.all_tenants()
            .filter(tenant=tenant, date__gte=month_start)
            .values("reason__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        reason_labels = [r["reason__name"] or "Non précisé" for r in reasons_qs]
        reason_values = [r["count"] for r in reasons_qs]

        late_ranking = (
            Attendance.objects.all_tenants()
            .filter(
                tenant=tenant, clock_type=Attendance.ClockType.ARRIVAL, status=Attendance.Status.LATE,
                clock_date__gte=month_start,
            )
            .values("employee__user__first_name", "employee__user__last_name")
            .annotate(total_late=Sum("late_minutes"), occurrences=Count("id"))
            .order_by("-total_late")[:10]
        )

        return {
            "total_employees": total_employees,
            "present_today": present_today,
            "on_leave_today": on_leave_today,
            "absent_today": max(expected_today - on_leave_today - present_today, 0),
            "late_today": late_today,
            "rate_today": self._presence_rate(tenant, today),
            "rate_yesterday": self._presence_rate(tenant, yesterday),
            "employees_on_leave_today": employees_on_leave_today,
            "employees_absent_today": employees_absent_today,
            **self._onboarding_context(tenant),
            "pending_leaves": Leave.objects.all_tenants().filter(tenant=tenant, status=Leave.Status.PENDING).count(),
            "pending_absences": Absence.objects.all_tenants().filter(
                tenant=tenant, status=Absence.Status.PENDING_REVIEW
            ).count(),
            "trend_labels": trend_labels,
            "trend_values": trend_values,
            "reason_labels": reason_labels,
            "reason_values": reason_values,
            "late_ranking": late_ranking,
            "recent_attendances": Attendance.objects.all_tenants().filter(tenant=tenant).select_related(
                "employee__user", "agency"
            ).order_by("-server_time")[:10],
        }

    def _employee_context(self, user):
        employee = get_active_employee(user)
        context = {"employee": employee}
        if employee is None:
            return context

        today = timezone.localdate()
        month_start = today.replace(day=1)

        next_clock_type, clock_date, _next_clock_slot = attendance_services.get_clock_status(employee)
        if next_clock_type is None:
            today_status = "done"
        elif next_clock_type == Attendance.ClockType.DEPARTURE:
            today_status = "present"
        else:
            today_status = "not_clocked_in"

        month_arrivals = Attendance.objects.all_tenants().filter(
            employee=employee, clock_date__gte=month_start, clock_type=Attendance.ClockType.ARRIVAL
        )

        context.update({
            "today_status": today_status,
            "today_attendances": Attendance.objects.all_tenants().filter(
                employee=employee, clock_date=clock_date
            ).order_by("server_time"),
            "days_present_month": month_arrivals.values("clock_date").distinct().count(),
            "days_late_month": month_arrivals.filter(status=Attendance.Status.LATE).count(),
            "recent_attendances": Attendance.objects.all_tenants().filter(employee=employee).select_related(
                "agency"
            ).order_by("-server_time")[:10],
            "my_leaves_pending": Leave.objects.all_tenants().filter(
                employee=employee, status=Leave.Status.PENDING
            ).count(),
            "my_absences_pending": Absence.objects.all_tenants().filter(
                employee=employee, status=Absence.Status.PENDING_REVIEW
            ).count(),
            # CDC §16.4 : « Annonces de l'organisation ».
            "active_announcements": announcement_services.active_announcements_for_employee(employee),
        })
        return context


# RM-UI-NAV-HUB (15/08/2026) : écrans plein qui remplacent les anciens menus
# déroulants de la barre d'onglets mobile. Taper "Organisation"/"Validations"/
# "Mon espace" doit faire quitter complètement l'écran courant (comme un
# onglet Facebook/Instagram), pas ouvrir une fenêtre flottante par-dessus le
# tableau de bord. Aucune donnée propre : ces vues listent les mêmes liens
# que les groupes de la barre du haut (desktop, laissée en menu déroulant —
# assez de place pour ça) ; les compteurs de badge viennent des context
# processors déjà globaux (apps.core.context_processors.sidebar_counts).
class OrganisationMenuView(RoleRequiredMixin, TemplateView):
    allowed_roles = ("ADMIN",)
    template_name = "core/menu_organisation.html"


class ValidationsMenuView(RoleRequiredMixin, TemplateView):
    allowed_roles = ("ADMIN", "MANAGER")
    template_name = "core/menu_validations.html"


class WorkspaceMenuView(RoleRequiredMixin, TemplateView):
    allowed_roles = ("MANAGER", "EMPLOYEE")
    template_name = "core/menu_workspace.html"


class TenantQuerysetMixin:
    """Restreint la queryset/l'objet accessible à l'organisation de
    l'utilisateur connecté — empêche l'édition d'un objet d'une autre
    organisation par simple manipulation d'URL."""

    model = None

    def get_queryset(self):
        return self.model.objects.all_tenants().filter(tenant=self.request.tenant)


class TenantFormMixin(TenantQuerysetMixin):
    """Pour Create/UpdateView sur un TenantModel. Injecte le tenant sur
    l'instance AVANT la validation du formulaire (pas après) : le clean()
    métier des modèles (vérifications cross-tenant) a besoin de tenant_id dès
    la validation, pas seulement à la sauvegarde. Convertit aussi une
    IntegrityError de contrainte d'unicité en erreur de formulaire lisible
    plutôt qu'en page 500 (la validate_unique() automatique de Django ignore
    les contraintes portant sur un champ exclu du formulaire, comme `tenant`)."""

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if kwargs.get("instance") is None:
            kwargs["instance"] = self.model(tenant=self.request.tenant)
        kwargs["tenant"] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        try:
            with transaction.atomic():
                return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, "Cette valeur existe déjà pour votre organisation.")
            return self.form_invalid(form)


class ToggleActiveView(RoleRequiredMixin, TenantQuerysetMixin, View):
    """Bascule un champ booléen (`is_active` par défaut) en une requête POST —
    évite de dupliquer une vue dédiée pour chaque module qui n'a besoin que
    d'activer/désactiver une ligne depuis sa liste (CDC : agences,
    départements, postes, horaires « créer, modifier, activer et désactiver »,
    §7.3/§10/§3.2.2). Sous-classer avec `model`, `allowed_roles` et
    `success_url` (+ `active_field` si différent de `is_active`)."""

    active_field = "is_active"
    success_url = None

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        setattr(obj, self.active_field, not getattr(obj, self.active_field))
        obj.save(update_fields=[self.active_field])
        return redirect(self.success_url)
