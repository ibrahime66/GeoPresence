from django.shortcuts import redirect
from django.urls import resolve
from django.urls.exceptions import Resolver404
from django.utils import translation

from . import sessions
from .password_policy import is_password_expired


class UserLanguageMiddleware:
    """CDC §3.5.1/§24.2 : la préférence de langue enregistrée sur le compte
    (User.language) prévaut sur la détection standard de LocaleMiddleware
    (session/cookie/en-tête Accept-Language) dès qu'un utilisateur est
    authentifié — les visiteurs anonymes (page de connexion...) restent
    gérés par LocaleMiddleware seul."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and user.language:
            translation.activate(user.language)
            request.LANGUAGE_CODE = user.language
        return self.get_response(request)


class ForcePasswordChangeMiddleware:
    """CDC §5.5/§13.2.1 : tant que must_change_password=True — ou que le mot
    de passe a dépassé sa durée de validité (PASSWORD_EXPIRATION_DAYS) —
    l'utilisateur ne peut accéder à aucune fonctionnalité hormis le
    changement de mot de passe et la déconnexion."""

    EXEMPT_VIEW_NAMES = {"accounts:force_password_change", "accounts:logout"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and (user.must_change_password or is_password_expired(user)):
            try:
                view_name = resolve(request.path_info).view_name
            except Resolver404:
                view_name = None
            if view_name not in self.EXEMPT_VIEW_NAMES and not request.path_info.startswith(("/static/", "/media/")):
                return redirect("accounts:force_password_change")
        return self.get_response(request)


class SessionActivityMiddleware:
    """CDC §5.6.2 : tient à jour `UserSession.last_activity_at` — une simple
    UPDATE par requête authentifiée, pas de throttling (volumes actuels trop
    faibles pour que ça pèse ; à revoir si ça devient un point chaud)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = getattr(request, "user", None)
        session_key = getattr(request.session, "session_key", None)
        if user is not None and user.is_authenticated and session_key:
            sessions.touch_session(session_key)
        return response
