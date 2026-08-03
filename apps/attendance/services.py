from datetime import datetime, timedelta
from decimal import Decimal

from django.utils import timezone

from apps.schedules.services import get_effective_schedule

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


def _slot_attendance_types(employee, clock_date, slot):
    return set(
        Attendance.objects.all_tenants()
        .filter(employee=employee, clock_date=clock_date, schedule_slot=slot)
        .values_list("clock_type", flat=True)
    )


def get_clock_status(employee, now=None):
    """Prochain type de pointage attendu (pour piloter le bouton affiché,
    CDC §9.3.1). Retourne (clock_type_ou_None, clock_date, slot_ou_None).

    CDC §10.2.4 (pointage multi-créneaux, ex. enseignants) : quand
    l'organisation active ce mode (apps.tenants.org_settings), chaque
    créneau du jour est une paire arrivée/départ indépendante — cf.
    apps.attendance.services.clock. Sinon (immense majorité des
    organisations), comportement historique inchangé : un aller-retour/jour."""
    now = now or timezone.now()

    from apps.tenants.org_settings import get_org_setting

    if get_org_setting(employee.tenant, "multi_slot_attendance_enabled"):
        today = now.date()
        schedule = get_effective_schedule(employee, on_date=today)
        if schedule is not None:
            ct = Attendance.ClockType
            for slot in schedule.slots_for_weekday(today.weekday()):
                types = _slot_attendance_types(employee, today, slot)
                if ct.ARRIVAL not in types:
                    return ct.ARRIVAL, today, slot
                if ct.DEPARTURE not in types:
                    return ct.DEPARTURE, today, slot
        return None, today, None

    departure_date = resolve_clock_date(employee, Attendance.ClockType.DEPARTURE, now)
    departure_day_types = set(
        Attendance.objects.all_tenants()
        .filter(employee=employee, clock_date=departure_date)
        .values_list("clock_type", flat=True)
    )
    if Attendance.ClockType.ARRIVAL in departure_day_types and Attendance.ClockType.DEPARTURE not in departure_day_types:
        return Attendance.ClockType.DEPARTURE, departure_date, None

    today = now.date()
    today_types = set(
        Attendance.objects.all_tenants()
        .filter(employee=employee, clock_date=today)
        .values_list("clock_type", flat=True)
    )
    if Attendance.ClockType.ARRIVAL not in today_types:
        return Attendance.ClockType.ARRIVAL, today, None
    if Attendance.ClockType.DEPARTURE not in today_types:
        return Attendance.ClockType.DEPARTURE, today, None
    return None, today, None


def _check_sequence(employee, clock_date, clock_type, slot=None, multi_slot=False):
    """RM-POINT-004/005 : une arrivée, un départ, une pause par jour — ou, en
    mode multi-créneaux, par créneau (arrivée/départ uniquement ; les pauses
    restent au niveau jour, une pause déjeuner n'a pas de sens "par cours") —
    et toujours dans le bon ordre."""
    ct = Attendance.ClockType

    if multi_slot and slot is not None and clock_type in (ct.ARRIVAL, ct.DEPARTURE):
        types = _slot_attendance_types(employee, clock_date, slot)
        if clock_type in types:
            raise ClockRejected(f"{clock_type} déjà enregistré pour ce créneau.", "duplicate")
        if clock_type == ct.DEPARTURE and ct.ARRIVAL not in types:
            raise ClockRejected("Aucune arrivée enregistrée pour ce créneau.", "no_arrival")
        return

    existing = set(
        Attendance.objects.all_tenants()
        .filter(employee=employee, clock_date=clock_date)
        .values_list("clock_type", flat=True)
    )

    if clock_type in existing:
        raise ClockRejected(f"{clock_type} déjà enregistré pour cette journée.", "duplicate")
    if clock_type == ct.DEPARTURE and ct.ARRIVAL not in existing:
        raise ClockRejected("Aucune arrivée enregistrée : impossible de pointer un départ.", "no_arrival")
    if clock_type == ct.BREAK_START and ct.ARRIVAL not in existing:
        raise ClockRejected("Aucune arrivée enregistrée.", "no_arrival")
    if clock_type == ct.BREAK_END and ct.BREAK_START not in existing:
        raise ClockRejected("Aucun départ en pause enregistré.", "no_break_start")


def resolve_slot(employee, clock_date, schedule, clock_type=None, multi_slot=False):
    """Retourne le créneau (ScheduleSlot) concerné par ce pointage.

    Hors mode multi-créneaux (comportement historique, inchangé) : toujours
    le premier créneau du jour, quel que soit clock_type.

    En mode multi-créneaux (CDC §10.2.4) et pour une arrivée/départ : le
    premier créneau du jour dont ce clock_type n'est pas encore enregistré
    (arrivée manquante, ou départ en attente d'une arrivée déjà pointée).
    None si tous les créneaux du jour sont déjà complets pour ce type."""
    if schedule is None:
        return None
    slots = list(schedule.slots_for_weekday(clock_date.weekday()))
    if not slots:
        return None

    ct = Attendance.ClockType
    if not multi_slot or clock_type not in (ct.ARRIVAL, ct.DEPARTURE):
        return slots[0]

    for slot in slots:
        types = _slot_attendance_types(employee, clock_date, slot)
        if clock_type == ct.ARRIVAL and ct.ARRIVAL not in types:
            return slot
        if clock_type == ct.DEPARTURE and ct.ARRIVAL in types and ct.DEPARTURE not in types:
            return slot
    return None


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


def compute_status_and_deltas(clock_type, schedule, slot, expected_dt, actual_dt, tenant=None):
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

    # CDC §6.4.2 : valeurs par défaut configurables par organisation
    # (apps.tenants.org_settings) — un Schedule qui surcharge explicitement
    # reste prioritaire (RM-HOR-002).
    from apps.tenants.org_settings import get_org_setting

    late_tolerance = _tolerance(schedule, "late_tolerance_minutes", get_org_setting(tenant, "late_tolerance_minutes"))
    early_tolerance = _tolerance(
        schedule, "early_leave_tolerance_minutes", get_org_setting(tenant, "early_leave_tolerance_minutes")
    )
    overtime_threshold = _tolerance(
        schedule, "overtime_threshold_minutes", get_org_setting(tenant, "overtime_threshold_minutes")
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
        # Un GPS simulé n'est jamais toléré, même en synchronisation hors ligne
        # (RM-POINT-009 : c'est un signal de fraude, pas un problème réseau).
        raise ClockRejected("Position GPS simulée détectée — pointage refusé.", "gps_mocked")

    is_offline = mode == Attendance.Mode.OFFLINE
    pending_reason = ""

    agency, distance, zone = _find_matching_agency(employee, latitude, longitude, gps_accuracy)
    if agency is None:
        if is_offline:
            # CDC §9.7.3 : un pointage hors ligne hors zone n'est pas perdu —
            # il est enregistré pour contrôle manuel (EN_ATTENTE_VALIDATION)
            # plutôt que rejeté, contrairement au flux en ligne.
            agency = employee.primary_agency
            pending_reason = "out_of_zone"
        elif distance is not None:
            message = f"Hors zone autorisée (distance {distance:.0f} m, rayon requis {zone['radius']:.0f} m)."
            raise ClockRejected(message, "out_of_zone")
        else:
            raise ClockRejected("Aucune agence associée à votre profil.", "no_agency")

    clock_date = resolve_clock_date(employee, clock_type, now)

    from apps.tenants.org_settings import get_org_setting

    multi_slot = get_org_setting(employee.tenant, "multi_slot_attendance_enabled")

    schedule = get_effective_schedule(employee, on_date=clock_date)
    slot = resolve_slot(employee, clock_date, schedule, clock_type=clock_type, multi_slot=multi_slot)

    ct = Attendance.ClockType
    if multi_slot and clock_type in (ct.ARRIVAL, ct.DEPARTURE) and schedule is not None and slot is None:
        if list(schedule.slots_for_weekday(clock_date.weekday())):
            raise ClockRejected("Tous les créneaux du jour sont déjà pointés pour ce type.", "all_slots_done")

    _check_sequence(employee, clock_date, clock_type, slot=slot, multi_slot=multi_slot)

    expected_dt = expected_datetime(clock_date, slot, clock_type)
    status, late, early, overtime = compute_status_and_deltas(
        clock_type, schedule, slot, expected_dt, now, tenant=employee.tenant
    )

    if is_offline and client_time is not None:
        max_delay = timedelta(hours=get_org_setting(employee.tenant, "offline_sync_max_delay_hours"))
        if now - client_time > max_delay:
            pending_reason = pending_reason or "sync_delay_exceeded"

    if pending_reason:
        status = Attendance.Status.PENDING_VALIDATION

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
        ip_address=ip_address,
        user_agent=user_agent[:255],
        device_type=device_type,
        schedule_slot=slot,
        scheduled_time=expected_dt,
        late_minutes=late,
        early_leave_minutes=early,
        overtime_minutes=overtime,
        status=status,
        mode=mode,
        synced_at=now if is_offline else None,
        notes=f"Synchronisé hors ligne — motif de contrôle : {pending_reason}" if pending_reason else "",
    )
    attendance.full_clean()
    attendance.save()
    return attendance
