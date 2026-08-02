from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin):
    """Restreint l'accès à une vue à une liste de rôles (RBAC minimal — CDC §3).
    `allowed_roles` vide = tout utilisateur authentifié (comportement de
    LoginRequiredMixin seul)."""

    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and self.allowed_roles and request.user.role not in self.allowed_roles:
            raise PermissionDenied("Vous n'avez pas les droits nécessaires pour accéder à cette page.")
        return super().dispatch(request, *args, **kwargs)
