from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import TenantModel
from apps.core.storage import generate_upload_filename

from . import geofencing


def agency_photo_path(instance, filename):
    return f"organizations/{instance.tenant_id}/agencies/{instance.id}/{generate_upload_filename(filename)}"


class Agency(TenantModel):
    """CDC §7. Unité de base du geofencing — c'est à partir de ses coordonnées
    que le système détermine si un pointage est autorisé (CDC §8)."""

    class AgencyType(models.TextChoices):
        HEADQUARTERS = "HEADQUARTERS", "Siège"
        BRANCH = "BRANCH", "Agence"
        SUBSIDIARY = "SUBSIDIARY", "Filiale"
        WAREHOUSE = "WAREHOUSE", "Entrepôt"
        CONSTRUCTION_SITE = "CONSTRUCTION_SITE", "Chantier"
        REMOTE = "REMOTE", "Télétravail"
        OTHER = "OTHER", "Autre"

    name = models.CharField("nom", max_length=255)
    code = models.CharField("code", max_length=20)
    agency_type = models.CharField(max_length=20, choices=AgencyType.choices, default=AgencyType.BRANCH)

    address = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    responsible = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agencies_managed",
    )

    # CDC §7.2 : décimale, 6 décimales minimum. DecimalField évite les erreurs
    # d'arrondi de FloatField sur des coordonnées utilisées pour du calcul de
    # distance légal/contractuel.
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    # CDC §7.2 : min 50m, max 5000m, défaut 200m.
    radius_meters = models.PositiveIntegerField(
        "rayon GPS (m)", default=200, validators=[MinValueValidator(50), MaxValueValidator(5000)]
    )
    # Zones supplémentaires (parking, annexe...) — CDC §8.5. Liste de
    # {"label": str, "latitude": float, "longitude": float, "radius": int}.
    extra_zones = models.JSONField(default=list, blank=True)

    is_active = models.BooleanField(default=True)
    allow_offline_clocking = models.BooleanField(
        "pointage hors ligne autorisé", default=True, help_text="Surcharge le paramètre par défaut de l'organisation."
    )

    photo = models.ImageField(upload_to=agency_photo_path, blank=True, null=True, max_length=255)
    notes = models.TextField(blank=True)

    # CDC §10.3 : horaire par défaut de l'agence — niveau de priorité 4 (le plus
    # faible) dans la hiérarchie d'affectation employé > poste > département > agence.
    default_schedule = models.ForeignKey(
        "schedules.Schedule", on_delete=models.SET_NULL, null=True, blank=True, related_name="agencies"
    )

    class Meta:
        verbose_name_plural = "agencies"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="agencies_agency_tenant_code_uniq"),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clean(self):
        super().clean()
        if self.responsible_id and self.responsible.tenant_id != self.tenant_id:
            raise ValidationError("Le responsable d'agence doit appartenir à la même organisation.")
        if self.default_schedule_id and self.default_schedule.tenant_id != self.tenant_id:
            raise ValidationError("L'horaire par défaut doit appartenir à la même organisation.")
        for i, zone in enumerate(self.extra_zones):
            missing = {"label", "latitude", "longitude", "radius"} - set(zone or {})
            if missing:
                raise ValidationError(f"Zone supplémentaire #{i + 1} : champs manquants {sorted(missing)}.")

    def zones(self):
        """Toutes les zones autorisées : la zone principale + les zones supplémentaires."""
        yield {"label": self.name, "latitude": self.latitude, "longitude": self.longitude, "radius": self.radius_meters}
        yield from self.extra_zones

    def check_point(self, lat, lon, gps_accuracy=None):
        """CDC §8.3/8.5 : vérifie un point GPS contre la zone principale ET les
        zones supplémentaires ; autorisé dès qu'une zone correspond.
        Retourne (autorisé, distance_min_m, zone_la_plus_proche)."""
        from apps.tenants.org_settings import get_org_setting

        tolerance_meters = get_org_setting(self.tenant, "gps_tolerance_meters")
        best = None
        for zone in self.zones():
            authorized, distance, radius = geofencing.check_point_in_zone(
                lat, lon, zone["latitude"], zone["longitude"], zone["radius"], gps_accuracy, tolerance_meters
            )
            if best is None or distance < best[1]:
                best = (authorized, distance, zone)
            if authorized:
                return True, distance, zone
        return False, best[1] if best else None, best[2] if best else None
