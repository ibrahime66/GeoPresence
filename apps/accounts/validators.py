import re

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
