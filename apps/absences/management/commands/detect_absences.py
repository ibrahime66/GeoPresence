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
        parser.add_argument("--date", help="Date à analyser (AAAA-MM-JJ). Par défaut : hier.")

    def handle(self, *args, **options):
        if options.get("date"):
            target_date = parse_date(options["date"])
            if target_date is None:
                raise CommandError("Date invalide — format attendu AAAA-MM-JJ.")
        else:
            target_date = timezone.localdate() - timedelta(days=1)

        holiday_cache = {}
        created_count = 0

        employees = (
            Employee.objects.all_tenants()
            .filter(status=Employee.Status.ACTIVE)
            .select_related("user", "tenant", "manager")
        )
        for employee in employees:
            if target_date in self._holidays_for(employee.tenant_id, target_date, holiday_cache):
                continue

            schedule = get_effective_schedule(employee, on_date=target_date)
            if schedule is None:
                continue
            if not schedule.slots_for_weekday(target_date.weekday()).exists():
                continue

            if self._on_approved_leave(employee, target_date):
                continue
            if self._has_arrival(employee, target_date):
                continue

            absence, was_created = Absence.objects.all_tenants().get_or_create(
                tenant=employee.tenant,
                employee=employee,
                date=target_date,
                defaults={"status": Absence.Status.UNJUSTIFIED, "is_auto_detected": True},
            )
            if was_created:
                created_count += 1
                self._notify(absence)

        self.stdout.write(self.style.SUCCESS(f"{created_count} absence(s) détectée(s) pour le {target_date}."))

    @staticmethod
    def _holidays_for(tenant_id, target_date, cache):
        if tenant_id not in cache:
            cache[tenant_id] = get_holiday_dates(tenant_id, target_date, target_date)
        return cache[tenant_id]

    @staticmethod
    def _on_approved_leave(employee, target_date):
        return Leave.objects.all_tenants().filter(
            employee=employee, status=Leave.Status.APPROVED, start_date__lte=target_date, end_date__gte=target_date
        ).exists()

    @staticmethod
    def _has_arrival(employee, target_date):
        return Attendance.objects.all_tenants().filter(
            employee=employee, clock_date=target_date, clock_type=Attendance.ClockType.ARRIVAL
        ).exists()

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
