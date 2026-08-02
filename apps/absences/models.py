from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TenantModel
from apps.core.storage import generate_upload_filename

from .validators import validate_justification_file


class AbsenceReason(TenantModel):
    """CDC §12.1.3 : liste de motifs configurable par organisation (pas figée)."""

    name = models.CharField(max_length=255)
    requires_certificate = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "name"], name="absences_reason_tenant_name_uniq"),
        ]

    def __str__(self):
        return self.name


def justification_path(instance, filename):
    return f"organizations/{instance.tenant_id}/absence-justificatifs/{instance.employee_id}/{generate_upload_filename(filename)}"


class Absence(TenantModel):
    """CDC §12.1. Une absence existe pour un (employé, jour) donné — créée soit
    manuellement ici, soit plus tard automatiquement par la tâche Celery de
    détection (différée, cf. is_auto_detected, non encore implémentée)."""

    class Status(models.TextChoices):
        UNJUSTIFIED = "UNJUSTIFIED", "Non justifiée"
        PENDING_REVIEW = "PENDING_REVIEW", "En attente de validation"
        JUSTIFIED = "JUSTIFIED", "Justifiée"
        REJECTED = "REJECTED", "Rejetée"

    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="absences")
    date = models.DateField()
    reason = models.ForeignKey(
        AbsenceReason, on_delete=models.SET_NULL, null=True, blank=True, related_name="absences"
    )
    employee_comment = models.TextField(blank=True)
    justification_file = models.FileField(
        upload_to=justification_path, blank=True, null=True, max_length=255, validators=[validate_justification_file]
    )

    status = models.CharField(max_length=15, choices=Status.choices, default=Status.UNJUSTIFIED)
    reviewer_comment = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="absences_reviewed"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    is_auto_detected = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "employee", "date"], name="absences_absence_emp_date_uniq"),
        ]

    def __str__(self):
        return f"{self.employee} — {self.date} ({self.get_status_display()})"

    def clean(self):
        super().clean()
        if self.employee_id and self.employee.tenant_id != self.tenant_id:
            raise ValidationError("L'employé doit appartenir à la même organisation.")
        if self.reason_id and self.reason.tenant_id != self.tenant_id:
            raise ValidationError("Le motif doit appartenir à la même organisation.")
