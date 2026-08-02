from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect

from apps.core.context import clear_current_tenant, set_current_tenant

from .models import Organization


class TenantMiddleware:
    """Résout le tenant courant depuis l'utilisateur authentifié (pas d'URL à
    slug pour l'instant — CDC §2.3.2 permet plusieurs stratégies, on a choisi
    la plus simple : identification via la session/l'utilisateur) et l'injecte
    dans request.tenant + le contexte thread-local consommé par TenantManager.

    RM-ORG-003/005 : si l'organisation de l'utilisateur devient suspendue en
    cours de session, la session est immédiatement invalidée à la requête
    suivante — pas besoin d'attendre l'expiration naturelle de la session."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        tenant = None

        if user is not None and user.is_authenticated:
            tenant = user.tenant
            if tenant is not None and tenant.status != Organization.Status.ACTIVE:
                auth_logout(request)
                messages.error(request, "Votre organisation est temporairement suspendue.")
                return redirect("accounts:login")

        request.tenant = tenant
        set_current_tenant(tenant)
        try:
            response = self.get_response(request)
        finally:
            clear_current_tenant()
        return response
