from django import forms
from django.core.files.uploadedfile import UploadedFile

from apps.accounts.models import User
from apps.core.forms import BootstrapModelFormMixin
from apps.schedules.models import Schedule

from .models import Agency


class AgencyForm(BootstrapModelFormMixin, forms.ModelForm):
    MAX_PHOTO_SIZE_BYTES = 5 * 1024 * 1024

    class Meta:
        model = Agency
        fields = [
            "name", "code", "agency_type", "address", "city", "country", "phone", "email",
            "responsible", "latitude", "longitude", "radius_meters", "default_schedule",
            "is_active", "allow_offline_clocking", "photo", "notes",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["responsible"].queryset = User.objects.filter(tenant=tenant)
        self.fields["responsible"].required = False
        self.fields["default_schedule"].queryset = Schedule.objects.all_tenants().filter(tenant=tenant, is_active=True)
        if not self.instance.pk:
            # CDC §6.4.2 : rayon GPS par défaut configurable par organisation —
            # pré-rempli uniquement à la création (une agence existante garde sa
            # propre valeur, jamais réécrasée par un changement de paramètre global).
            from apps.tenants.org_settings import get_org_setting

            self.fields["radius_meters"].initial = get_org_setting(tenant, "gps_radius_default_meters")

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if isinstance(photo, UploadedFile) and photo.size > self.MAX_PHOTO_SIZE_BYTES:
            raise forms.ValidationError("L'image dépasse la taille maximale autorisée (5 Mo).")
        return photo
