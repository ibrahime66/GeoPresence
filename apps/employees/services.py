from .models import Employee


def get_active_employee(user):
    """Profil employé actif lié à ce compte, ou None. Utilisé par tous les
    modules qui exposent des vues en self-service (pointage, congés, absences)."""
    employee = getattr(user, "employee_profile", None)
    if employee is None or employee.status != Employee.Status.ACTIVE:
        return None
    return employee
