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


class OnboardingDismissView(RoleRequiredMixin, View):
    """Masque la check-list de démarrage du tableau de bord Admin — persisté
    par organisation (pas par navigateur) : un second Admin de la même
    organisation ne doit pas revoir une check-list qu'un collègue a déjà
    fermée. Se réaffiche d'elle-même si l'org redevient incomplète (impossible
    en pratique, rien ne "dé-crée" une agence/un horaire/un employé)."""

    allowed_roles = ADMIN_ONLY

    def post(self, request):
        tenant = request.tenant
        tenant.settings = {**(tenant.settings or {}), "onboarding_dismissed": True}
        tenant.save(update_fields=["settings"])
        # Toujours postée depuis le tableau de bord lui-même — pas de `next`
        # à valider (jamais suivre une URL de redirection fournie par le
        # client sans whitelist, cf. open redirect).
        return redirect("core:dashboard")
