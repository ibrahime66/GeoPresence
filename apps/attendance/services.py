from datetime import datetime, timedelta
from decimal import Decimal

from django.utils import timezone

from apps.schedules.services import get_effective_schedule

from . import constants
from .models import Attendance


class ClockRejected(Exception):
    """CDC §9.2 : une des vérifications pré-pointage a échoué — le pointage
    n'est PAS enregistré (contrairement à un horaire non respecté, cf.
    compute_status_and_deltas, qui lui est enregistré avec un statut adapté)."""

    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(message)


CLOCK_TYPE_WINDOW_FIELDS = {
    Attendance.ClockType.ARRIVAL: ("clock_in_window_before_minutes", "clock_in_window_after_minutes"),
    Attendance.ClockType.BREAK_END: ("clock_in_window_before_minutes", "clock_in_window_after_minutes"),
    Attendance.ClockType.BREAK_START: ("clock_out_window_before_minutes", "clock_out_window_after_minutes"),
    Attendance.ClockType.DEPARTURE: ("clock_out_window_before_minutes", "clock_out_window_after_minutes"),
}


def _combine(clock_date, t, next_day=False):
    dt = datetime.combine(clock_date + timedelta(days=1 if next_day else 0), t)
    return timezone.make_aware(dt) if timezone.is_naive(dt) else dt


def _find_matching_agency(employee, latitude, longitude, gps_accuracy):
    """CDC §8.3 point 39 : si l'employé est affecté à plusieurs agences,
    toutes ses zones sont vérifiées. Retourne (agence_ou_None, distance, zone)."""
    candidates = [employee.primary_agency] + list(employee.secondary_agencies.all())
    closest = None
    for agency in candidates:
        authorized, distance, zone = agency.check_point(latitude, longitude, gps_accuracy)
        if authorized:
            return agency, distance, zone
        if closest is None or distance < closest[1]:
            closest = (agency, distance, zone)
    return None, closest[1] if closest else None, closest[2] if closest else None


def resolve_clock_date(employee, clock_type, now):
    """RM-HOR-004 : un DEPARTURE (ou une pause) qui suit une arrivée non
    encore clôturée de la veille reste rattaché au jour de cette arrivée
    (équipe de nuit à cheval sur minuit)."""
    today = now.date()
    if clock_type == Attendance.ClockType.ARRIVAL:
        return today

    yesterday = today - timedelta(days=1)
    yesterday_types = set(
        Attendance.objects.all_tenants()
        .filter(employee=employee, clock_date=yesterday)
        .values_list("clock_type", flat=True)
    )
    if Attendance.ClockType.ARRIVAL in yesterday_types and Attendance.ClockType.DEPARTURE not in yesterday_types:
        return yesterday
    return today


def get_clock_status(employee, now=None):
    """Prochain type de pointage attendu (pour piloter le bouton affiché,
    CDC §9.3.1). Retourne (clock_type_ou_None, clock_date)."""
    now = now or timezone.now()
    departure_date = resolve_clock_date(employee, Attendance.ClockType.DEPARTURE, now)
    departure_day_types = set(
        Attendance.objects.all_tenants()
        .filter(employee=employee, clock_date=departure_date)
        .values_list("clock_type", flat=True)
    )
    if Attendance.ClockType.ARRIVAL in departure_day_types and Attendance.ClockType.DEPARTURE not in departure_day_types:
        return Attendance.ClockType.DEPARTURE, departure_date

    today = now.date()
    today_types = set(
        Attendance.objects.all_tenants()
        .filter(employee=employee, clock_date=today)
        .values_list("clock_type", flat=True)
    )
    if Attendance.ClockType.ARRIVAL not in today_types:
        return Attendance.ClockType.ARRIVAL, today
    if Attendance.ClockType.DEPARTURE not in today_types:
        return Attendance.ClockType.DEPARTURE, today
    return None, today


def _check_sequence(employee, clock_date, clock_type):
    """RM-POINT-004/005 : une arrivée, un départ, une pause par jour, et
    toujours dans le bon ordre."""
    existing = set(
        Attendance.objects.all_tenants()
        .filter(employee=employee, clock_date=clock_date)
        .values_list("clock_type", flat=True)
    )
    ct = Attendance.ClockType

    if clock_type in existing:
        raise ClockRejected(f"{clock_type} déjà enregistré pour cette journée.", "duplicate")
    if clock_type == ct.DEPARTURE and ct.ARRIVAL not in existing:
        raise ClockRejected("Aucune arrivée enregistrée : impossible de pointer un départ.", "no_arrival")
    if clock_type == ct.BREAK_START and ct.ARRIVAL not in existing:
        raise ClockRejected("Aucune arrivée enregistrée.", "no_arrival")
    if clock_type == ct.BREAK_END and ct.BREAK_START not in existing:
        raise ClockRejected("Aucun départ en pause enregistré.", "no_break_start")


def resolve_slot(employee, clock_date, schedule):
    if schedule is None:
        return None
    slots = list(schedule.slots_for_weekday(clock_date.weekday()))
    if not slots:
        return None
    # Cas standard : un créneau/jour. Le support de plusieurs créneaux/jour
    # (enseignants) est une extension différée — on prend le premier.
    return slots[0]


def expected_datetime(clock_date, slot, clock_type):
    if slot is None:
        return None
    ct = Attendance.ClockType
    if clock_type == ct.ARRIVAL:
        return _combine(clock_date, slot.start_time)
    if clock_type == ct.DEPARTURE:
        return _combine(clock_date, slot.end_time, next_day=slot.is_overnight)
    if clock_type == ct.BREAK_START and slot.break_start_time:
        return _combine(clock_date, slot.break_start_time)
    if clock_type == ct.BREAK_END and slot.break_end_time:
        return _combine(clock_date, slot.break_end_time, next_day=slot.is_overnight and slot.break_end_time <= slot.break_start_time)
    return None


def compute_status_and_deltas(clock_type, schedule, slot, expected_dt, actual_dt):
    """RM-POINT-009 : retard = heure pointage − (heure prévue + tolérance).
    RM-HOR-003 : hors fenêtre de pointage -> statut HORS_HORAIRE, mais le
    pointage reste enregistré (ce n'est pas un motif de refus, cf. ClockRejected
    qui lui gère les vraies raisons de refus : zone GPS, doublon, séquence...)."""
    ct = Attendance.ClockType
    Status = Attendance.Status

    if expected_dt is None or slot is None:
        return Status.OUT_OF_SCHEDULE, None, None, None

    before_field, after_field = CLOCK_TYPE_WINDOW_FIELDS[clock_type]
    window_start = expected_dt - timedelta(minutes=getattr(slot, before_field))
    window_end = expected_dt + timedelta(minutes=getattr(slot, after_field))
    if actual_dt < window_start or actual_dt > window_end:
        return Status.OUT_OF_SCHEDULE, None, None, None

    late_tolerance = _tolerance(schedule, "late_tolerance_minutes", constants.DEFAULT_LATE_TOLERANCE_MINUTES)
    early_tolerance = _tolerance(
        schedule, "early_leave_tolerance_minutes", constants.DEFAULT_EARLY_LEAVE_TOLERANCE_MINUTES
    )
    overtime_threshold = _tolerance(
        schedule, "overtime_threshold_minutes", constants.DEFAULT_OVERTIME_THRESHOLD_MINUTES
    )

    delta_minutes = (actual_dt - expected_dt).total_seconds() / 60

    if clock_type in (ct.ARRIVAL, ct.BREAK_END):
        late = round(delta_minutes - late_tolerance)
        if late > 0:
            return Status.LATE, late, None, None
        return Status.ON_TIME, None, None, None

    # DEPARTURE / BREAK_START
    early = round(-delta_minutes - early_tolerance)
    if early > 0:
        return Status.EARLY_LEAVE, None, early, None
    overtime = round(delta_minutes - overtime_threshold)
    if overtime > 0:
        return Status.OVERTIME, None, None, overtime
    return Status.ON_TIME, None, None, None


def _tolerance(schedule, field_name, default):
    if schedule is not None:
        value = getattr(schedule, field_name)
        if value is not None:
            return value
    return default


def clock(
    employee,
    clock_type,
    *,
    latitude,
    longitude,
    gps_accuracy=None,
    is_gps_mocked=False,
    photo,
    ip_address=None,
    user_agent="",
    device_type="",
    client_time=None,
    now=None,
    mode=Attendance.Mode.ONLINE,
):
    """Orchestration complète d'un pointage — CDC §9.3.6 (re-validation
    serveur de toutes les vérifications, calcul du statut, enregistrement)."""
    now = now or timezone.now()
    # Django convertit un float en Decimal via sa représentation binaire exacte
    # (ex. 48.8583701 -> 48.858370099999996...), ce qui dépasse decimal_places=7
    # sur le modèle. En passant par str() d'abord, on obtient la représentation
    # décimale attendue. Les DecimalField de formulaire font déjà ça correctement
    # (Decimal(str(...))) ; on le refait ici pour rester correct quel que soit
    # l'appelant (form validé, tests, futur endpoint de synchronisation offline).
    latitude = Decimal(str(latitude))
    longitude = Decimal(str(longitude))
    if gps_accuracy is not None:
        gps_accuracy = Decimal(str(gps_accuracy))

    if is_gps_mocked:
        raise ClockRejected("Position GPS simulée détectée — pointage refusé.", "gps_mocked")

    agency, distance, zone = _find_matching_agency(employee, latitude, longitude, gps_accuracy)
    if agency is None:
        if distance is not None:
            message = f"Hors zone autorisée (distance {distance:.0f} m, rayon requis {zone['radius']:.0f} m)."
        else:
            message = "Aucune agence associée à votre profil."
        raise ClockRejected(message, "out_of_zone")

    clock_date = resolve_clock_date(employee, clock_type, now)
    _check_sequence(employee, clock_date, clock_type)

    schedule = get_effective_schedule(employee, on_date=clock_date)
    slot = resolve_slot(employee, clock_date, schedule)
    expected_dt = expected_datetime(clock_date, slot, clock_type)
    status, late, early, overtime = compute_status_and_deltas(clock_type, schedule, slot, expected_dt, now)

    attendance = Attendance(
        tenant=employee.tenant,
        employee=employee,
        agency=agency,
        clock_type=clock_type,
        clock_date=clock_date,
        server_time=now,
        client_time=client_time,
        latitude=latitude,
        longitude=longitude,
        gps_accuracy=gps_accuracy,
        is_gps_mocked=is_gps_mocked,
        photo=photo,
        ip_address=ip_address,
        user_agent=user_agent[:255],
        device_type=device_type,
        scheduled_time=expected_dt,
        late_minutes=late,
        early_leave_minutes=early,
        overtime_minutes=overtime,
        status=status,
        mode=mode,
    )
    attendance.full_clean()
    attendance.save()
    return attendance
