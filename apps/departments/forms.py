from django import forms

from apps.core.forms import BootstrapModelFormMixin, apply_module_gating
from apps.schedules.models import Schedule

from .models import Department, Position


class DepartmentForm(BootstrapModelFormMixin, forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "code", "description", "default_schedule", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["default_schedule"].queryset = Schedule.objects.all_tenants().filter(tenant=tenant, is_active=True)
        self.fields["default_schedule"].required = False


class PositionForm(BootstrapModelFormMixin, forms.ModelForm):
    class Meta:
        model = Position
        fields = ["title", "department", "description", "default_schedule", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].queryset = Department.objects.all_tenants().filter(tenant=tenant, is_active=True)
        self.fields["department"].required = False
        self.fields["default_schedule"].queryset = Schedule.objects.all_tenants().filter(tenant=tenant, is_active=True)
        self.fields["default_schedule"].required = False
        apply_module_gating(self, tenant, {"department": "departments_enabled"})
