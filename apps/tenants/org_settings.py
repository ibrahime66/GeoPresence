"""CDC §6.4.2/§6.4.3 : paramètres de pointage et de sécurité configurables
PAR ORGANISATION. Stockés dans `Organization.settings` (JSONField) plutôt que
dans des colonnes dédiées — évite une migration à chaque nouveau paramètre,
au prix d'une validation applicative plutôt que par le schéma (assumé, cf.
`OrganizationSettingsForm`).

Chaque clé a une valeur plateforme par défaut ci-dessous, identique à
l'ancienne constante codée en dur qu'elle remplace (comportement inchangé
tant qu'aucune organisation ne surcharge la valeur).
"""

from django.utils.translation import gettext_lazy as _

DEFAULTS = {
    # Jours de repos hebdomadaires (indices apps.schedules.models.Weekday,
    # 0=Lundi ... 6=Dimanche) — exclus du décompte des jours de congé
    # (apps.leaves.services.compute_working_days). N'affecte pas les horaires
    # de pointage eux-mêmes, déjà librement configurables jour par jour.
    "rest_weekdays": [5, 6],
    # CDC §6.4.2 — pointage.
    "gps_radius_default_meters": 200,
    "gps_tolerance_meters": 30,
    "late_tolerance_minutes": 5,
    "early_leave_tolerance_minutes": 5,
    "overtime_threshold_minutes": 15,
    "offline_sync_max_delay_hours": 48,
    # Modules — toute organisation n'a pas la même structure (une pharmacie
    # n'a souvent pas besoin de hiérarchie de départements ; une école a
    # besoin de plusieurs créneaux de pointage par jour, CDC §10.2.4). Réglages
    # PAR ORGANISATION plutôt que figés par type — le type d'organisation ne
    # fait que pré-cocher une valeur par défaut sensée à la création (cf.
    # apps.superadmin.forms.OrganizationCreateForm), l'Admin garde la main.
    "departments_enabled": True,
    "positions_enabled": True,
    "multi_slot_attendance_enabled": False,
    # RM-ORG-SCHOOL (21/08/2026) : distinct de multi_slot_attendance_enabled
    # (qui ne fait qu'autoriser plusieurs arrivées/départs par jour) — celui-ci
    # ajoute les champs matière/salle/groupe/remplacement propres au CDC
    # §10.2.4. Une pharmacie ou un restaurant n'a besoin d'aucun des deux ;
    # une école pourrait en théorie vouloir l'un sans l'autre, d'où deux
    # réglages séparés plutôt qu'un seul.
    "school_scheduling_enabled": False,
    # CDC §6.4.3 — sécurité.
    "max_failed_login_attempts": 5,
    "lockout_base_minutes": 15,
    "session_duration_admin_hours": 2,
    "session_duration_employee_hours": 8,
    "password_min_length": 8,
    "password_expiration_days": 90,
    "password_history_count": 5,
}

# CDC §13.3.1 : la progression du blocage (15/30/60/240/1440 min par défaut)
# est exprimée comme des multiplicateurs de `lockout_base_minutes`, pour
# qu'une organisation qui change la base voie toute l'échelle suivre.
LOCKOUT_MULTIPLIERS = [1, 2, 4, 16, 96]

# Pré-réglages suggérés à la création selon le secteur (Organization.OrgType)
# — une simple valeur de départ, jamais figée : l'Admin peut tout changer
# ensuite depuis Paramètres. Un type absent de ce dict garde les DEFAULTS
# plateforme (aucune suggestion particulière).
TYPE_DEFAULTS = {
    "PHARMACY": {"departments_enabled": False, "positions_enabled": False},
    "RESTAURANT": {"positions_enabled": False},
    "ASSOCIATION": {"positions_enabled": False},
    "NGO": {"positions_enabled": False},
    "SCHOOL": {"multi_slot_attendance_enabled": True, "school_scheduling_enabled": True},
    "UNIVERSITY": {"multi_slot_attendance_enabled": True, "school_scheduling_enabled": True},
}


# Registre central des modules optionnels qui masquent un lien de menu ET un
# ou plusieurs champs de formulaire selon le réglage. Pour ajouter un nouveau
# module de ce type : UNE seule entrée ici (plutôt que de toucher séparément
# le processeur de contexte, la sidebar et chaque formulaire concerné). Le
# blocage des champs de formulaire reste déclaré dans chaque formulaire via
# `apps.core.forms.apply_module_gating` (les noms de champs varient d'un
# formulaire à l'autre pour un même module).
MODULES = [
    {
        "key": "departments_enabled",
        "sidebar_label": _("Départements"),
        "sidebar_icon": "building",
        "sidebar_url": "departments:list",
        "sidebar_match_namespace": "departments",
    },
    {
        "key": "positions_enabled",
        "sidebar_label": _("Postes"),
        "sidebar_icon": "briefcase",
        "sidebar_url": "departments:position_list",
        "sidebar_match_url_name": "position_list",
    },
]


def initial_settings_for_type(org_type):
    """Utilisé une seule fois, à la création de l'organisation (cf.
    apps.superadmin.views.OrganizationCreateView) — au-delà, ces valeurs sont
    des réglages normaux, modifiables comme n'importe quel autre."""
    return dict(TYPE_DEFAULTS.get(org_type, {}))


def get_org_settings(tenant):
    """Retourne le dict de paramètres effectifs (défauts fusionnés avec les
    surcharges de l'organisation). `tenant=None` (Super Admin) -> défauts purs."""
    if tenant is None:
        return dict(DEFAULTS)
    overrides = tenant.settings or {}
    return {**DEFAULTS, **{k: v for k, v in overrides.items() if k in DEFAULTS}}


def get_org_setting(tenant, key):
    return get_org_settings(tenant)[key]


def lockout_duration_minutes(tenant, lockout_count):
    base = get_org_setting(tenant, "lockout_base_minutes")
    index = min(lockout_count, len(LOCKOUT_MULTIPLIERS) - 1)
    return base * LOCKOUT_MULTIPLIERS[index]
