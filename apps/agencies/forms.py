from django import forms

from apps.accounts.models import User
from apps.core.forms import BootstrapModelFormMixin
from apps.schedules.models import Schedule

from .models import Agency


class AgencyForm(BootstrapModelFormMixin, forms.ModelForm):
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
