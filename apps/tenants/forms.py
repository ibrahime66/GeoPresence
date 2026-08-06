from django import forms

from apps.core.forms import BootstrapModelFormMixin

from .org_settings import DEFAULTS


class OrganizationSettingsForm(BootstrapModelFormMixin, forms.Form):
    """CDC §6.4.2/§6.4.3 : paramètres de pointage et de sécurité propres à
    l'organisation — stockés dans Organization.settings (JSON), pas de Meta
    de ModelForm possible ici."""

    departments_enabled = forms.BooleanField(
        label="Départements activés", required=False,
        help_text="Désactiver masque le menu Départements — utile pour une structure organisationnelle plate.",
    )
    positions_enabled = forms.BooleanField(
        label="Postes activés", required=False,
        help_text="Désactiver masque le menu Postes et le champ « Poste » sur la fiche employé.",
    )
    multi_slot_attendance_enabled = forms.BooleanField(
        label="Pointage multi-créneaux", required=False,
        help_text="Autorise plusieurs arrivées/départs par jour, un par créneau d'horaire (ex. enseignants).",
    )

    gps_radius_default_meters = forms.IntegerField(
        label="Rayon GPS par défaut (m)", min_value=50, max_value=5000,
        help_text="Appliqué comme valeur initiale à la création d'une nouvelle agence.",
    )
    gps_tolerance_meters = forms.IntegerField(
        label="Marge de tolérance GPS (m)", min_value=0, max_value=500,
        help_text="Ajoutée au rayon de chaque agence pour absorber l'imprécision GPS des smartphones.",
    )
    late_tolerance_minutes = forms.IntegerField(label="Tolérance de retard (min)", min_value=0, max_value=120)
    early_leave_tolerance_minutes = forms.IntegerField(
        label="Tolérance de départ anticipé (min)", min_value=0, max_value=120
    )
    overtime_threshold_minutes = forms.IntegerField(
        label="Seuil heures supplémentaires (min)", min_value=0, max_value=240
    )
    offline_sync_max_delay_hours = forms.IntegerField(
        label="Délai max de synchronisation hors ligne (h)", min_value=1, max_value=168
    )

    max_failed_login_attempts = forms.IntegerField(label="Tentatives avant blocage du compte", min_value=3, max_value=10)
    lockout_base_minutes = forms.IntegerField(
        label="Durée de blocage initiale (min)", min_value=1, max_value=1440,
        help_text="Double à chaque récidive (15 → 30 → 60 min...).",
    )
    session_duration_admin_hours = forms.IntegerField(
        label="Durée de session — Administrateurs (h)", min_value=1, max_value=24
    )
    session_duration_employee_hours = forms.IntegerField(
        label="Durée de session — Employés (h)", min_value=1, max_value=24
    )
    password_min_length = forms.IntegerField(
        label="Longueur minimale du mot de passe", min_value=8, max_value=20,
        help_text="Ne peut pas être inférieure à 8 (plancher plateforme).",
    )
    password_expiration_days = forms.IntegerField(label="Expiration du mot de passe (jours)", min_value=30, max_value=365)
    password_history_count = forms.IntegerField(
        label="Historique des mots de passe (nombre mémorisé)", min_value=1, max_value=20
    )

    @classmethod
    def initial_from_organization(cls, organization):
        overrides = organization.settings or {}
        return {key: overrides.get(key, default) for key, default in DEFAULTS.items()}

    def save(self, organization):
        organization.settings = {**(organization.settings or {}), **self.cleaned_data}
        organization.save(update_fields=["settings"])
        return organization
