from django.db.models import Q
from django.utils import timezone

from .models import EmployeeScheduleAssignment


def get_effective_schedule(employee, on_date=None):
    """CDC §10.3 : hiérarchie de priorité employé > poste > département > agence.
    RM-HOR-002 : cet ordre est figé, pas configurable par organisation.

    Utilise `all_tenants()` explicitement plutôt que le manager par défaut :
    cette fonction doit rester correcte même appelée hors d'une requête HTTP
    (tâche Celery de détection d'absences, par ex.) où le contexte thread-local
    du TenantMiddleware n'existe pas."""
    on_date = on_date or timezone.localdate()

    assignment = (
        EmployeeScheduleAssignment.objects.all_tenants()
        .filter(employee_id=employee.id, valid_from__lte=on_date)
        .filter(Q(valid_until__isnull=True) | Q(valid_until__gte=on_date))
        .order_by("-valid_from")
        .first()
    )
    if assignment:
        return assignment.schedule

    if employee.position_id and employee.position.default_schedule_id:
        return employee.position.default_schedule
    if employee.department_id and employee.department.default_schedule_id:
        return employee.department.default_schedule
    if employee.primary_agency_id and employee.primary_agency.default_schedule_id:
        return employee.primary_agency.default_schedule

    return None
