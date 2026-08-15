from datetime import timedelta

from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_date

from apps.absences.models import Absence
from apps.accounts.models import User
from apps.attendance.models import Attendance
from apps.employees.models import Employee
from apps.leaves.models import Leave
from apps.leaves.services import get_holiday_dates
from apps.schedules.services import get_effective_schedule
from apps.tenants.models import Organization
from apps.tenants.org_settings import get_org_setting


class Command(BaseCommand):
    """CDC §12.1.1 : détection automatique des absences non justifiées.

    Aucune tâche planifiée (Celery/Redis absents du projet, cf.
    requirements/production.txt) n'exécute encore cette commande
    automatiquement — à brancher sur un cron système ou Celery Beat quand
    l'infrastructure sera en place :
        0 6 * * *  cd /app && python manage.py detect_absences
    En attendant, elle s'exécute manuellement ou via une tâche cron simple.
    """

    help = "Détecte les employés attendus un jour donné (hier par défaut) sans pointage d'arrivée."

    def add_arguments(self, parser):
        parser.add_argument("--date", help="Date à analyser (AAAA-MM-JJ). Par défaut : hier (fuseau de chaque organisation).")

    def handle(self, *args, **options):
        explicit_date = None
        if options.get("date"):
            explicit_date = parse_date(options["date"])
            if explicit_date is None:
                raise CommandError("Date invalide — format attendu AAAA-MM-JJ.")

        holiday_cache = {}
        created_count = 0

        tenants = Organization.objects.filter(status=Organization.Status.ACTIVE)
        for tenant in tenants:
            # RM-HOR (fuseau horaire) : "hier" doit être calculé dans le fuseau
            # de CHAQUE organisation, pas celui du serveur — cette commande ne
            # passe jamais par TenantMiddleware (pas de requête HTTP), donc le
            # fuseau doit être activé explicitement ici, tenant par tenant.
            timezone.activate(tenant.timezone)
            try:
                target_date = explicit_date or (timezone.localdate() - timedelta(days=1))
                multi_slot = get_org_setting(tenant, "multi_slot_attendance_enabled")

                if target_date in self._holidays_for(tenant.id, target_date, holiday_cache):
                    continue

                employees = (
                    Employee.objects.all_tenants()
                    .filter(tenant=tenant, status=Employee.Status.ACTIVE)
                    .select_related("user", "manager")
                )
                for employee in employees:
                    schedule = get_effective_schedule(employee, on_date=target_date)
                    if schedule is None:
                        continue
                    slots = list(schedule.slots_for_weekday(target_date.weekday()))
                    if not slots:
                        continue

                    if self._on_approved_leave(employee, target_date):
                        continue
                    if self._has_arrival(employee, target_date, slots, multi_slot):
                        continue

                    absence, was_created = Absence.objects.all_tenants().get_or_create(
                        tenant=tenant,
                        employee=employee,
                        date=target_date,
                        defaults={"status": Absence.Status.UNJUSTIFIED, "is_auto_detected": True},
                    )
                    if was_created:
                        created_count += 1
                        self._notify(absence)
            finally:
                timezone.deactivate()

        self.stdout.write(self.style.SUCCESS(f"{created_count} absence(s) détectée(s)."))

    @staticmethod
    def _holidays_for(tenant_id, target_date, cache):
        key = (tenant_id, target_date)
        if key not in cache:
            cache[key] = get_holiday_dates(tenant_id, target_date, target_date)
        return cache[key]

    @staticmethod
    def _on_approved_leave(employee, target_date):
        return Leave.objects.all_tenants().filter(
            employee=employee, status=Leave.Status.APPROVED, start_date__lte=target_date, end_date__gte=target_date
        ).exists()

    @staticmethod
    def _has_arrival(employee, target_date, slots, multi_slot):
        """CDC §10.2.4 : en mode multi-créneaux, un employé attendu sur
        plusieurs créneaux ce jour-là (ex. enseignant) doit être arrivé sur
        CHACUN pour ne pas être considéré absent — sans quoi une arrivée sur un
        seul créneau masquait un créneau entier manqué le même jour (Absence
        n'a qu'une granularité journalière, donc un seul créneau manqué génère
        une absence pour la journée entière, faute de pouvoir représenter
        « absent seulement l'après-midi »)."""
        arrivals = Attendance.objects.all_tenants().filter(
            employee=employee, clock_date=target_date, clock_type=Attendance.ClockType.ARRIVAL
        )
        if not multi_slot:
            return arrivals.exists()
        arrived_slot_ids = set(arrivals.values_list("schedule_slot_id", flat=True))
        return all(slot.id in arrived_slot_ids for slot in slots)

    @staticmethod
    def _notify(absence):
        """CDC §12.1.1 : notification à l'employé, son manager et les
        Administrateurs de l'organisation."""
        employee_name = absence.employee.user.full_name or absence.employee.user.email
        recipients = [absence.employee.user.email]
        if absence.employee.manager_id and absence.employee.manager.email:
            recipients.append(absence.employee.manager.email)
        recipients.extend(
            User.objects.filter(tenant=absence.tenant, role=User.Role.ADMIN, is_active=True).values_list(
                "email", flat=True
            )
        )

        send_mail(
            subject=f"Absence détectée — {employee_name}",
            message=(
                f"Une absence a été détectée automatiquement pour {employee_name} le {absence.date:%d/%m/%Y} "
                "(aucun pointage d'arrivée enregistré alors qu'un horaire était planifié).\n\n"
                "L'employé peut justifier cette absence depuis son espace GeoPresence, rubrique « Mes absences »."
            ),
            from_email=None,
            recipient_list=list(dict.fromkeys(recipients)),
        )
