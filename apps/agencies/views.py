from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.core.views import DEFAULT_PAGE_SIZE, TenantFormMixin, TenantQuerysetMixin, ToggleActiveView

from .forms import AgencyForm
from .models import Agency

ADMIN_ONLY = (User.Role.ADMIN,)


class AgencyListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ADMIN_ONLY
    model = Agency
    template_name = "agencies/agency_list.html"
    context_object_name = "agencies"
    paginate_by = DEFAULT_PAGE_SIZE


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


class AgencyToggleActiveView(ToggleActiveView):
    """CDC §7.3 : activer/désactiver une agence — une agence désactivée
    n'accepte plus aucun pointage."""

    allowed_roles = ADMIN_ONLY
    model = Agency
    success_url = reverse_lazy("agencies:list")
