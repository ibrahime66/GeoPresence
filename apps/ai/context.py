"""CDC §15.4 : "le contexte envoyé à l'IA est strictement limité aux données
nécessaires à la réponse" — ce module construit, pour chaque rôle, un résumé
agrégé et déjà scopé au tenant courant (jamais une requête libre sur la base).
Aucune fonction ici ne prend de tenant en paramètre explicite pour les rôles
non-Super Admin : elle est toujours dérivée de `user`, pour qu'il soit
impossible d'appeler ce module avec le tenant d'un autre utilisateur par erreur."""

from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone

from apps.absences.models import Absence
from apps.attendance.models import Attendance
from apps.employees.models import Employee
from apps.employees.services import get_active_employee
from apps.leaves.models import Leave
from apps.tenants.models import Organization

# Les suggestions générées par le modèle (cf. apps.ai.services) portent
# parfois sur "comment faire X dans l'appli" plutôt que sur des chiffres —
# sans ce mini-guide, GeoIA propose ces questions puis répond "je ne sais
# pas", ce qui n'a aucun sens pour l'utilisateur. Chemins de menu exacts,
# à tenir à jour si la navigation change.
APP_HELP_FAQ = (
    "Aide sur l'utilisation de GeoPresence (aide-toi de ceci pour les "
    "questions sur COMMENT faire quelque chose dans l'application, en plus "
    "des données ci-dessus) :\n"
    "- Pointer son arrivée/départ : menu « Pointer », autoriser la "
    "géolocalisation, puis appuyer sur le bouton d'arrivée ou de départ affiché.\n"
    "- Demander un congé : menu « Mes congés » > carte « Nouvelle demande » > "
    "remplir le formulaire > bouton « Soumettre ». La demande part ensuite à "
    "son manager pour validation.\n"
    "- Justifier une absence : menu « Mes absences » > carte « Justifier une "
    "absence » > remplir le formulaire > bouton « Soumettre ».\n"
    "- Consulter son solde de congés : visible sur le tableau de bord et "
    "dans « Mes congés ».\n"
    "- Changer sa langue d'affichage : menu « Mon profil » > « Langue d'affichage ».\n"
    "- Voir ou révoquer ses sessions actives : menu « Mon profil » > « Sessions actives »."
)


def _presence_rate(tenant, date, total_employees):
    if total_employees == 0:
        return 0.0
    present = (
        Attendance.objects.all_tenants()
        .filter(tenant=tenant, clock_date=date, clock_type=Attendance.ClockType.ARRIVAL)
        .values("employee_id")
        .distinct()
        .count()
    )
    return round(present / total_employees * 100, 1)


def build_employee_context(user):
    employee = get_active_employee(user)
    if employee is None:
        return "Aucune fiche employé active associée à cet utilisateur."

    today = timezone.localdate()
    month_start = today.replace(day=1)
    month_arrivals = Attendance.objects.all_tenants().filter(
        employee=employee, clock_date__gte=month_start, clock_type=Attendance.ClockType.ARRIVAL
    )
    last = Attendance.objects.all_tenants().filter(employee=employee).order_by("-server_time").first()

    return (
        f"Employé : {user.full_name or user.email}.\n"
        f"Solde de congés : {employee.leave_balance} jours.\n"
        f"Ce mois-ci : {month_arrivals.values('clock_date').distinct().count()} jours présents, "
        f"{month_arrivals.filter(status=Attendance.Status.LATE).count()} retards.\n"
        f"Demandes en attente : {Leave.objects.all_tenants().filter(employee=employee, status=Leave.Status.PENDING).count()} congé(s), "
        f"{Absence.objects.all_tenants().filter(employee=employee, status=Absence.Status.PENDING_REVIEW).count()} justificatif(s).\n"
        f"Dernier pointage : {last.server_time.strftime('%d/%m/%Y %H:%M') if last else 'aucun'}."
    )


def build_manager_context(user):
    today = timezone.localdate()
    team_qs = Employee.objects.all_tenants().filter(
        tenant=user.tenant, status=Employee.Status.ACTIVE, manager=user,
    )
    team_ids = list(team_qs.values_list("id", flat=True))
    total_team = len(team_ids)

    today_arrivals = Attendance.objects.all_tenants().filter(
        employee_id__in=team_ids, clock_date=today, clock_type=Attendance.ClockType.ARRIVAL
    )
    present_today = today_arrivals.count()
    late_today = today_arrivals.filter(status=Attendance.Status.LATE).count()

    return (
        f"Équipe de {user.full_name or user.email} : {total_team} employé(s).\n"
        f"Aujourd'hui : {present_today} présent(s), {max(total_team - present_today, 0)} absent(s), {late_today} retard(s).\n"
        f"Demandes en attente : "
        f"{Leave.objects.all_tenants().filter(tenant=user.tenant, employee_id__in=team_ids, status=Leave.Status.PENDING).count()} congé(s), "
        f"{Absence.objects.all_tenants().filter(tenant=user.tenant, employee_id__in=team_ids, status=Absence.Status.PENDING_REVIEW).count()} justificatif(s)."
    )


def build_admin_context(user):
    tenant = user.tenant
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)
    month_start = today.replace(day=1)

    total_employees = Employee.objects.all_tenants().filter(tenant=tenant, status=Employee.Status.ACTIVE).count()
    present_today = (
        Attendance.objects.all_tenants()
        .filter(tenant=tenant, clock_date=today, clock_type=Attendance.ClockType.ARRIVAL)
        .values("employee_id").distinct().count()
    )
    late_today = Attendance.objects.all_tenants().filter(
        tenant=tenant, clock_date=today, clock_type=Attendance.ClockType.ARRIVAL, status=Attendance.Status.LATE
    ).count()

    late_ranking = (
        Attendance.objects.all_tenants()
        .filter(
            tenant=tenant, clock_type=Attendance.ClockType.ARRIVAL, status=Attendance.Status.LATE,
            clock_date__gte=month_start,
        )
        .values("employee__user__first_name", "employee__user__last_name")
        .annotate(total_late=Sum("late_minutes"), occurrences=Count("id"))
        .order_by("-total_late")[:5]
    )
    ranking_text = ", ".join(
        f"{r['employee__user__first_name']} {r['employee__user__last_name']} ({r['occurrences']} retards)"
        for r in late_ranking
    ) or "aucun"

    return (
        f"Organisation : {tenant.display_name}.\n"
        f"{total_employees} employé(s) actif(s).\n"
        f"Aujourd'hui : taux de présence {_presence_rate(tenant, today, total_employees)}% "
        f"(hier : {_presence_rate(tenant, yesterday, total_employees)}%), {late_today} retard(s).\n"
        f"Demandes en attente : "
        f"{Leave.objects.all_tenants().filter(tenant=tenant, status=Leave.Status.PENDING).count()} congé(s), "
        f"{Absence.objects.all_tenants().filter(tenant=tenant, status=Absence.Status.PENDING_REVIEW).count()} justificatif(s).\n"
        f"Top retardataires ce mois : {ranking_text}."
    )


def build_super_admin_context():
    """CDC §15.3.3 : le Super Admin ne voit que des agrégats plateforme,
    jamais le détail opérationnel d'un tenant (cf. apps.superadmin.views)."""
    today = timezone.localdate()
    return (
        f"Plateforme GeoPresence — vue globale.\n"
        f"Organisations : {Organization.objects.filter(status=Organization.Status.ACTIVE).count()} active(s), "
        f"{Organization.objects.filter(status=Organization.Status.SUSPENDED).count()} suspendue(s) sur "
        f"{Organization.objects.count()} au total.\n"
        f"Pointages aujourd'hui (toutes organisations) : "
        f"{Attendance.objects.all_tenants().filter(clock_date=today).count()}."
    )


def build_context(user):
    """Point d'entrée unique — renvoie le texte de contexte (données du rôle
    + aide de navigation, cf. APP_HELP_FAQ)."""
    if user.role == "SUPER_ADMIN":
        data = build_super_admin_context()
    elif user.role == "ADMIN":
        data = build_admin_context(user)
    elif user.role == "MANAGER":
        data = build_manager_context(user)
    else:
        data = build_employee_context(user)
    return f"{data}\n\n{APP_HELP_FAQ}"
