from datetime import date as date_cls

from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, TemplateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.audit import services as audit
from apps.audit.models import AuditLog
from apps.core import exports
from apps.core.views import DEFAULT_PAGE_SIZE, TenantQuerysetMixin, ToggleActiveView
from apps.tenants.org_settings import get_org_setting

from . import services
from .forms import ScheduleForm, ScheduleSlotFormSet
from .models import Schedule

# Regroupements proposés sur la page « Présence enseignants » — clé de tri
# lisible dans l'URL (?groupe=) -> (libellé de l'onglet, fonction qui renvoie
# le libellé du groupe pour une entrée).
PRESENCE_GROUP_MODES = {
    "salle": ("Salle", lambda e: e["slot"].room or "Sans salle"),
    "classe": ("Classe", lambda e: e["slot"].student_group or "Sans classe"),
    "enseignant": ("Enseignant", lambda e: e["employee"].user.full_name or e["employee"].user.email),
}

ADMIN_ONLY = (User.Role.ADMIN,)


class ScheduleListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ADMIN_ONLY
    model = Schedule
    template_name = "schedules/schedule_list.html"
    context_object_name = "schedules"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["school_scheduling_enabled"] = get_org_setting(
            self.request.tenant, "school_scheduling_enabled"
        )
        return context


class ScheduleToggleActiveView(ToggleActiveView):
    allowed_roles = ADMIN_ONLY
    model = Schedule
    success_url = reverse_lazy("schedules:list")


class ScheduleFormView(RoleRequiredMixin, View):
    """Un horaire et ses créneaux se modifient ensemble sur une même page —
    pas un CreateView/UpdateView standard (formset imbriqué)."""

    allowed_roles = ADMIN_ONLY
    template_name = "schedules/schedule_form.html"

    def get_object(self, request, pk):
        if pk is None:
            return Schedule(tenant=request.tenant)
        return get_object_or_404(Schedule.objects.all_tenants().filter(tenant=request.tenant), pk=pk)

    def _context_extra(self, request):
        return {"school_scheduling_enabled": get_org_setting(request.tenant, "school_scheduling_enabled")}

    def get(self, request, pk=None):
        schedule = self.get_object(request, pk)
        form = ScheduleForm(instance=schedule, tenant=request.tenant)
        formset = ScheduleSlotFormSet(instance=schedule, tenant=request.tenant)
        context = {"form": form, "formset": formset, "object": schedule if pk else None}
        return render(request, self.template_name, {**context, **self._context_extra(request)})

    def post(self, request, pk=None):
        schedule = self.get_object(request, pk)
        form = ScheduleForm(request.POST, instance=schedule, tenant=request.tenant)
        formset = ScheduleSlotFormSet(request.POST, instance=schedule, tenant=request.tenant)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, "Horaire enregistré.")
            return redirect("schedules:list")
        context = {"form": form, "formset": formset, "object": schedule if pk else None}
        return render(request, self.template_name, {**context, **self._context_extra(request)})


class UnstaffedSlotsView(RoleRequiredMixin, TemplateView):
    """RM-ORG-SCHOOL : détail de l'alerte "cours sans professeur" du tableau
    de bord Admin (cf. apps.schedules.services.unstaffed_slots_today) —
    accessible seulement si le module école est actif, comme le reste de
    cette fonctionnalité."""

    allowed_roles = ADMIN_ONLY
    template_name = "schedules/unstaffed_slots.html"

    def get_context_data(self, **kwargs):
        from django.utils import timezone

        context = super().get_context_data(**kwargs)
        context["school_scheduling_enabled"] = get_org_setting(self.request.tenant, "school_scheduling_enabled")
        alerts = (
            services.unstaffed_slots_today(self.request.tenant) if context["school_scheduling_enabled"] else []
        )
        today = timezone.localdate()
        for alert in alerts:
            substitutes = services.available_substitutes(
                self.request.tenant, alert["slot"], today, exclude_employee_id=alert["employee"].id
            )
            alert["substitutes"] = substitutes[:5]
            alert["substitutes_more"] = max(0, len(substitutes) - 5)
        context["alerts"] = alerts
        return context


class RoomPlanningView(RoleRequiredMixin, TemplateView):
    """RM-ORG-SCHOOL : planning visuel de l'occupation des salles pour un jour
    de la semaine (cf. apps.schedules.services.room_day_planning). Comme le
    reste du module école, accessible seulement si school_scheduling_enabled."""

    allowed_roles = ADMIN_ONLY
    template_name = "schedules/room_planning.html"

    # Bornes de l'axe horaire quand aucun créneau n'existe encore ce jour-là —
    # journée scolaire classique, juste pour que la grille ne soit pas vide.
    DEFAULT_DAY_START_MINUTES = 8 * 60
    DEFAULT_DAY_END_MINUTES = 18 * 60

    def get_context_data(self, **kwargs):
        from django.utils import timezone

        from .models import Weekday

        context = super().get_context_data(**kwargs)
        enabled = get_org_setting(self.request.tenant, "school_scheduling_enabled")
        context["school_scheduling_enabled"] = enabled

        valid_weekdays = {choice.value for choice in Weekday}
        try:
            weekday = int(self.request.GET.get("jour", ""))
        except (TypeError, ValueError):
            weekday = None
        if weekday not in valid_weekdays:
            # Le week-end, on ouvre sur lundi plutôt que sur une grille vide.
            today = timezone.localdate().weekday()
            weekday = today if today <= Weekday.FRIDAY else Weekday.MONDAY

        rooms, unroomed_count = (
            services.room_day_planning(self.request.tenant, weekday) if enabled else ([], 0)
        )

        # Axe horaire commun à toutes les salles : de la 1re à la dernière
        # minute occupée du jour, arrondi à l'heure pleine pour des repères
        # lisibles.
        starts = [e["slot"].start_time for r in rooms for e in r["entries"]]
        ends = [e["slot"].end_time for r in rooms for e in r["entries"]]
        if starts and ends:
            day_start = (min(t.hour * 60 + t.minute for t in starts)) // 60 * 60
            day_end = -(-max(t.hour * 60 + t.minute for t in ends) // 60) * 60
        else:
            day_start = self.DEFAULT_DAY_START_MINUTES
            day_end = self.DEFAULT_DAY_END_MINUTES
        span = max(day_end - day_start, 60)

        for room in rooms:
            for entry in room["entries"]:
                slot = entry["slot"]
                s = slot.start_time.hour * 60 + slot.start_time.minute
                e = slot.end_time.hour * 60 + slot.end_time.minute
                entry["offset_pct"] = round((s - day_start) / span * 100, 3)
                entry["width_pct"] = round(max(e - s, 15) / span * 100, 3)

        context["weekday"] = weekday
        context["weekday_label"] = Weekday(weekday).label
        context["weekdays"] = Weekday.choices
        context["rooms"] = rooms
        context["unroomed_count"] = unroomed_count
        context["hour_marks"] = [
            {"hour": h, "left_pct": round((h * 60 - day_start) / span * 100, 3)}
            for h in range(day_start // 60, day_end // 60 + 1)
        ]
        return context


def _presence_date(request):
    """Date consultée sur la page « Présence enseignants » — ?date=YYYY-MM-DD,
    défaut aujourd'hui. Une date invalide retombe silencieusement sur
    aujourd'hui plutôt que de lever une 400 (champ saisi à la main dans l'URL)."""
    raw = request.GET.get("date", "")
    try:
        return date_cls.fromisoformat(raw)
    except (TypeError, ValueError):
        return timezone.localdate()


class TeacherPresenceView(RoleRequiredMixin, TemplateView):
    """RM-ORG-SCHOOL : pour une date, quels enseignants ont pointé et pour
    quel cours / salle / classe (cf. apps.schedules.services.teacher_presence).
    Réservé aux organisations avec school_scheduling_enabled, comme le reste
    du module."""

    allowed_roles = ADMIN_ONLY
    template_name = "schedules/teacher_presence.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        enabled = get_org_setting(tenant, "school_scheduling_enabled")
        context["school_scheduling_enabled"] = enabled

        on_date = _presence_date(self.request)
        group_mode = self.request.GET.get("groupe", "salle")
        if group_mode not in PRESENCE_GROUP_MODES:
            group_mode = "salle"
        group_label_fn = PRESENCE_GROUP_MODES[group_mode][1]

        entries = services.teacher_presence(tenant, on_date) if enabled else []

        groups = {}
        for entry in entries:
            groups.setdefault(group_label_fn(entry), []).append(entry)

        context["on_date"] = on_date
        context["prev_date"] = on_date - timezone.timedelta(days=1)
        context["next_date"] = on_date + timezone.timedelta(days=1)
        context["is_today"] = on_date == timezone.localdate()
        context["group_mode"] = group_mode
        context["group_modes"] = [(key, label) for key, (label, _fn) in PRESENCE_GROUP_MODES.items()]
        context["groups"] = [
            {"label": label, "entries": groups[label]} for label in sorted(groups, key=str.casefold)
        ]
        context["total_slots"] = len(entries)
        context["clocked_count"] = sum(1 for e in entries if e["clocked"])
        context["missing_count"] = sum(1 for e in entries if not e["clocked"])
        context["in_progress_count"] = sum(1 for e in entries if e["in_progress"])
        context["query_string"] = self.request.GET.urlencode()
        return context


class TeacherPresenceExportView(RoleRequiredMixin, View):
    """Export CSV/Excel/PDF de la page « Présence enseignants » — même date
    que l'écran (?date=), sans regroupement (lignes à plat pour la paie /
    l'archivage d'une feuille de présence enseignants)."""

    allowed_roles = ADMIN_ONLY

    HEADERS = [
        "Date", "Début", "Fin", "Matière", "Classe", "Salle", "Enseignant",
        "Arrivée", "Statut arrivée", "Départ", "En classe",
    ]

    def get(self, request, fmt):
        if not get_org_setting(request.tenant, "school_scheduling_enabled"):
            raise Http404("Module horaires enseignants non activé.")
        on_date = _presence_date(request)
        entries = services.teacher_presence(request.tenant, on_date)

        rows = []
        for e in entries:
            slot, arrival, departure = e["slot"], e["arrival"], e["departure"]
            rows.append([
                on_date.isoformat(),
                slot.start_time.strftime("%H:%M"),
                slot.end_time.strftime("%H:%M"),
                slot.subject or "",
                slot.student_group or "",
                slot.room or "",
                e["employee"].user.full_name or e["employee"].user.email,
                timezone.localtime(arrival.server_time).strftime("%H:%M") if arrival else "",
                arrival.get_status_display() if arrival else "Non pointé",
                timezone.localtime(departure.server_time).strftime("%H:%M") if departure else "",
                "Oui" if e["in_progress"] else "",
            ])

        base = f"presence_enseignants_{request.tenant.slug}_{on_date.isoformat()}"
        if fmt == "csv":
            response = exports.export_csv(f"{base}.csv", self.HEADERS, rows)
        elif fmt == "xlsx":
            response = exports.export_xlsx(f"{base}.xlsx", self.HEADERS, rows, sheet_title="Présence enseignants")
        elif fmt == "pdf":
            response = exports.export_pdf(
                f"{base}.pdf", "Présence enseignants", self.HEADERS, rows,
                subtitle=f"{request.tenant.display_name} · {on_date:%d/%m/%Y}",
            )
        else:
            raise Http404("Format d'export inconnu.")

        audit.log_event(
            request, audit.EXPORT_DATA, AuditLog.Result.SUCCESS, user=request.user,
            description=f"Export présence enseignants ({fmt}, {len(rows)} lignes)",
        )
        return response
