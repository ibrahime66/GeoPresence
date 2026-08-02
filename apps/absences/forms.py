from django import forms

from .models import AbsenceReason


class JustificationForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    reason = forms.ModelChoiceField(queryset=AbsenceReason.objects.none(), required=False, label="Motif")
    comment = forms.CharField(label="Commentaire", required=False, widget=forms.Textarea(attrs={"rows": 2}))
    file = forms.FileField(label="Justificatif (PDF, JPG, PNG — 5 Mo max)", required=False)

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-control".strip()
        self.fields["reason"].queryset = AbsenceReason.objects.all_tenants().filter(tenant=tenant, is_active=True)
