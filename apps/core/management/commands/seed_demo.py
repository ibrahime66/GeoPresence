from datetime import date, time
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.absences.models import Absence
from apps.accounts.models import User
from apps.agencies.models import Agency
from apps.absences.models import AbsenceReason
from apps.attendance.models import Attendance
from apps.departments.models import Department
from apps.employees.models import Employee
from apps.leaves.models import Leave, LeaveType
from apps.schedules.models import Schedule, ScheduleSlot
from apps.tenants.models import Organization

DEMO_SLUG = "demo-corp"
PASSWORD = "Demo1234!"


class Command(BaseCommand):
    help = "Crée un jeu de données de démo complet (organisation, agence, horaire, comptes) pour tester l'application manuellement. Supprime et recrée toute donnée de démo existante (slug 'demo-corp')."

    def handle(self, *args, **options):
        # Ordre important : les employés protègent (PROTECT) agences/départements/
        # horaires contre la suppression tant qu'ils existent — il faut donc
        # supprimer tout ce qui référence un Employee avant l'Organization elle-même.
        existing = Organization.objects.filter(slug=DEMO_SLUG).first()
        if existing:
            Attendance.objects.all_tenants().filter(tenant=existing).delete()
            Leave.objects.all_tenants().filter(tenant=existing).delete()
            Absence.objects.all_tenants().filter(tenant=existing).delete()
            Employee.objects.all_tenants().filter(tenant=existing).delete()
            User.objects.filter(tenant=existing).delete()
            existing.delete()

        org = Organization.objects.create(
            legal_name="Demo Corp SARL",
            display_name="Demo Corp",
            slug=DEMO_SLUG,
            country="France",
            city="Paris",
            email="contact@demo-corp.local",
        )

        # Tour Eiffel — repère facile à retrouver si tu veux forcer ta position
        # GPS dans les DevTools du navigateur (More tools > Sensors > Location).
        agency = Agency.objects.create(
            tenant=org, name="Siège Demo", code="HQ", city="Paris", country="France",
            latitude=Decimal("48.8583701"), longitude=Decimal("2.2944813"), radius_meters=200,
        )

        dept = Department.objects.create(tenant=org, name="Opérations")

        # Horaire volontairement très large (n'importe quelle heure de la
        # journée est acceptée) pour pouvoir tester le pointage à tout moment,
        # contrairement à un horaire réaliste 8h-17h.
        schedule = Schedule.objects.create(tenant=org, name="Horaire démo (large)", schedule_type=Schedule.ScheduleType.FIXED)
        for weekday in range(7):
            ScheduleSlot.objects.create(
                tenant=org, schedule=schedule, weekday=weekday,
                start_time=time(0, 0), end_time=time(23, 59),
                clock_in_window_before_minutes=60, clock_in_window_after_minutes=1439,
                clock_out_window_before_minutes=1439, clock_out_window_after_minutes=60,
            )
        dept.default_schedule = schedule
        dept.save(update_fields=["default_schedule"])

        paid_leave = LeaveType.objects.create(tenant=org, name="Congé annuel payé", deducts_from_balance=True)
        LeaveType.objects.create(tenant=org, name="Congé sans solde", deducts_from_balance=False)
        AbsenceReason.objects.create(tenant=org, name="Maladie", requires_certificate=True)
        AbsenceReason.objects.create(tenant=org, name="Autre")

        admin_user = User.objects.create_user(
            email="admin@demo.local", password=PASSWORD, tenant=org, role=User.Role.ADMIN,
            must_change_password=False, first_name="Alice", last_name="Admin",
        )
        manager_user = User.objects.create_user(
            email="manager@demo.local", password=PASSWORD, tenant=org, role=User.Role.MANAGER,
            must_change_password=False, first_name="Marc", last_name="Manager",
        )
        employee_user = User.objects.create_user(
            email="employee@demo.local", password=PASSWORD, tenant=org, role=User.Role.EMPLOYEE,
            must_change_password=False, first_name="Emma", last_name="Employée",
        )

        Employee.objects.create(
            tenant=org, user=manager_user, department=dept, primary_agency=agency,
            hire_date=date(2022, 1, 1), annual_leave_days=Decimal("25"),
        )
        Employee.objects.create(
            tenant=org, user=employee_user, department=dept, primary_agency=agency,
            hire_date=date(2023, 1, 1), annual_leave_days=Decimal("25"), manager=manager_user,
        )

        self.stdout.write(self.style.SUCCESS("\nDonnées de démo créées.\n"))
        self.stdout.write(f"Organisation : {org.display_name} ({org.slug})")
        self.stdout.write(f"Agence       : {agency.name} — lat {agency.latitude}, lon {agency.longitude}, rayon {agency.radius_meters} m\n")
        self.stdout.write("Comptes (mot de passe identique pour les trois) :")
        self.stdout.write(f"  Admin    : admin@demo.local    / {PASSWORD}")
        self.stdout.write(f"  Manager  : manager@demo.local  / {PASSWORD}")
        self.stdout.write(f"  Employé  : employee@demo.local / {PASSWORD}  (géré par manager@demo.local)")
        self.stdout.write("\nConnecte-toi sur http://127.0.0.1:8000/accounts/login/")
