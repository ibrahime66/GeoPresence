from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TenantModel


class AbsenceReason(TenantModel):
    """CDC §12.1.3 : liste de motifs configurable par organisation (pas figée)."""

    name = models.CharField("nom", max_length=255)
    requires_certificate = models.BooleanField("certificat requis", default=False)
    is_active = models.BooleanField("actif", default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "name"], name="absences_reason_tenant_name_uniq"),
        ]

    def __str__(self):
        return self.name


def justification_path(instance, filename):
    """Conservée pour compatibilité avec les migrations historiques
    (0001/0002 référencent cette fonction par chemin d'import) — le champ
    justification_file a été retiré, cette fonction n'est plus appelée."""
    return f"organizations/{instance.tenant_id}/absence-justificatifs/{instance.employee_id}/{filename}"


class Absence(TenantModel):
    """CDC §12.1. Une absence existe pour un (employé, jour) donné — créée soit
    manuellement ici, soit plus tard automatiquement par la tâche Celery de
    détection (différée, cf. is_auto_detected, non encore implémentée)."""

    class Status(models.TextChoices):
        UNJUSTIFIED = "UNJUSTIFIED", "Non justifiée"
        PENDING_REVIEW = "PENDING_REVIEW", "En attente de validation"
        JUSTIFIED = "JUSTIFIED", "Justifiée"
        REJECTED = "REJECTED", "Rejetée"

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="absences", verbose_name="employé"
    )
    date = models.DateField("date")
    reason = models.ForeignKey(
        AbsenceReason, on_delete=models.SET_NULL, null=True, blank=True, related_name="absences", verbose_name="motif"
    )
    custom_reason = models.CharField("motif personnalisé", max_length=255, blank=True)
    employee_comment = models.TextField("commentaire de l'employé", blank=True)

    status = models.CharField("statut", max_length=15, choices=Status.choices, default=Status.UNJUSTIFIED)
    reviewer_comment = models.TextField("commentaire du valideur", blank=True)
    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="absences_reviewed",
        verbose_name="validé par",
    )
    reviewed_at = models.DateTimeField("validé le", null=True, blank=True)

    is_auto_detected = models.BooleanField("détectée automatiquement", default=False)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "employee", "date"], name="absences_absence_emp_date_uniq"),
        ]

    def __str__(self):
        return f"{self.employee} — {self.date} ({self.get_status_display()})"

    @property
    def display_reason(self):
        if self.custom_reason:
            return self.custom_reason
        return self.reason.name if self.reason else ""

    def clean(self):
        super().clean()
        if self.employee_id and self.employee.tenant_id != self.tenant_id:
            raise ValidationError("L'employé doit appartenir à la même organisation.")
        if self.reason_id and self.reason.tenant_id != self.tenant_id:
            raise ValidationError("Le motif doit appartenir à la même organisation.")
