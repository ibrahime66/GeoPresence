from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TenantModel


class Department(TenantModel):
    """CDC §3.2.2. Structure organisationnelle simple pour l'instant (nom,
    code, statut) — suffisant pour affecter employés et postes."""

    name = models.CharField("nom", max_length=255)
    code = models.CharField("code", max_length=20, blank=True)
    description = models.TextField("description", blank=True)
    is_active = models.BooleanField("actif", default=True)

    # CDC §10.3 : horaire par défaut du département — niveau de priorité 3.
    default_schedule = models.ForeignKey(
        "schedules.Schedule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departments",
        verbose_name="horaire par défaut",
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "name"], name="departments_department_tenant_name_uniq"),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.default_schedule_id and self.default_schedule.tenant_id != self.tenant_id:
            raise ValidationError("L'horaire par défaut doit appartenir à la même organisation.")


class Position(TenantModel):
    """CDC §3.2.2 / §10.3 : horaire par défaut du poste — niveau de priorité 2."""

    title = models.CharField("intitulé", max_length=255)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="positions", verbose_name="département"
    )
    description = models.TextField("description", blank=True)
    is_active = models.BooleanField("actif", default=True)

    default_schedule = models.ForeignKey(
        "schedules.Schedule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="positions",
        verbose_name="horaire par défaut",
    )

    class Meta:
        ordering = ["title"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "title"], name="departments_position_tenant_title_uniq"),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.department_id and self.department.tenant_id != self.tenant_id:
            raise ValidationError("Le département d'un poste doit appartenir à la même organisation.")
        if self.default_schedule_id and self.default_schedule.tenant_id != self.tenant_id:
            raise ValidationError("L'horaire par défaut doit appartenir à la même organisation.")
