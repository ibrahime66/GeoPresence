"""CDC §13.2.1/§6.4.3 — historique et expiration des mots de passe,
paramètres par organisation (cf. apps.tenants.org_settings)."""

from datetime import timedelta

from django.utils import timezone

from apps.tenants.org_settings import get_org_setting

from .models import PasswordHistory


def record_password(user):
    """À appeler juste après tout set_password()+save() réussi : ajoute le
    hash courant à l'historique et purge au-delà du nombre configuré pour
    l'organisation (password_history_count)."""
    PasswordHistory.objects.create(user=user, hashed_password=user.password)
    count = get_org_setting(user.tenant, "password_history_count")
    stale_ids = list(
        PasswordHistory.objects.filter(user=user).order_by("-created_at").values_list("id", flat=True)[count:]
    )
    if stale_ids:
        PasswordHistory.objects.filter(id__in=stale_ids).delete()


def password_expires_at(user):
    if not user.last_password_change:
        return None
    days = get_org_setting(user.tenant, "password_expiration_days")
    return user.last_password_change + timedelta(days=days)


def is_password_expired(user):
    expires_at = password_expires_at(user)
    return expires_at is not None and timezone.now() > expires_at
