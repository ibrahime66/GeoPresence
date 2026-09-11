from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TenantModel


def attendance_photo_path(instance, filename):
    # Conservée uniquement pour la compatibilité de l'historique des migrations
    # (référencée par upload_to dans migrations/0002_*) — la photo obligatoire
    # au pointage a été retirée, plus aucun code actif ne l'appelle.
    d = instance.clock_date
    return f"organizations/{instance.tenant_id}/attendance-photos/{d:%Y}/{d:%m}/{d:%d}/{instance.id}.jpg"


class Attendance(TenantModel):
    """CDC §9. Le cœur fonctionnel de la plateforme."""

    class ClockType(models.TextChoices):
        ARRIVAL = "ARRIVAL", "Arrivée"
        BREAK_START = "BREAK_START", "Départ pause"
        BREAK_END = "BREAK_END", "Retour pause"
        DEPARTURE = "DEPARTURE", "Départ"

    class Status(models.TextChoices):
        ON_TIME = "ON_TIME", "À l'heure"
        LATE = "LATE", "Retard"
        EARLY_LEAVE = "EARLY_LEAVE", "Départ anticipé"
        OVERTIME = "OVERTIME", "Heures supplémentaires"
        OUT_OF_SCHEDULE = "OUT_OF_SCHEDULE", "Hors horaire"
        PENDING_VALIDATION = "PENDING_VALIDATION", "En attente de validation"
        MANUALLY_VALIDATED = "MANUALLY_VALIDATED", "Validé manuellement"
        REJECTED = "REJECTED", "Rejeté"

    class Mode(models.TextChoices):
        ONLINE = "ONLINE", "En ligne"
        OFFLINE = "OFFLINE", "Hors ligne"

    class Source(models.TextChoices):
        APP = "APP", "Application"
        # RM-QR-001 : pointage initié en scannant le QR imprimé d'une agence —
        # tracé séparément pour la transparence (l'Admin peut voir comment
        # chaque pointage est arrivé), mais soumis exactement aux mêmes
        # vérifications GPS que APP (cf. apps.attendance.services.clock).
        QR = "QR", "Code QR"

    employee = models.ForeignKey("employees.Employee", on_delete=models.PROTECT, related_name="attendances")
    agency = models.ForeignKey("agencies.Agency", on_delete=models.PROTECT, related_name="attendances")

    clock_type = models.CharField(max_length=15, choices=ClockType.choices)
    # Date de RATTACHEMENT du pointage (RM-HOR-004 : une équipe de nuit reste
    # rattachée au jour de début, même si le départ a lieu après minuit).
    clock_date = models.DateField()

    # RM-POINT-005/006 : l'heure serveur est la source de vérité pour tous les
    # calculs ; l'heure client n'est conservée qu'à titre indicatif/forensique.
    server_time = models.DateTimeField()
    client_time = models.DateTimeField(null=True, blank=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    gps_accuracy = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # CDC §8.6 : signalé par le client (API navigateur) — pas de détection
    # serveur indépendante possible à ce stade (limitation documentée).
    is_gps_mocked = models.BooleanField(default=False)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    device_type = models.CharField(max_length=20, blank=True)

    # CDC §10.2.4 : créneau d'horaire concerné par ce pointage — toujours
    # renseigné quand un horaire s'applique (même hors mode multi-créneaux,
    # où c'est simplement le seul créneau du jour). Permet à une organisation
    # "pointage multi-créneaux" (apps.tenants.org_settings) d'avoir plusieurs
    # arrivées/départs par jour, un par créneau (ex. enseignant à plusieurs
    # cours) — cf. apps.attendance.services._check_sequence.
    schedule_slot = models.ForeignKey(
        "schedules.ScheduleSlot", null=True, blank=True, on_delete=models.SET_NULL, related_name="attendances"
    )

    # Calculés par apps.attendance.services au moment de l'enregistrement.
    scheduled_time = models.DateTimeField(null=True, blank=True)
    late_minutes = models.PositiveIntegerField(null=True, blank=True)
    early_leave_minutes = models.PositiveIntegerField(null=True, blank=True)
    overtime_minutes = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices)
    mode = models.CharField(max_length=10, choices=Mode.choices, default=Mode.ONLINE)
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.APP)
    synced_at = models.DateTimeField(null=True, blank=True)

    is_validated = models.BooleanField(default=False)
    validated_by = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="attendances_validated"
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-server_time"]
        constraints = [
            # RM-POINT-004 : un seul pointage par employé/jour/type/créneau.
            # Filet de sécurité niveau base — le cas "schedule_slot NULL" (pas
            # d'horaire défini) reste couvert par apps.attendance.services.
            # _check_sequence, MySQL ne rejetant pas deux NULL comme doublons
            # dans un index unique.
            models.UniqueConstraint(
                fields=["tenant", "employee", "clock_date", "clock_type", "schedule_slot"],
                name="attendance_one_per_day_type_slot",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "employee", "clock_date"], name="attendance_emp_date_idx"),
            models.Index(fields=["tenant", "agency", "clock_date"], name="attendance_agency_date_idx"),
        ]

    def __str__(self):
        return f"{self.employee} — {self.get_clock_type_display()} {self.clock_date}"

    def clean(self):
        super().clean()
        if self.employee_id and self.employee.tenant_id != self.tenant_id:
            raise ValidationError("L'employé doit appartenir à la même organisation.")
        if self.agency_id and self.agency.tenant_id != self.tenant_id:
            raise ValidationError("L'agence doit appartenir à la même organisation.")
