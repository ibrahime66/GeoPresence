from django import forms
from django.core.exceptions import ValidationError

from .models import LeaveType

OTHER_LEAVE_TYPE_NAME = "Autre"
# Types proposés par défaut à chaque organisation qui n'en a encore configuré
# aucun (CDC §12.3.1 : liste configurable, pas figée — mais une liste vide
# rend le formulaire de demande de congé inutilisable pour l'employé).
DEFAULT_LEAVE_TYPES = [
    {"name": "Congé annuel payé", "deducts_from_balance": True},
    {"name": "Congé sans solde", "deducts_from_balance": False},
    {"name": "Congé maladie", "deducts_from_balance": False},
    {"name": OTHER_LEAVE_TYPE_NAME, "deducts_from_balance": False},
]


class LeaveRequestForm(forms.Form):
    leave_type = forms.ModelChoiceField(queryset=LeaveType.objects.none(), label="Type de congé")
    start_date = forms.DateField(label="Date de début", widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(label="Date de fin", widget=forms.DateInput(attrs={"type": "date"}))
    comment = forms.CharField(label="Commentaire", required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-control".strip()
        if tenant is not None and not LeaveType.objects.all_tenants().filter(tenant=tenant).exists():
            for defaults in DEFAULT_LEAVE_TYPES:
                LeaveType.objects.all_tenants().create(tenant=tenant, **defaults)
        self.fields["leave_type"].queryset = LeaveType.objects.all_tenants().filter(tenant=tenant, is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        leave_type = cleaned_data.get("leave_type")
        if leave_type and leave_type.name == OTHER_LEAVE_TYPE_NAME and not cleaned_data.get("comment"):
            raise ValidationError({"comment": "Précisez le motif de ce congé."})
        return cleaned_data
