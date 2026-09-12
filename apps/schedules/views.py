from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.core.views import DEFAULT_PAGE_SIZE, TenantQuerysetMixin, ToggleActiveView
from apps.tenants.org_settings import get_org_setting

from . import services
from .forms import ScheduleForm, ScheduleSlotFormSet
from .models import Schedule

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
