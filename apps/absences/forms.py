from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import AbsenceReason

OTHER_REASON_NAME = "Autre"


class JustificationForm(forms.Form):
    date = forms.DateField(label="Date", widget=forms.DateInput(attrs={"type": "date"}))
    reason = forms.ModelChoiceField(queryset=AbsenceReason.objects.none(), required=False, label="Motif")
    custom_reason = forms.CharField(
        label="Précisez votre motif", required=False, widget=forms.TextInput(attrs={"maxlength": 255})
    )
    comment = forms.CharField(label="Commentaire", required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-control".strip()
        if tenant is not None:
            AbsenceReason.objects.all_tenants().get_or_create(tenant=tenant, name=OTHER_REASON_NAME)
        self.fields["reason"].queryset = AbsenceReason.objects.all_tenants().filter(tenant=tenant, is_active=True)

    def clean_date(self):
        date = self.cleaned_data["date"]
        if date > timezone.localdate():
            # Une absence se justifie après coup (un fait déjà survenu) —
            # accepter une date future n'a pas de sens dans ce flux et
            # pourrait faire approuver une "absence" pour un jour qui n'a pas
            # encore eu lieu. Une absence prévue à l'avance relève des congés
            # (apps.leaves), pas de ce module.
            raise ValidationError("Impossible de justifier une absence à une date future.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        reason = cleaned_data.get("reason")
        if reason and reason.name == OTHER_REASON_NAME and not cleaned_data.get("custom_reason"):
            raise ValidationError({"custom_reason": "Précisez votre motif."})
        return cleaned_data
