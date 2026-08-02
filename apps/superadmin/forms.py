import zoneinfo

from django import forms
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.core.forms import BootstrapModelFormMixin
from apps.tenants.models import Organization

TIMEZONE_CHOICES = [(tz, tz) for tz in sorted(zoneinfo.available_timezones()) if "/" in tz]

ORG_FIELDS = [
    "legal_name", "display_name", "slug", "org_type", "country", "city", "address",
    "phone", "email", "website", "timezone", "language", "date_format", "time_format",
    "primary_color", "secondary_color", "logo",
]

ORG_WIDGETS = {
    "address": forms.Textarea(attrs={"rows": 2}),
    "primary_color": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),
    "secondary_color": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),
}


class OrganizationCreateForm(BootstrapModelFormMixin, forms.ModelForm):
    """CDC §6.2 : crée l'organisation ET son premier compte Administrateur
    (mot de passe temporaire, changement forcé — même mécanisme que la
    création d'employé)."""

    timezone = forms.ChoiceField(choices=TIMEZONE_CHOICES, label="Fuseau horaire", initial="UTC")
    admin_first_name = forms.CharField(label="Prénom de l'administrateur", max_length=150)
    admin_last_name = forms.CharField(label="Nom de l'administrateur", max_length=150)
    admin_email = forms.EmailField(label="E-mail de l'administrateur")

    class Meta:
        model = Organization
        fields = ORG_FIELDS
        widgets = ORG_WIDGETS

    def clean_admin_email(self):
        email = self.cleaned_data["admin_email"].strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Un compte existe déjà avec cet e-mail.")
        return email


class OrganizationUpdateForm(BootstrapModelFormMixin, forms.ModelForm):
    timezone = forms.ChoiceField(choices=TIMEZONE_CHOICES, label="Fuseau horaire")

    class Meta:
        model = Organization
        fields = ORG_FIELDS + ["status"]
        widgets = ORG_WIDGETS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # RM-ORG-001 : slug immuable après création. `disabled` (pas juste
        # `readonly`) car Django ignore alors toute valeur POSTée pour ce champ,
        # même une tentative de contournement via une requête forgée.
        self.fields["slug"].disabled = True
