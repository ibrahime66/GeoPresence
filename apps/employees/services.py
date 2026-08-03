from .models import Employee


def get_active_employee(user):
    """Profil employé actif lié à ce compte, ou None. Utilisé par tous les
    modules qui exposent des vues en self-service (pointage, congés, absences)."""
    employee = getattr(user, "employee_profile", None)
    if employee is None or employee.status != Employee.Status.ACTIVE:
        return None
    return employee


def sync_user_active_state(employee):
    """L'accès à la connexion suit le statut RH (CDC §11.4) : Actif et En congé
    peuvent se connecter, Suspendu et Archivé non — appelé après toute
    modification de `employee.status`. Suspendre/archiver révoque aussi
    immédiatement toutes les sessions déjà ouvertes (CDC §5.6.2) : sans ça,
    un employé désactivé resterait connecté sur les appareils où il l'était déjà."""
    from apps.accounts.sessions import revoke_all_sessions

    should_be_active = employee.status in (Employee.Status.ACTIVE, Employee.Status.ON_LEAVE)
    was_active = employee.user.is_active
    if was_active != should_be_active:
        employee.user.is_active = should_be_active
        employee.user.save(update_fields=["is_active"])
    if was_active and not should_be_active:
        revoke_all_sessions(employee.user)
