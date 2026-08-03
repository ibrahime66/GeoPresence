from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.core.views import DEFAULT_PAGE_SIZE, TenantQuerysetMixin, ToggleActiveView

from .forms import ScheduleForm, ScheduleSlotFormSet
from .models import Schedule

ADMIN_ONLY = (User.Role.ADMIN,)


class ScheduleListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ADMIN_ONLY
    model = Schedule
    template_name = "schedules/schedule_list.html"
    context_object_name = "schedules"
    paginate_by = DEFAULT_PAGE_SIZE


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

    def get(self, request, pk=None):
        schedule = self.get_object(request, pk)
        form = ScheduleForm(instance=schedule, tenant=request.tenant)
        formset = ScheduleSlotFormSet(instance=schedule, tenant=request.tenant)
        return render(request, self.template_name, {"form": form, "formset": formset, "object": schedule if pk else None})

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
        return render(request, self.template_name, {"form": form, "formset": formset, "object": schedule if pk else None})
