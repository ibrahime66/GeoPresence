import re

from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError


class UppercaseValidator:
    def validate(self, password, user=None):
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre majuscule.", code="password_no_upper"
            )

    def get_help_text(self):
        return "Le mot de passe doit contenir au moins une lettre majuscule."


class LowercaseValidator:
    def validate(self, password, user=None):
        if not re.search(r"[a-z]", password):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre minuscule.", code="password_no_lower"
            )

    def get_help_text(self):
        return "Le mot de passe doit contenir au moins une lettre minuscule."


class DigitValidator:
    def validate(self, password, user=None):
        if not re.search(r"\d", password):
            raise ValidationError("Le mot de passe doit contenir au moins un chiffre.", code="password_no_digit")

    def get_help_text(self):
        return "Le mot de passe doit contenir au moins un chiffre."


class SpecialCharacterValidator:
    SPECIAL_CHARS = r"@#$!%*?&_\-+=.,;:^~"

    def validate(self, password, user=None):
        if not re.search(f"[{re.escape(self.SPECIAL_CHARS)}]", password):
            raise ValidationError(
                "Le mot de passe doit contenir au moins un caractère spécial (@, #, $, !, ...).",
                code="password_no_special",
            )

    def get_help_text(self):
        return "Le mot de passe doit contenir au moins un caractère spécial (@, #, $, !, ...)."


class OrgMinimumLengthValidator:
    """CDC §6.4.3/§13.2.1 : longueur minimale — le plancher plateforme (8,
    cf. MinimumLengthValidator dans AUTH_PASSWORD_VALIDATORS) ne peut être
    qu'AUGMENTÉ par une organisation, jamais abaissé."""

    def validate(self, password, user=None):
        if user is None or user.pk is None:
            return
        from apps.tenants.org_settings import get_org_setting

        min_length = get_org_setting(user.tenant, "password_min_length")
        if len(password) < min_length:
            raise ValidationError(
                f"Le mot de passe doit contenir au moins {min_length} caractères pour cette organisation.",
                code="password_too_short_for_org",
            )

    def get_help_text(self):
        return "Votre organisation peut exiger un mot de passe plus long que le minimum de 8 caractères."


class PersonalInfoValidator:
    """Interdit que le mot de passe contienne le prénom, le nom ou l'e-mail (CDC §13.2.1)."""

    def validate(self, password, user=None):
        if user is None:
            return
        lowered_password = password.lower()
        candidates = [
            getattr(user, "first_name", ""),
            getattr(user, "last_name", ""),
            (getattr(user, "email", "") or "").split("@")[0],
        ]
        for value in candidates:
            if value and len(value) >= 3 and value.lower() in lowered_password:
                raise ValidationError(
                    "Le mot de passe ne peut pas contenir votre nom, prénom ou e-mail.",
                    code="password_contains_personal_info",
                )

    def get_help_text(self):
        return "Le mot de passe ne peut pas contenir votre nom, prénom ou e-mail."


class PasswordHistoryValidator:
    """CDC §13.2.1/§6.4.3 : le nouveau mot de passe ne peut pas être identique
    à l'un des N derniers (N configurable par organisation, défaut 5) — y
    compris le mot de passe actuel, déjà dans l'historique."""

    def validate(self, password, user=None):
        if user is None or user.pk is None:
            return
        from apps.tenants.org_settings import get_org_setting

        from .models import PasswordHistory

        count = get_org_setting(user.tenant, "password_history_count")
        recent = PasswordHistory.objects.filter(user=user).order_by("-created_at")[:count]
        for entry in recent:
            if check_password(password, entry.hashed_password):
                raise ValidationError(
                    f"Ce mot de passe a déjà été utilisé récemment — choisissez-en un différent des "
                    f"{count} derniers.",
                    code="password_reused",
                )

    def get_help_text(self):
        return "Le mot de passe ne peut pas être identique à l'un de vos 5 derniers mots de passe."
