from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.accounts.constants import PASSWORD_RESET_TOKEN_LIFETIME_MINUTES
from apps.core.models import TimeStampedModel, UUIDModel


class UserManager(BaseUserManager):
    """L'identifiant de connexion est l'e-mail (CDC §5.2.5) — pas de username."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("L'adresse e-mail est obligatoire.")
        user = self.model(email=email.lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        # Un createsuperuser crée toujours un Super Administrateur de plateforme
        # (CDC §2.3.3 / §3.1) : jamais rattaché à un tenant.
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", User.Role.SUPER_ADMIN)
        extra_fields.setdefault("must_change_password", False)
        extra_fields["tenant"] = None

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Un superuser doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superuser doit avoir is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, UUIDModel, TimeStampedModel):
    """CDC §3 (acteurs) + §5 (authentification), ANALYSE-TECHNIQUE §2.2/§3 (app accounts).

    Les informations RH détaillées (matricule, poste, contrat...) vivent dans
    l'app `employees`, pas ici — ce modèle ne porte que l'identité et la sécurité
    du compte.
    """

    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Administrateur"
        ADMIN = "ADMIN", "Administrateur"
        MANAGER = "MANAGER", "Manager"
        EMPLOYEE = "EMPLOYEE", "Employé"

    class Language(models.TextChoices):
        FR = "fr", "Français"
        EN = "en", "English"
        AR = "ar", "العربية"

    tenant = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
        help_text="Vide uniquement pour le Super Administrateur (CDC §2.3.3).",
    )

    email = models.EmailField("e-mail", unique=True)
    first_name = models.CharField("prénom", max_length=150, blank=True)
    last_name = models.CharField("nom", max_length=150, blank=True)
    role = models.CharField("rôle", max_length=20, choices=Role.choices, default=Role.EMPLOYEE)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # RM-AUTH-004 : verrouillage après N échecs (défaut 5 / 15 min, configurable par organisation).
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    # CDC §13.3.1 : blocage progressif — nombre de verrouillages consécutifs,
    # utilisé pour faire croître la durée (15min/30min/1h/4h/24h). Remis à
    # zéro à chaque connexion réussie.
    lockout_count = models.PositiveSmallIntegerField(default=0)

    # RM-AUTH-006 : changement de mot de passe obligatoire à la première connexion.
    must_change_password = models.BooleanField(default=True)
    last_password_change = models.DateTimeField(null=True, blank=True)

    # CDC §3.5.1/§24.2 : langue d'affichage — préférence personnelle, distincte
    # de la langue par défaut de l'organisation (Organization.language, qui ne
    # sert qu'à pré-remplir ce champ à la création du compte).
    language = models.CharField("langue", max_length=2, choices=Language.choices, default=Language.FR)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def clean(self):
        super().clean()
        # RM-ORG-004 / CDC §2.3.3 : le Super Admin n'appartient à aucun tenant,
        # tous les autres rôles doivent obligatoirement en avoir un.
        if self.role == self.Role.SUPER_ADMIN and self.tenant_id is not None:
            raise ValidationError("Le Super Administrateur ne doit être rattaché à aucune organisation.")
        if self.role != self.Role.SUPER_ADMIN and self.tenant_id is None:
            raise ValidationError("Un utilisateur non Super Administrateur doit appartenir à une organisation.")


class UserSession(UUIDModel):
    """CDC §5.6.2 : suivi des sessions actives d'un utilisateur, en plus de la
    session Django elle-même (django.contrib.sessions.models.Session, qui ne
    porte aucune info exploitable côté métier — juste une clé et un blob
    opaque). Une ligne par session vivante ; supprimée à la déconnexion ou à
    la révocation (et la Session Django sous-jacente est supprimée en même
    temps pour invalider réellement l'accès, cf. apps.accounts.sessions)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    session_key = models.CharField(max_length=40, unique=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    device_type = models.CharField(max_length=20, blank=True)
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-last_activity_at"]

    def __str__(self):
        return f"{self.user} — {self.browser}/{self.os} ({self.ip_address})"


class PasswordHistory(UUIDModel):
    """CDC §13.2.1 : conserve le hash des N derniers mots de passe d'un
    compte pour empêcher leur réutilisation — jamais le mot de passe en clair."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_history")
    hashed_password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "password histories"


class PasswordResetToken(UUIDModel):
    """CDC §5.4 : token UUID v4 à usage unique, expire après 30 min, un seul
    token valide à la fois par compte. L'UUID `id` (hérité de UUIDModel) sert
    lui-même de valeur de token dans l'URL — pas besoin d'un champ séparé."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def is_valid(self):
        return self.used_at is None and timezone.now() < self.expires_at

    @classmethod
    def issue_for(cls, user, lifetime_minutes=PASSWORD_RESET_TOKEN_LIFETIME_MINUTES):
        # RM-AUTH-007 : invalide tout token encore actif avant d'en émettre un nouveau.
        cls.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())
        return cls.objects.create(user=user, expires_at=timezone.now() + timedelta(minutes=lifetime_minutes))
