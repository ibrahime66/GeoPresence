from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.core.views import TenantFormMixin, TenantQuerysetMixin

from .forms import AgencyForm
from .models import Agency

ADMIN_ONLY = (User.Role.ADMIN,)


class AgencyListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ADMIN_ONLY
    model = Agency
    template_name = "agencies/agency_list.html"
    context_object_name = "agencies"


class AgencyCreateView(RoleRequiredMixin, TenantFormMixin, CreateView):
    allowed_roles = ADMIN_ONLY
    model = Agency
    form_class = AgencyForm
    template_name = "agencies/agency_form.html"
    success_url = reverse_lazy("agencies:list")


class AgencyUpdateView(RoleRequiredMixin, TenantFormMixin, UpdateView):
    allowed_roles = ADMIN_ONLY
    model = Agency
    form_class = AgencyForm
    template_name = "agencies/agency_form.html"
    success_url = reverse_lazy("agencies:list")
