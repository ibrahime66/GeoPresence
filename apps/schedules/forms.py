from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from apps.core.forms import BootstrapModelFormMixin

from .models import Schedule, ScheduleSlot, Weekday


def _time_to_minutes(t):
    return t.hour * 60 + t.minute


def _slot_segments(start_time, end_time):
    """Découpe un créneau en une ou deux plages [début, fin) en minutes
    depuis minuit — un créneau de nuit (ex. 22h→06h, RM-HOR-004) chevauche
    minuit et doit être comparé en deux morceaux (22h-24h et 0h-6h) pour que
    la détection de chevauchement reste correcte dans ce cas."""
    start, end = _time_to_minutes(start_time), _time_to_minutes(end_time)
    if end <= start:
        return [(start, 24 * 60), (0, end)]
    return [(start, end)]


def _segments_overlap(a, b):
    return a[0] < b[1] and b[0] < a[1]


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
            "is_cancelled",
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

    def clean(self):
        """Deux créneaux du même jour qui se chevauchent créent une
        ambiguïté au pointage : `resolve_slot` (apps/attendance/services.py)
        rattache automatiquement un pointage au premier créneau du jour (par
        heure de début) dont l'arrivée manque encore, sans jamais demander à
        l'employé pour quel créneau il pointe — un chevauchement peut donc
        rattacher silencieusement un pointage au mauvais créneau (mauvais
        calcul de retard/avance, fausse absence détectée sur l'autre
        créneau)."""
        super().clean()
        if any(self.errors):
            return

        by_weekday = {}
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get("DELETE"):
                continue
            if form.cleaned_data.get("is_cancelled"):
                continue
            start_time, end_time = form.cleaned_data.get("start_time"), form.cleaned_data.get("end_time")
            weekday = form.cleaned_data.get("weekday")
            if start_time is None or end_time is None or weekday is None:
                continue
            by_weekday.setdefault(weekday, []).append((form, _slot_segments(start_time, end_time)))

        for weekday, entries in by_weekday.items():
            for i in range(len(entries)):
                form_a, segments_a = entries[i]
                for j in range(i + 1, len(entries)):
                    form_b, segments_b = entries[j]
                    if any(_segments_overlap(a, b) for a in segments_a for b in segments_b):
                        weekday_label = dict(Weekday.choices).get(weekday, weekday)
                        raise forms.ValidationError(
                            f"Deux créneaux du {weekday_label} se chevauchent "
                            f"({form_a.cleaned_data['start_time']:%H:%M}–{form_a.cleaned_data['end_time']:%H:%M} "
                            f"et {form_b.cleaned_data['start_time']:%H:%M}–{form_b.cleaned_data['end_time']:%H:%M})."
                        )


ScheduleSlotFormSet = inlineformset_factory(
    Schedule, ScheduleSlot, form=ScheduleSlotForm, formset=TenantInlineFormSet, extra=1, can_delete=True,
)
