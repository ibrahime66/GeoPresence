from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User

from .forms import OrganizationSettingsForm

ADMIN_ONLY = (User.Role.ADMIN,)


class OrganizationSettingsView(RoleRequiredMixin, View):
    """CDC §3.2.1/§6.4 : paramètres de pointage et de sécurité de
    l'organisation — réservé à son Administrateur (jamais aux autres tenants,
    `request.tenant` est déjà scopé par TenantMiddleware)."""

    allowed_roles = ADMIN_ONLY
    template_name = "tenants/organization_settings.html"

    def get(self, request):
        form = OrganizationSettingsForm(initial=OrganizationSettingsForm.initial_from_organization(request.tenant))
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = OrganizationSettingsForm(request.POST)
        if form.is_valid():
            form.save(request.tenant)
            messages.success(request, "Paramètres de l'organisation mis à jour.")
            return redirect("tenants:settings")
        return render(request, self.template_name, {"form": form})
