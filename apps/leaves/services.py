from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.employees.models import Employee

from .models import Holiday, Leave


class LeaveRejected(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(message)


def get_holiday_dates(tenant_id, start_date, end_date):
    """CDC §12.4 : jours fériés récurrents (mois/jour fixe, année ignorée) ou ponctuels."""
    dates = set()
    for holiday in Holiday.objects.all_tenants().filter(tenant_id=tenant_id):
        if holiday.is_recurring:
            for year in range(start_date.year, end_date.year + 1):
                try:
                    d = holiday.date.replace(year=year)
                except ValueError:
                    continue  # 29 février sur une année non bissextile.
                if start_date <= d <= end_date:
                    dates.add(d)
        elif start_date <= holiday.date <= end_date:
            dates.add(holiday.date)
    return dates


def compute_working_days(tenant, start_date, end_date):
    """RM-CONGE-002 : jours fériés et jours de repos hebdomadaires (réglage
    `rest_weekdays` par organisation, apps.tenants.org_settings — samedi/dimanche
    par défaut) exclus du décompte."""
    from apps.tenants.org_settings import get_org_setting

    holidays = get_holiday_dates(tenant.id if tenant is not None else None, start_date, end_date)
    rest_weekdays = set(get_org_setting(tenant, "rest_weekdays"))
    count = 0
    d = start_date
    while d <= end_date:
        if d.weekday() not in rest_weekdays and d not in holidays:
            count += 1
        d += timedelta(days=1)
    return Decimal(count)


def _has_overlap(employee, start_date, end_date, exclude_pk=None):
    qs = Leave.objects.all_tenants().filter(
        employee=employee,
        status__in=[Leave.Status.PENDING, Leave.Status.APPROVED],
        start_date__lte=end_date,
        end_date__gte=start_date,
    )
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    return qs.exists()


def submit_leave(employee, leave_type, start_date, end_date, comment="", now=None):
    now = now or timezone.now()

    if end_date < start_date:
        raise LeaveRejected("La date de fin doit être postérieure ou égale à la date de début.", "invalid_dates")

    if _has_overlap(employee, start_date, end_date):
        raise LeaveRejected("Chevauchement avec une demande de congé existante.", "overlap")

    working_days = compute_working_days(employee.tenant, start_date, end_date)
    if working_days <= 0:
        raise LeaveRejected("La période sélectionnée ne contient aucun jour ouvrable.", "no_working_days")

    if leave_type.deducts_from_balance and working_days > employee.leave_balance:
        raise LeaveRejected(
            f"Solde insuffisant ({employee.leave_balance} j disponibles, {working_days} j demandés).",
            "insufficient_balance",
        )

    leave = Leave(
        tenant=employee.tenant,
        employee=employee,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        working_days=working_days,
        employee_comment=comment,
        status=Leave.Status.PENDING,
    )
    leave.full_clean()
    leave.save()
    return leave


def approve_leave(leave, reviewer, comment=""):
    if leave.status != Leave.Status.PENDING:
        raise LeaveRejected("Seule une demande en attente peut être approuvée.", "invalid_state")
    with transaction.atomic():
        if leave.leave_type.deducts_from_balance:
            # Verrou de ligne (SELECT ... FOR UPDATE), pas seulement une
            # lecture : deux approbations concurrentes pour le même employé
            # (deux demandes sans chevauchement de dates) doivent s'exécuter
            # en séquence, sinon les deux liraient le même solde encore
            # disponible et le feraient passer sous zéro toutes les deux —
            # une simple vérification sans verrou laisse cette fenêtre ouverte.
            current_balance = Employee.objects.all_tenants().select_for_update().filter(
                pk=leave.employee_id
            ).values_list("leave_balance", flat=True).first()
            if leave.working_days > current_balance:
                raise LeaveRejected(
                    f"Solde insuffisant pour approuver cette demande ({current_balance} j disponibles, "
                    f"{leave.working_days} j demandés) — une autre demande a probablement été approuvée depuis.",
                    "insufficient_balance",
                )
        leave.status = Leave.Status.APPROVED
        leave.reviewer_comment = comment
        leave.reviewed_by = reviewer
        leave.reviewed_at = timezone.now()
        leave.save(update_fields=["status", "reviewer_comment", "reviewed_by", "reviewed_at"])
        if leave.leave_type.deducts_from_balance:
            Employee.objects.all_tenants().filter(pk=leave.employee_id).update(
                leave_balance=F("leave_balance") - leave.working_days
            )
    return leave


def reject_leave(leave, reviewer, comment=""):
    if leave.status != Leave.Status.PENDING:
        raise LeaveRejected("Seule une demande en attente peut être rejetée.", "invalid_state")
    leave.status = Leave.Status.REJECTED
    leave.reviewer_comment = comment
    leave.reviewed_by = reviewer
    leave.reviewed_at = timezone.now()
    leave.save(update_fields=["status", "reviewer_comment", "reviewed_by", "reviewed_at"])
    return leave


def cancel_leave(leave):
    """RM-CONGE-004 : l'annulation d'un congé déjà approuvé restitue le solde."""
    if leave.status not in (Leave.Status.PENDING, Leave.Status.APPROVED):
        raise LeaveRejected("Cette demande ne peut plus être annulée.", "invalid_state")
    was_approved = leave.status == Leave.Status.APPROVED
    leave.status = Leave.Status.CANCELLED
    leave.save(update_fields=["status"])
    if was_approved and leave.leave_type.deducts_from_balance:
        Employee.objects.all_tenants().filter(pk=leave.employee_id).update(
            leave_balance=F("leave_balance") + leave.working_days
        )
    return leave
