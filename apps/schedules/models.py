from datetime import date as date_cls

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TenantModel


class Weekday(models.IntegerChoices):
    MONDAY = 0, "Lundi"
    TUESDAY = 1, "Mardi"
    WEDNESDAY = 2, "Mercredi"
    THURSDAY = 3, "Jeudi"
    FRIDAY = 4, "Vendredi"
    SATURDAY = 5, "Samedi"
    SUNDAY = 6, "Dimanche"


class Schedule(TenantModel):
    """CDC §10.2. Les 4 types (fixe, équipe, personnalisé, enseignant) partagent
    la même structure de créneaux hebdomadaires (ScheduleSlot) — seul le type
    change la façon dont l'horaire est affecté et interprété, pas sa forme.

    La rotation effective des équipes (qui travaille quelle semaine) relève du
    futur module Emplois du temps (CDC §10.2.2) : ici, une équipe "Nuit" est un
    Schedule comme un autre, affecté via EmployeeScheduleAssignment."""

    class ScheduleType(models.TextChoices):
        FIXED = "FIXED", "Horaire fixe"
        TEAM = "TEAM", "Équipe (rotation)"
        CUSTOM = "CUSTOM", "Personnalisé"
        TEACHER = "TEACHER", "Enseignant"

    name = models.CharField("nom", max_length=255)
    schedule_type = models.CharField(
        "type d'horaire", max_length=10, choices=ScheduleType.choices, default=ScheduleType.FIXED
    )
    is_active = models.BooleanField("actif", default=True)

    # Surchargent les paramètres par défaut de l'organisation si renseignés (CDC §10.2.1).
    late_tolerance_minutes = models.PositiveSmallIntegerField(
        "tolérance de retard (min)", null=True, blank=True
    )
    early_leave_tolerance_minutes = models.PositiveSmallIntegerField(
        "tolérance de départ anticipé (min)", null=True, blank=True
    )
    overtime_threshold_minutes = models.PositiveSmallIntegerField(
        "seuil d'heures supplémentaires (min)", null=True, blank=True
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "name"], name="schedules_schedule_tenant_name_uniq"),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_schedule_type_display()})"

    def slots_for_weekday(self, weekday):
        return self.slots.filter(weekday=weekday, is_cancelled=False).order_by("start_time")


class ScheduleSlot(TenantModel):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="slots", verbose_name="horaire")
    weekday = models.IntegerField("jour de la semaine", choices=Weekday.choices)
    start_time = models.TimeField("heure de début")
    end_time = models.TimeField("heure de fin")
    break_start_time = models.TimeField("début de pause", null=True, blank=True)
    break_end_time = models.TimeField("fin de pause", null=True, blank=True)

    # Fenêtres de pointage : minutes avant/après l'heure officielle où le
    # pointage est accepté (CDC §10.2.1).
    clock_in_window_before_minutes = models.PositiveSmallIntegerField(
        "fenêtre d'arrivée avant (min)", default=30
    )
    clock_in_window_after_minutes = models.PositiveSmallIntegerField(
        "fenêtre d'arrivée après (min)", default=120
    )
    clock_out_window_before_minutes = models.PositiveSmallIntegerField(
        "fenêtre de départ avant (min)", default=30
    )
    clock_out_window_after_minutes = models.PositiveSmallIntegerField(
        "fenêtre de départ après (min)", default=180
    )

    is_cancelled = models.BooleanField("annulé", default=False)

    class Meta:
        ordering = ["weekday", "start_time"]

    def __str__(self):
        return f"{self.get_weekday_display()} {self.start_time}–{self.end_time}"

    @property
    def is_overnight(self):
        """RM-HOR-004 : un créneau chevauchant minuit (ex. équipe de nuit
        22h→06h) reste rattaché au jour de DÉBUT (`weekday`), jamais au
        lendemain — c'est cette propriété qui signale ce cas au module Pointage."""
        return self.end_time <= self.start_time

    def clean(self):
        super().clean()
        if self.schedule_id and self.tenant_id and self.schedule.tenant_id != self.tenant_id:
            raise ValidationError("Le créneau doit appartenir à la même organisation que l'horaire.")
        if bool(self.break_start_time) != bool(self.break_end_time):
            raise ValidationError("La pause doit avoir une heure de début ET de fin, ou aucune des deux.")
        if self.break_start_time and self.break_end_time and self.break_start_time >= self.break_end_time:
            raise ValidationError("L'heure de fin de pause doit être postérieure à l'heure de début.")


class EmployeeScheduleAssignment(TenantModel):
    """CDC §10.4 : historique complet des horaires d'un employé. Niveau de
    priorité 1 (le plus fort) dans la hiérarchie CDC §10.3."""

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="schedule_assignments", verbose_name="employé"
    )
    schedule = models.ForeignKey(
        Schedule, on_delete=models.PROTECT, related_name="employee_assignments", verbose_name="horaire"
    )
    valid_from = models.DateField("valide à partir du")
    valid_until = models.DateField("valide jusqu'au", null=True, blank=True)

    class Meta:
        ordering = ["-valid_from"]

    def __str__(self):
        return f"{self.employee} → {self.schedule} (dès {self.valid_from})"

    def clean(self):
        super().clean()
        if self.employee_id and self.employee.tenant_id != self.tenant_id:
            raise ValidationError("L'employé doit appartenir à la même organisation.")
        if self.schedule_id and self.schedule.tenant_id != self.tenant_id:
            raise ValidationError("L'horaire doit appartenir à la même organisation.")
        if self.valid_until and self.valid_from and self.valid_until < self.valid_from:
            raise ValidationError("La date de fin doit être postérieure ou égale à la date de début.")

        if self.employee_id and self.valid_from:
            self_end = self.valid_until or date_cls.max
            existing = EmployeeScheduleAssignment.objects.all_tenants().filter(employee_id=self.employee_id)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            for other in existing:
                other_end = other.valid_until or date_cls.max
                if self.valid_from <= other_end and other.valid_from <= self_end:
                    raise ValidationError(
                        "Chevauchement avec une affectation existante "
                        f"({other.valid_from} → {other.valid_until or '∞'})."
                    )
