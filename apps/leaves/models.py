from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TenantModel


class Holiday(TenantModel):
    """CDC §12.4. `is_recurring` : jour férié annuel (ex. 1er mai) — le champ
    `date` sert alors uniquement de référence mois/jour, l'année est ignorée
    au moment du calcul (cf. apps.leaves.services.get_holiday_dates)."""

    name = models.CharField("nom", max_length=255)
    date = models.DateField("date")
    is_recurring = models.BooleanField("récurrent", default=True)

    class Meta:
        ordering = ["date"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "name", "date"], name="leaves_holiday_tenant_name_date_uniq"),
        ]

    def __str__(self):
        return f"{self.name} ({self.date:%d/%m})"


class LeaveType(TenantModel):
    """CDC §12.3.1 : types de congés configurables par organisation (congé
    annuel payé, RTT, sans solde, maladie, ...) — pas une liste figée."""

    name = models.CharField("nom", max_length=255)
    # Ex. congé annuel payé -> True ; congé sans solde / maladie -> généralement False.
    deducts_from_balance = models.BooleanField("déduit du solde", default=True)
    requires_justification = models.BooleanField("justificatif requis", default=False)
    is_active = models.BooleanField("actif", default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "name"], name="leaves_leavetype_tenant_name_uniq"),
        ]

    def __str__(self):
        return self.name


class Leave(TenantModel):
    """CDC §12.3.2/§12.3.3. `working_days` est calculé et figé à la soumission
    (apps.leaves.services.submit_leave) — jours fériés et week-ends exclus."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "En attente"
        APPROVED = "APPROVED", "Approuvé"
        REJECTED = "REJECTED", "Rejeté"
        CANCELLED = "CANCELLED", "Annulé"

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="leaves", verbose_name="employé"
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, related_name="leaves", verbose_name="type de congé")

    start_date = models.DateField("date de début")
    end_date = models.DateField("date de fin")
    working_days = models.DecimalField("jours ouvrés", max_digits=5, decimal_places=1)

    status = models.CharField("statut", max_length=10, choices=Status.choices, default=Status.PENDING)
    employee_comment = models.TextField("commentaire de l'employé", blank=True)
    reviewer_comment = models.TextField("commentaire du valideur", blank=True)
    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leaves_reviewed",
        verbose_name="validé par",
    )
    reviewed_at = models.DateTimeField("validé le", null=True, blank=True)

    class Meta:
        ordering = ["-start_date"]
        indexes = [models.Index(fields=["tenant", "employee", "status"], name="leaves_leave_emp_status_idx")]

    def __str__(self):
        return f"{self.employee} — {self.leave_type} ({self.start_date} → {self.end_date})"

    def clean(self):
        super().clean()
        if self.employee_id and self.employee.tenant_id != self.tenant_id:
            raise ValidationError("L'employé doit appartenir à la même organisation.")
        if self.leave_type_id and self.leave_type.tenant_id != self.tenant_id:
            raise ValidationError("Le type de congé doit appartenir à la même organisation.")
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("La date de fin doit être postérieure ou égale à la date de début.")

    def save(self, *args, **kwargs):
        # RM-CONGE-003 : modifier une demande déjà approuvée la repasse en
        # attente d'une nouvelle validation.
        if self.pk:
            previous = Leave.objects.all_tenants().filter(pk=self.pk).values("status", "start_date", "end_date").first()
            if previous and previous["status"] == self.Status.APPROVED and self.status == self.Status.APPROVED:
                if previous["start_date"] != self.start_date or previous["end_date"] != self.end_date:
                    self.status = self.Status.PENDING
                    self.reviewed_by = None
                    self.reviewed_at = None
        super().save(*args, **kwargs)
