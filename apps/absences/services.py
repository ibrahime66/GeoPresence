from django.utils import timezone

from apps.attendance.models import Attendance

from .models import Absence


class AbsenceRejected(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(message)


class AbsenceCancelled(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(message)


def submit_justification(employee, date, reason=None, comment="", custom_reason=""):
    """CDC §12.1.2. Fonctionne aussi bien pour justifier une absence détectée
    au préalable (get_or_create) que pour une absence signalée directement
    par l'employé sans détection automatique préalable."""
    if Attendance.objects.all_tenants().filter(
        employee=employee, clock_date=date, clock_type=Attendance.ClockType.ARRIVAL
    ).exists():
        # Une arrivée pointée ce jour-là signifie que l'employé était
        # présent — sans ce contrôle, un employé pouvait faire approuver une
        # "absence justifiée" pour un jour où il a réellement travaillé,
        # créant une incohérence entre pointage et absence dans son dossier.
        raise AbsenceRejected(
            "Un pointage d'arrivée existe pour cette date — vous n'étiez pas absent(e) ce jour-là.",
            "attendance_exists",
        )

    absence, _ = Absence.objects.all_tenants().get_or_create(
        tenant=employee.tenant,
        employee=employee,
        date=date,
        defaults={"status": Absence.Status.PENDING_REVIEW},
    )
    if absence.status == Absence.Status.JUSTIFIED:
        raise AbsenceRejected("Cette absence est déjà justifiée.", "already_justified")

    absence.reason = reason
    absence.custom_reason = custom_reason
    absence.employee_comment = comment
    absence.status = Absence.Status.PENDING_REVIEW
    absence.full_clean()
    absence.save()
    return absence


def cancel_justification(absence):
    """Retire un justificatif encore en attente de validation (erreur de
    saisie, pièce jointe erronée...) — l'absence redevient non justifiée et
    peut être resoumise via `submit_justification`."""
    if absence.status != Absence.Status.PENDING_REVIEW:
        raise AbsenceCancelled("Seul un justificatif en attente peut être annulé.", "invalid_state")
    absence.status = Absence.Status.UNJUSTIFIED
    absence.save(update_fields=["status"])
    return absence


def review_absence(absence, reviewer, approve, comment=""):
    if absence.status != Absence.Status.PENDING_REVIEW:
        raise AbsenceRejected("Seule une absence en attente de validation peut être traitée.", "invalid_state")
    absence.status = Absence.Status.JUSTIFIED if approve else Absence.Status.REJECTED
    absence.reviewer_comment = comment
    absence.reviewed_by = reviewer
    absence.reviewed_at = timezone.now()
    absence.save(update_fields=["status", "reviewer_comment", "reviewed_by", "reviewed_at"])
    return absence
