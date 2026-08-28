from datetime import datetime, timedelta

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


def unstaffed_slots_today(tenant, now=None):
    """Créneaux planifiés aujourd'hui dont la fenêtre d'arrivée est déjà
    écoulée sans qu'aucun pointage d'arrivée n'ait été enregistré — une
    "salle sans professeur", pas juste un retard (RM-ORG-SCHOOL, idée hors
    CDC proposée pour les écoles/universités). Réutilise get_effective_schedule
    (même hiérarchie de priorité que le reste de l'app) plutôt que de
    réinventer la résolution d'horaire.

    N'a de sens que pour une organisation avec school_scheduling_enabled —
    l'appelant est responsable de ce filtre (cf. apps.core.views._admin_context),
    cette fonction reste utilisable indépendamment si besoin."""
    from apps.attendance.models import Attendance
    from apps.employees.models import Employee

    now = now or timezone.now()
    today = timezone.localdate(now)
    weekday = today.weekday()

    alerts = []
    employees = (
        Employee.objects.all_tenants()
        .filter(tenant=tenant, status=Employee.Status.ACTIVE)
        .select_related("user")
    )
    for employee in employees:
        schedule = get_effective_schedule(employee, on_date=today)
        if schedule is None:
            continue
        for slot in schedule.slots_for_weekday(weekday):
            expected_dt = datetime.combine(today, slot.start_time)
            if timezone.is_naive(expected_dt):
                expected_dt = timezone.make_aware(expected_dt)
            grace_deadline = expected_dt + timedelta(minutes=slot.clock_in_window_after_minutes)
            if now < grace_deadline:
                continue
            has_arrival = Attendance.objects.all_tenants().filter(
                employee=employee, schedule_slot=slot, clock_date=today, clock_type=Attendance.ClockType.ARRIVAL
            ).exists()
            if not has_arrival:
                alerts.append({"employee": employee, "slot": slot, "expected": expected_dt})
    alerts.sort(key=lambda a: a["expected"])
    return alerts


def _time_ranges_overlap(start_a, end_a, start_b, end_b):
    """Chevauchement de deux plages horaires (heures, pas dates) — ne gère
    pas le cas d'un créneau à cheval sur minuit (is_overnight) : négligeable
    ici, un cours ne s'étend pas sur minuit en pratique."""
    return start_a < end_b and start_b < end_a


def available_substitutes(tenant, slot, on_date, exclude_employee_id=None):
    """RM-ORG-SCHOOL : pour un créneau donné, qui d'autre dans l'effectif est
    libre à ce moment précis aujourd'hui — collègues dont l'horaire du jour
    ne chevauche pas ce créneau. Une simple liste de référence pour la
    direction, pas une affectation automatique (cf. décision produit :
    l'humain choisit et prévient lui-même le remplaçant)."""
    from apps.employees.models import Employee

    weekday = on_date.weekday()
    candidates = []
    employees = (
        Employee.objects.all_tenants()
        .filter(tenant=tenant, status=Employee.Status.ACTIVE)
        .select_related("user")
    )
    for employee in employees:
        if exclude_employee_id and employee.id == exclude_employee_id:
            continue
        schedule = get_effective_schedule(employee, on_date=on_date)
        if schedule is None:
            candidates.append(employee)
            continue
        conflict = any(
            _time_ranges_overlap(s.start_time, s.end_time, slot.start_time, slot.end_time)
            for s in schedule.slots_for_weekday(weekday)
        )
        if not conflict:
            candidates.append(employee)
    return candidates


def room_day_planning(tenant, weekday):
    """RM-ORG-SCHOOL : occupation des salles pour un jour donné — une ligne
    par salle, les créneaux qui s'y déroulent avec matière / groupe /
    enseignant. Sert à repérer d'un coup d'œil les salles libres et les
    doubles réservations.

    Même résolution d'horaire que le reste du module (get_effective_schedule,
    hiérarchie CDC §10.3) : on part des employés actifs plutôt que des
    ScheduleSlot bruts, ce qui donne l'enseignant de chaque créneau sans
    jointure supplémentaire — et un créneau affecté à deux enseignants
    apparaît deux fois, ce qui EST le signal de conflit recherché.

    Renvoie (rooms, unroomed_count) :
      - rooms : liste de dicts {"room", "entries", "has_conflict"}, salles
        triées alpha, entries triées par heure de début. Chaque entrée :
        {"slot", "employee", "conflict"} (conflict = chevauche une autre
        entrée de la MÊME salle).
      - unroomed_count : nombre de créneaux du jour sans salle renseignée
        (juste une info : ils n'apparaissent nulle part dans la grille)."""
    from apps.employees.models import Employee

    by_room = {}
    unroomed_count = 0
    employees = (
        Employee.objects.all_tenants()
        .filter(tenant=tenant, status=Employee.Status.ACTIVE)
        .select_related("user")
    )
    for employee in employees:
        schedule = get_effective_schedule(employee)
        if schedule is None:
            continue
        for slot in schedule.slots_for_weekday(weekday):
            room = (slot.room or "").strip()
            if not room:
                unroomed_count += 1
                continue
            by_room.setdefault(room, []).append({"slot": slot, "employee": employee})

    rooms = []
    for room in sorted(by_room, key=str.casefold):
        entries = sorted(by_room[room], key=lambda e: e["slot"].start_time)
        for entry in entries:
            entry["conflict"] = False
        has_conflict = False
        for i, a in enumerate(entries):
            for b in entries[i + 1 :]:
                if _time_ranges_overlap(
                    a["slot"].start_time, a["slot"].end_time,
                    b["slot"].start_time, b["slot"].end_time,
                ):
                    a["conflict"] = b["conflict"] = has_conflict = True
        rooms.append({"room": room, "entries": entries, "has_conflict": has_conflict})
    return rooms, unroomed_count


def teacher_presence(tenant, on_date):
    """RM-ORG-SCHOOL : pour une date donnée, qui enseigne (ou devrait enseigner)
    quoi, où, et a-t-il pointé. Croise les créneaux "cours" prévus ce jour-là
    (créneaux avec matière OU salle OU groupe renseigné — ce qui écarte
    naturellement le personnel non-enseignant) avec les pointages du jour
    reliés à ces créneaux (Attendance.schedule_slot, déjà rempli par
    apps.attendance.services.resolve_slot au moment du pointage).

    Renvoie une liste d'entrées {employee, slot, arrival, departure,
    in_progress, clocked}, triée par heure de début puis salle. Une entrée
    par couple (enseignant, créneau) : soit prévue et pointée, soit prévue
    non pointée (arrival=None), soit pointée sur un créneau qui n'est plus
    dans l'horaire effectif de l'enseignant (planned absent, arrival présent).

    `in_progress` : arrivée pointée, pas encore de départ, on est aujourd'hui
    et l'heure de fin du créneau n'est pas dépassée — "l'enseignant est en
    classe en ce moment"."""
    from apps.attendance.models import Attendance
    from apps.employees.models import Employee

    weekday = on_date.weekday()

    # 1. Créneaux "cours" prévus ce jour-là, indexés par (employé, créneau).
    planned = {}
    employees = (
        Employee.objects.all_tenants()
        .filter(tenant=tenant, status=Employee.Status.ACTIVE)
        .select_related("user")
    )
    for employee in employees:
        schedule = get_effective_schedule(employee, on_date=on_date)
        if schedule is None:
            continue
        for slot in schedule.slots_for_weekday(weekday):
            if slot.subject or slot.room or slot.student_group:
                planned[(employee.id, slot.id)] = {"employee": employee, "slot": slot}

    # 2. Pointages du jour reliés à un créneau "cours".
    attendances = (
        Attendance.objects.all_tenants()
        .filter(tenant=tenant, clock_date=on_date, schedule_slot__isnull=False)
        .exclude(schedule_slot__subject="", schedule_slot__room="", schedule_slot__student_group="")
        .select_related("employee__user", "schedule_slot")
        .order_by("server_time")
    )
    clocked = {}
    for att in attendances:
        key = (att.employee_id, att.schedule_slot_id)
        rec = clocked.setdefault(
            key, {"employee": att.employee, "slot": att.schedule_slot, "arrival": None, "departure": None}
        )
        if att.clock_type == Attendance.ClockType.ARRIVAL:
            rec["arrival"] = att
        elif att.clock_type == Attendance.ClockType.DEPARTURE:
            rec["departure"] = att

    # 3. Fusion prévu + pointé.
    now = timezone.localtime()
    is_today = on_date == timezone.localdate()
    entries = []
    for key in set(planned) | set(clocked):
        source = clocked.get(key) or planned[key]
        arrival = source.get("arrival") if key in clocked else None
        departure = source.get("departure") if key in clocked else None
        slot = source["slot"]
        entries.append(
            {
                "employee": source["employee"],
                "slot": slot,
                "arrival": arrival,
                "departure": departure,
                "clocked": arrival is not None,
                "in_progress": bool(arrival) and departure is None and is_today and now.time() <= slot.end_time,
            }
        )
    entries.sort(key=lambda e: (e["slot"].start_time, (e["slot"].room or "").casefold(), str(e["employee"])))
    return entries
