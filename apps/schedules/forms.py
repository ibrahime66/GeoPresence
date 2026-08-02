from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from apps.core.forms import BootstrapModelFormMixin

from .models import Schedule, ScheduleSlot


class ScheduleForm(BootstrapModelFormMixin, forms.ModelForm):
    class Meta:
        model = Schedule
        fields = [
            "name", "schedule_type", "is_active",
            "late_tolerance_minutes", "early_leave_tolerance_minutes", "overtime_threshold_minutes",
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)


class ScheduleSlotForm(BootstrapModelFormMixin, forms.ModelForm):
    class Meta:
        model = ScheduleSlot
        fields = [
            "weekday", "start_time", "end_time", "break_start_time", "break_end_time",
            "clock_in_window_before_minutes", "clock_in_window_after_minutes",
            "clock_out_window_before_minutes", "clock_out_window_after_minutes",
            "subject", "room", "group_label", "is_cancelled",
        ]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "break_start_time": forms.TimeInput(attrs={"type": "time"}),
            "break_end_time": forms.TimeInput(attrs={"type": "time"}),
        }


class TenantInlineFormSet(BaseInlineFormSet):
    """Injecte le tenant sur chaque instance de créneau AVANT la validation —
    même raison que TenantFormMixin côté formulaire simple : le clean() du
    modèle compare des tenant_id qui doivent déjà être renseignés."""

    def __init__(self, *args, tenant=None, **kwargs):
        self.tenant = tenant
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        form = super()._construct_form(i, **kwargs)
        if form.instance.tenant_id is None:
            form.instance.tenant = self.tenant
        return form


ScheduleSlotFormSet = inlineformset_factory(
    Schedule, ScheduleSlot, form=ScheduleSlotForm, formset=TenantInlineFormSet, extra=1, can_delete=True,
)
