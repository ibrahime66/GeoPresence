from django import forms
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.agencies.models import Agency
from apps.core.forms import BootstrapModelFormMixin
from apps.departments.models import Department, Position

from .models import Employee

# Un Admin ne peut jamais créer de SUPER_ADMIN via ce formulaire (rôle plateforme uniquement).
CREATABLE_ROLES = [
    (User.Role.EMPLOYEE, "Employé"),
    (User.Role.SUPERVISOR, "Superviseur"),
    (User.Role.MANAGER, "Manager"),
    (User.Role.ADMIN, "Administrateur"),
]
MANAGER_ROLES = (User.Role.MANAGER, User.Role.SUPERVISOR, User.Role.ADMIN)


class EmployeeCreateForm(forms.Form):
    """CDC §11.3 : crée le compte User ET le profil Employee ensemble."""

    email = forms.EmailField(label="E-mail professionnel")
    first_name = forms.CharField(label="Prénom", max_length=150)
    last_name = forms.CharField(label="Nom", max_length=150)
    role = forms.ChoiceField(choices=CREATABLE_ROLES, label="Rôle")

    department = forms.ModelChoiceField(queryset=Department.objects.none(), required=False, label="Département")
    position = forms.ModelChoiceField(queryset=Position.objects.none(), required=False, label="Poste")
    primary_agency = forms.ModelChoiceField(queryset=Agency.objects.none(), label="Agence principale")
    manager = forms.ModelChoiceField(queryset=User.objects.none(), required=False, label="Manager direct")

    contract_type = forms.ChoiceField(choices=Employee.ContractType.choices, label="Type de contrat")
    hire_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="Date d'entrée")
    annual_leave_days = forms.DecimalField(
        label="Droit aux congés (j/an)", max_digits=5, decimal_places=1, initial=25
    )

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        for field in self.fields.values():
            css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()
        self.fields["department"].queryset = Department.objects.all_tenants().filter(tenant=tenant, is_active=True)
        self.fields["position"].queryset = Position.objects.all_tenants().filter(tenant=tenant, is_active=True)
        self.fields["primary_agency"].queryset = Agency.objects.all_tenants().filter(tenant=tenant, is_active=True)
        self.fields["manager"].queryset = User.objects.filter(tenant=tenant, role__in=MANAGER_ROLES)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        # L'e-mail est unique sur TOUTE la plateforme (CDC §11.3.3), pas
        # seulement au sein du tenant.
        if User.objects.filter(email=email).exists():
            raise ValidationError("Un compte existe déjà avec cet e-mail.")
        return email


class EmployeeUpdateForm(BootstrapModelFormMixin, forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "department", "position", "primary_agency", "manager",
            "contract_type", "hire_date", "contract_end_date", "annual_leave_days", "status",
        ]
        widgets = {
            "hire_date": forms.DateInput(attrs={"type": "date"}),
            "contract_end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].queryset = Department.objects.all_tenants().filter(tenant=tenant, is_active=True)
        self.fields["department"].required = False
        self.fields["position"].queryset = Position.objects.all_tenants().filter(tenant=tenant, is_active=True)
        self.fields["position"].required = False
        self.fields["primary_agency"].queryset = Agency.objects.all_tenants().filter(tenant=tenant, is_active=True)
        self.fields["manager"].queryset = User.objects.filter(tenant=tenant, role__in=MANAGER_ROLES)
        self.fields["manager"].required = False
