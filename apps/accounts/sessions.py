"""CDC §5.6.2 — gestion des sessions actives.

Pas de dépendance externe pour parser le user-agent (le projet n'utilise que
Django Templates/Bootstrap/JS vanilla, CDC §24.1) : une heuristique simple
suffit pour l'affichage, elle n'a aucun rôle de sécurité.
"""

import re

from django.contrib.sessions.models import Session

from .models import UserSession

_BROWSER_PATTERNS = [
    ("Edge", r"Edg/"),
    ("Chrome", r"Chrome/"),
    ("Firefox", r"Firefox/"),
    ("Safari", r"Version/.*Safari/"),
    ("Opera", r"OPR/"),
]

_OS_PATTERNS = [
    ("Windows", r"Windows"),
    ("macOS", r"Mac OS X"),
    ("Android", r"Android"),
    ("iOS", r"iPhone|iPad|iPod"),
    ("Linux", r"Linux"),
]


def parse_user_agent(ua):
    ua = ua or ""
    browser = next((name for name, pattern in _BROWSER_PATTERNS if re.search(pattern, ua)), "Navigateur inconnu")
    os_name = next((name for name, pattern in _OS_PATTERNS if re.search(pattern, ua)), "OS inconnu")
    if "iPad" in ua or "Tablet" in ua:
        device_type = "Tablette"
    elif "Mobi" in ua or "iPhone" in ua or "Android" in ua:
        device_type = "Mobile"
    else:
        device_type = "Ordinateur"
    return device_type, browser, os_name


def register_session(request, user):
    """Appelé à la connexion (CDC §5.2.3 point 12) : force la création de la
    clé de session Django si nécessaire, puis journalise la session côté métier."""
    if not request.session.session_key:
        request.session.save()

    device_type, browser, os_name = parse_user_agent(request.META.get("HTTP_USER_AGENT", ""))
    UserSession.objects.update_or_create(
        session_key=request.session.session_key,
        defaults={
            "user": user,
            "ip_address": request.META.get("REMOTE_ADDR"),
            "user_agent": request.META.get("HTTP_USER_AGENT", "")[:255],
            "device_type": device_type,
            "browser": browser,
            "os": os_name,
        },
    )


def touch_session(session_key):
    """Rafraîchit la dernière activité — appelé à chaque requête authentifiée
    (cf. apps.accounts.middleware.SessionActivityMiddleware)."""
    UserSession.objects.filter(session_key=session_key).update(last_activity_at=_now())


def _now():
    from django.utils import timezone

    return timezone.now()


def revoke_session(user_session):
    """Supprime la session Django sous-jacente (invalide réellement l'accès
    de l'appareil concerné dès sa prochaine requête) en plus de la ligne de suivi."""
    Session.objects.filter(pk=user_session.session_key).delete()
    user_session.delete()


def revoke_all_sessions(user, except_session_key=None):
    """RM-AUTH-008 : invalide toutes les sessions d'un compte — utilisé au
    changement de mot de passe (sauf la session courante) et par
    l'Administrateur pour déconnecter un utilisateur de partout (CDC §5.6.2)."""
    qs = UserSession.objects.filter(user=user)
    if except_session_key:
        qs = qs.exclude(session_key=except_session_key)
    session_keys = list(qs.values_list("session_key", flat=True))
    if session_keys:
        Session.objects.filter(pk__in=session_keys).delete()
    qs.delete()
