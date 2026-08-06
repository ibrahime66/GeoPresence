from datetime import timedelta

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import IntegrityError, connection, transaction
from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from apps.absences.models import Absence
from apps.accounts.mixins import RoleRequiredMixin
from apps.announcements import services as announcement_services
from apps.attendance import services as attendance_services
from apps.attendance.models import Attendance
from apps.employees.models import Employee
from apps.employees.services import get_active_employee
from apps.leaves.models import Leave

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


class HomeView(TemplateView):
    """Page d'accueil publique (site vitrine). Un utilisateur déjà connecté est
    renvoyé directement à son tableau de bord plutôt que de revoir la vitrine."""

    template_name = "core/home.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:dashboard")
        return super().get(request, *args, **kwargs)


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

        trend_labels, trend_values = [], []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            trend_labels.append(d.strftime("%d/%m"))
            trend_values.append(self._presence_rate(user.tenant, d, total_team) if total_team else 0.0)

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
            "absent_team_today": max(total_team - len(today_arrivals), 0),
            "late_team_today": late_today,
            "team_trend_labels": trend_labels,
            "team_trend_values": trend_values,
            "team_pending_leaves": pending_leaves_qs.count(),
            "team_pending_absences": pending_absences_qs.count(),
        }

    @staticmethod
    def _presence_rate(tenant, date, total_employees):
        if total_employees == 0:
            return 0.0
        present = (
            Attendance.objects.all_tenants()
            .filter(tenant=tenant, clock_date=date, clock_type=Attendance.ClockType.ARRIVAL)
            .values("employee_id")
            .distinct()
            .count()
        )
        return round(present / total_employees * 100, 1)

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

        trend_labels, trend_values = [], []
        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            trend_labels.append(d.strftime("%d/%m"))
            trend_values.append(self._presence_rate(tenant, d, total_employees))

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
            "absent_today": max(total_employees - present_today, 0),
            "late_today": late_today,
            "rate_today": self._presence_rate(tenant, today, total_employees),
            "rate_yesterday": self._presence_rate(tenant, yesterday, total_employees),
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
