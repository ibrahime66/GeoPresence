from django.core.validators import RegexValidator
from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel
from apps.core.storage import generate_upload_filename

HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r"^#[0-9A-Fa-f]{6}$",
    message="La couleur doit être un code hexadécimal valide, ex. #1565C0.",
)


def organization_logo_path(instance, filename):
    return f"organizations/{instance.id}/logo/{generate_upload_filename(filename)}"


class Organization(UUIDModel, TimeStampedModel):
    """Le tenant lui-même. CDC §6, ANALYSE-TECHNIQUE §5.2 (table organizations)."""

    class OrgType(models.TextChoices):
        COMPANY = "COMPANY", "Entreprise"
        SCHOOL = "SCHOOL", "Établissement scolaire"
        UNIVERSITY = "UNIVERSITY", "Université"
        RESTAURANT = "RESTAURANT", "Restaurant"
        PHARMACY = "PHARMACY", "Pharmacie"
        HOSPITAL = "HOSPITAL", "Clinique / Hôpital"
        NGO = "NGO", "ONG"
        ADMIN = "ADMIN", "Administration publique"
        ASSOCIATION = "ASSOCIATION", "Association"
        OTHER = "OTHER", "Autre"

    class EmployeeCountRange(models.TextChoices):
        UNDER_10 = "UNDER_10", "< 10"
        FROM_10_TO_50 = "10_50", "10 – 50"
        FROM_50_TO_200 = "50_200", "50 – 200"
        FROM_200_TO_500 = "200_500", "200 – 500"
        OVER_500 = "OVER_500", "> 500"

    class Language(models.TextChoices):
        FR = "fr", "Français"
        EN = "en", "English"
        AR = "ar", "العربية"

    class DateFormat(models.TextChoices):
        DMY = "DD/MM/YYYY", "JJ/MM/AAAA"
        MDY = "MM/DD/YYYY", "MM/JJ/AAAA"
        YMD = "YYYY-MM-DD", "AAAA-MM-JJ"

    class TimeFormat(models.TextChoices):
        H24 = "24H", "24h"
        H12 = "12H", "12h (AM/PM)"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspendue"
        EXPIRED = "EXPIRED", "Expirée"
        DELETED = "DELETED", "Supprimée"

    legal_name = models.CharField("nom légal", max_length=255)
    display_name = models.CharField("nom commercial", max_length=255)
    slug = models.SlugField(unique=True)

    org_type = models.CharField(max_length=20, choices=OrgType.choices, default=OrgType.OTHER)
    sector = models.CharField("secteur d'activité", max_length=255, blank=True)

    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField()
    website = models.URLField(blank=True)
    employee_count_range = models.CharField(
        max_length=10, choices=EmployeeCountRange.choices, blank=True
    )

    timezone = models.CharField(max_length=64, default="UTC")
    language = models.CharField(max_length=2, choices=Language.choices, default=Language.FR)
    date_format = models.CharField(max_length=10, choices=DateFormat.choices, default=DateFormat.DMY)
    time_format = models.CharField(max_length=3, choices=TimeFormat.choices, default=TimeFormat.H24)

    logo = models.ImageField(upload_to=organization_logo_path, blank=True, null=True, max_length=255)
    primary_color = models.CharField(max_length=7, default="#0D2137", validators=[HEX_COLOR_VALIDATOR])
    secondary_color = models.CharField(max_length=7, default="#1565C0", validators=[HEX_COLOR_VALIDATOR])

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    # Paramètres de pointage/sécurité/etc. non encore structurés en champs dédiés
    # (tolérance retard, rayon GPS par défaut, durée de session...) — CDC §6.4.
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        # RM-ORG-001 : slug immuable après création.
        if self.pk:
            original_slug = Organization.objects.filter(pk=self.pk).values_list("slug", flat=True).first()
            if original_slug is not None and original_slug != self.slug:
                raise ValueError("Le slug d'une organisation ne peut pas être modifié après création (RM-ORG-001).")
        super().save(*args, **kwargs)
