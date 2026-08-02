from django.shortcuts import redirect
from django.urls import resolve
from django.urls.exceptions import Resolver404


class ForcePasswordChangeMiddleware:
    """CDC §5.5 : tant que must_change_password=True, l'utilisateur ne peut
    accéder à aucune fonctionnalité hormis le changement de mot de passe et
    la déconnexion."""

    EXEMPT_VIEW_NAMES = {"accounts:force_password_change", "accounts:logout"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and user.must_change_password:
            try:
                view_name = resolve(request.path_info).view_name
            except Resolver404:
                view_name = None
            if view_name not in self.EXEMPT_VIEW_NAMES and not request.path_info.startswith(("/static/", "/media/")):
                return redirect("accounts:force_password_change")
        return self.get_response(request)
