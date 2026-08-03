from .models import AuditLog

# Codes d'action — CDC §14.2.1 (authentification). Les autres catégories
# (utilisateurs, pointages, données, documents) seront ajoutées avec leurs
# modules respectifs.
LOGIN_SUCCESS = "LOGIN_SUCCESS"
LOGIN_FAILURE = "LOGIN_FAILURE"
LOGOUT = "LOGOUT"
ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
PASSWORD_RESET_REQUESTED = "PASSWORD_RESET_REQUESTED"
PASSWORD_RESET_COMPLETED = "PASSWORD_RESET_COMPLETED"
PASSWORD_CHANGED = "PASSWORD_CHANGED"

# CDC §14.2.3 — pointages.
CLOCK_SUCCESS = "CLOCK_SUCCESS"
CLOCK_REJECTED = "CLOCK_REJECTED"

# CDC §14.2.4 — organisations (actions Super Admin, CDC §3.1.1).
CREATE_ORGANIZATION = "CREATE_ORGANIZATION"
UPDATE_ORGANIZATION = "UPDATE_ORGANIZATION"
SUSPEND_ORGANIZATION = "SUSPEND_ORGANIZATION"
REACTIVATE_ORGANIZATION = "REACTIVATE_ORGANIZATION"
DELETE_ORGANIZATION = "DELETE_ORGANIZATION"

# CDC §14.2.4 — données.
EXPORT_DATA = "EXPORT_DATA"
IMPORT_DATA = "IMPORT_DATA"

# CDC §15.4 — module IA.
AI_QUESTION_ASKED = "AI_QUESTION_ASKED"
AI_CONFIG_UPDATED = "AI_CONFIG_UPDATED"


def log_event(request, action, result, *, user=None, tenant=None, description="", error=""):
    """Enregistre un événement dans le journal d'audit (CDC §14).

    `user` est optionnel car un LOGIN_FAILURE sur un e-mail inconnu n'a pas
    d'utilisateur associé — l'événement doit quand même être tracé.
    """
    if user is not None and tenant is None:
        tenant = user.tenant

    AuditLog.objects.create(
        tenant=tenant,
        user=user,
        user_email=getattr(user, "email", ""),
        user_role=getattr(user, "role", ""),
        action=action,
        description=description,
        result=result,
        details_erreur=error,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
    )
