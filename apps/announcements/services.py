from django.db.models import Q
from django.utils import timezone

from .models import Announcement


def active_announcements_for_employee(employee, now=None):
    """CDC §16.4 : annonces actuellement publiées, non expirées, et ciblées
    sur cet employé (ou sans ciblage du tout = tout le monde) — cf.
    apps.announcements.models.Announcement pour la règle de ciblage."""
    now = now or timezone.now()

    untargeted = Q(agencies__isnull=True, departments__isnull=True, employees__isnull=True)
    targeted = Q(employees=employee)
    if employee.primary_agency_id:
        targeted |= Q(agencies=employee.primary_agency_id)
    if employee.department_id:
        targeted |= Q(departments=employee.department_id)

    return (
        Announcement.objects.all_tenants()
        .filter(tenant=employee.tenant, publish_at__lte=now)
        .filter(Q(expire_at__isnull=True) | Q(expire_at__gt=now))
        .filter(untargeted | targeted)
        .distinct()
        .order_by("-publish_at")
    )
