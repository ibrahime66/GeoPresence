from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel


class Backup(UUIDModel, TimeStampedModel):
    """CDC §18.4 : sauvegarde complète de la base de données, chiffrée au
    repos. Modèle global à la plateforme — pas un TenantModel, une sauvegarde
    couvre toutes les organisations à la fois."""

    class Status(models.TextChoices):
        SUCCESS = "SUCCESS", "Réussie"
        FAILED = "FAILED", "Échouée"

    filename = models.CharField(max_length=255)
    size_bytes = models.BigIntegerField(default=0)
    checksum_sha256 = models.CharField(max_length=64, blank=True)

    is_manual = models.BooleanField(default=False)
    triggered_by = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="backups_triggered"
    )
    comment = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SUCCESS)
    error_message = models.TextField(blank=True)

    # CDC §18.4.3 : au moins deux emplacements distincts. `secondary_path` est
    # vide si aucun second emplacement n'est configuré (BACKUP_SECONDARY_DIR).
    secondary_path = models.CharField(max_length=500, blank=True)

    # CDC §18.4.4 : résultat du dernier contrôle d'intégrité (vérification du
    # checksum après déchiffrement) — tient lieu de "test de restauration
    # hebdomadaire" simplifié (pas d'environnement de test séparé disponible).
    last_verified_at = models.DateTimeField(null=True, blank=True)
    last_verification_ok = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.filename} ({self.get_status_display()})"
