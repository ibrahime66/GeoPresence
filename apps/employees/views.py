import secrets

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.core.views import TenantFormMixin, TenantQuerysetMixin

from .forms import EmployeeCreateForm, EmployeeUpdateForm
from .models import Employee

ADMIN_ONLY = (User.Role.ADMIN,)


class EmployeeListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ADMIN_ONLY
    model = Employee
    template_name = "employees/employee_list.html"
    context_object_name = "employees"

    def get_queryset(self):
        return super().get_queryset().select_related("user", "department", "position", "primary_agency")


class EmployeeCreateView(RoleRequiredMixin, View):
    """CDC §11.3.2 : crée le User (mot de passe temporaire, changement forcé à
    la première connexion — déjà géré par le module accounts) ET le profil
    Employee, puis envoie l'e-mail de bienvenue."""

    allowed_roles = ADMIN_ONLY
    template_name = "employees/employee_create_form.html"

    def get(self, request):
        return render(request, self.template_name, {"form": EmployeeCreateForm(tenant=request.tenant)})

    def post(self, request):
        form = EmployeeCreateForm(request.POST, tenant=request.tenant)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        temp_password = secrets.token_urlsafe(10)
        user = User.objects.create_user(
            email=form.cleaned_data["email"],
            password=temp_password,
            tenant=request.tenant,
            role=form.cleaned_data["role"],
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            must_change_password=True,
        )

        employee = Employee(
            tenant=request.tenant,
            user=user,
            department=form.cleaned_data["department"],
            position=form.cleaned_data["position"],
            primary_agency=form.cleaned_data["primary_agency"],
            manager=form.cleaned_data["manager"],
            contract_type=form.cleaned_data["contract_type"],
            hire_date=form.cleaned_data["hire_date"],
            annual_leave_days=form.cleaned_data["annual_leave_days"],
        )
        try:
            employee.full_clean()
        except ValidationError as exc:
            user.delete()
            for errors in exc.message_dict.values():
                for error in errors:
                    form.add_error(None, error)
            return render(request, self.template_name, {"form": form})

        employee.save()

        send_mail(
            subject="Bienvenue sur GeoPresence",
            message=(
                f"Bonjour {user.first_name},\n\n"
                f"Votre compte a été créé sur GeoPresence.\n"
                f"E-mail : {user.email}\n"
                f"Mot de passe temporaire : {temp_password}\n\n"
                "Connectez-vous et changez votre mot de passe dès la première connexion."
            ),
            from_email=None,
            recipient_list=[user.email],
        )
        messages.success(request, f"Employé créé. Accès envoyés par e-mail à {user.email}.")
        return redirect("employees:list")


class EmployeeUpdateView(RoleRequiredMixin, TenantFormMixin, UpdateView):
    allowed_roles = ADMIN_ONLY
    model = Employee
    form_class = EmployeeUpdateForm
    template_name = "employees/employee_form.html"
    success_url = reverse_lazy("employees:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        employee = self.object
        # Suspendre/archiver un employé lui coupe aussi l'accès à la connexion ;
        # le réactiver la restaure. CDC §11.4.
        should_be_active = employee.status in (Employee.Status.ACTIVE, Employee.Status.ON_LEAVE)
        if employee.user.is_active != should_be_active:
            employee.user.is_active = should_be_active
            employee.user.save(update_fields=["is_active"])
        return response
