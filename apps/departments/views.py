from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.core.views import TenantFormMixin, TenantQuerysetMixin

from .forms import DepartmentForm, PositionForm
from .models import Department, Position

ADMIN_ONLY = (User.Role.ADMIN,)


class DepartmentListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ADMIN_ONLY
    model = Department
    template_name = "departments/department_list.html"
    context_object_name = "departments"


class DepartmentCreateView(RoleRequiredMixin, TenantFormMixin, CreateView):
    allowed_roles = ADMIN_ONLY
    model = Department
    form_class = DepartmentForm
    template_name = "departments/department_form.html"
    success_url = reverse_lazy("departments:list")


class DepartmentUpdateView(RoleRequiredMixin, TenantFormMixin, UpdateView):
    allowed_roles = ADMIN_ONLY
    model = Department
    form_class = DepartmentForm
    template_name = "departments/department_form.html"
    success_url = reverse_lazy("departments:list")


class PositionListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ADMIN_ONLY
    model = Position
    template_name = "departments/position_list.html"
    context_object_name = "positions"


class PositionCreateView(RoleRequiredMixin, TenantFormMixin, CreateView):
    allowed_roles = ADMIN_ONLY
    model = Position
    form_class = PositionForm
    template_name = "departments/position_form.html"
    success_url = reverse_lazy("departments:position_list")


class PositionUpdateView(RoleRequiredMixin, TenantFormMixin, UpdateView):
    allowed_roles = ADMIN_ONLY
    model = Position
    form_class = PositionForm
    template_name = "departments/position_form.html"
    success_url = reverse_lazy("departments:position_list")
