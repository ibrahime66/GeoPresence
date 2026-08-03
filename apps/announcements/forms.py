from django import forms

from apps.agencies.models import Agency
from apps.core.forms import BootstrapModelFormMixin
from apps.departments.models import Department
from apps.employees.models import Employee

from .models import Announcement


class AnnouncementForm(BootstrapModelFormMixin, forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title", "content", "publish_at", "expire_at", "agencies", "departments", "employees"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 5}),
            "publish_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "expire_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "agencies": forms.SelectMultiple(attrs={"size": 6}),
            "departments": forms.SelectMultiple(attrs={"size": 6}),
            "employees": forms.SelectMultiple(attrs={"size": 6}),
        }
        labels = {
            "publish_at": "Date de publication",
            "expire_at": "Date d'expiration",
            "agencies": "Agences",
            "departments": "Départements",
            "employees": "Employés",
        }
        help_texts = {
            "agencies": "Laisser vide pour cibler toute l'organisation.",
            "employees": "Optionnel — ajouter des employés précis en plus des agences/départements ciblés.",
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["publish_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["expire_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["agencies"].queryset = Agency.objects.all_tenants().filter(tenant=tenant, is_active=True)
        self.fields["departments"].queryset = Department.objects.all_tenants().filter(tenant=tenant, is_active=True)
        self.fields["employees"].queryset = (
            Employee.objects.all_tenants().filter(tenant=tenant, status=Employee.Status.ACTIVE).select_related("user")
        )

        from apps.tenants.org_settings import get_org_setting

        if not get_org_setting(tenant, "departments_enabled"):
            del self.fields["departments"]
