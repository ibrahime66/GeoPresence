from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.encrypted_fields import EncryptedCharField
from apps.core.models import TenantModel
from apps.core.storage import generate_upload_filename


def employee_photo_path(instance, filename):
    return f"organizations/{instance.tenant_id}/employees/{instance.id}/{generate_upload_filename(filename)}"


class Employee(TenantModel):
    """CDC §11. Profil RH détaillé — étend accounts.User (identité/auth/rôle)
    plutôt que de dupliquer prénom/nom/e-mail professionnel, déjà sur User."""

    class Gender(models.TextChoices):
        MALE = "MALE", "Masculin"
        FEMALE = "FEMALE", "Féminin"
        UNSPECIFIED = "UNSPECIFIED", "Non renseigné"

    class ContractType(models.TextChoices):
        CDI = "CDI", "CDI"
        CDD = "CDD", "CDD"
        INTERIM = "INTERIM", "Intérim"
        INTERNSHIP = "INTERNSHIP", "Stage"
        VOLUNTEER = "VOLUNTEER", "Bénévole"
        CONSULTANT = "CONSULTANT", "Consultant"
        OTHER = "OTHER", "Autre"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Actif"
        SUSPENDED = "SUSPENDED", "Suspendu"
        ON_LEAVE = "ON_LEAVE", "En congé"
        ARCHIVED = "ARCHIVED", "Archivé"

    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="employee_profile")

    matricule = models.CharField(max_length=30, blank=True)
    preferred_name = models.CharField("nom d'usage", max_length=150, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=15, choices=Gender.choices, default=Gender.UNSPECIFIED)
    nationality = models.CharField(max_length=100, blank=True)
    # RM-SEC-004 : chiffré au repos (numéro de carte d'identité / passeport).
    id_number = EncryptedCharField(blank=True)

    profile_photo = models.ImageField(upload_to=employee_photo_path, blank=True, null=True, max_length=255)

    personal_email = models.EmailField(blank=True)
    work_phone = models.CharField(max_length=30, blank=True)
    personal_phone = models.CharField(max_length=30, blank=True)
    home_address = models.TextField(blank=True)

    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)

    department = models.ForeignKey(
        "departments.Department", on_delete=models.PROTECT, null=True, blank=True, related_name="employees"
    )
    position = models.ForeignKey(
        "departments.Position", on_delete=models.PROTECT, null=True, blank=True, related_name="employees"
    )
    primary_agency = models.ForeignKey(
        "agencies.Agency", on_delete=models.PROTECT, related_name="employees_primary"
    )
    secondary_agencies = models.ManyToManyField(
        "agencies.Agency", blank=True, related_name="employees_secondary"
    )

    contract_type = models.CharField(max_length=15, choices=ContractType.choices, default=ContractType.CDI)
    hire_date = models.DateField()
    contract_end_date = models.DateField(null=True, blank=True)

    # NOTE : l'horaire affecté (CDC §10.3, priorité employé > poste > département
    # > agence) rejoindra ce modèle avec l'app `schedules`.

    manager = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="direct_reports"
    )

    annual_leave_days = models.DecimalField("droit aux congés (j/an)", max_digits=5, decimal_places=1, default=0)
    leave_balance = models.DecimalField("solde congés (j)", max_digits=5, decimal_places=1, default=0)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["matricule"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "matricule"], name="employees_employee_tenant_matricule_uniq"),
        ]

    def __str__(self):
        return f"{self.matricule} — {self.user.full_name or self.user.email}"

    def clean(self):
        super().clean()
        if self.user_id and self.tenant_id and self.user.tenant_id != self.tenant_id:
            raise ValidationError("Le compte utilisateur lié doit appartenir à la même organisation.")
        for field_name in ("department", "position", "primary_agency"):
            related = getattr(self, field_name, None)
            if related is not None and related.tenant_id != self.tenant_id:
                raise ValidationError(f"« {field_name} » doit appartenir à la même organisation.")
        if self.manager_id and self.manager.tenant_id != self.tenant_id:
            raise ValidationError("Le manager direct doit appartenir à la même organisation.")
        # CDC §11.3.3 : la date d'entrée ne peut pas être dans le futur de plus de 30 jours.
        if self.hire_date and self.hire_date > timezone.localdate() + timedelta(days=30):
            raise ValidationError("La date d'entrée ne peut pas être à plus de 30 jours dans le futur.")
        if self.contract_end_date and self.hire_date and self.contract_end_date <= self.hire_date:
            raise ValidationError("La date de fin de contrat doit être postérieure à la date d'entrée.")

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if not self.matricule:
            self.matricule = self._generate_matricule()
        if is_new and not self.leave_balance:
            self.leave_balance = self.annual_leave_days
        super().save(*args, **kwargs)

    def _generate_matricule(self):
        sequence = type(self).objects.all_tenants().filter(tenant=self.tenant).count() + 1
        candidate = f"EMP{sequence:05d}"
        while type(self).objects.all_tenants().filter(tenant=self.tenant, matricule=candidate).exists():
            sequence += 1
            candidate = f"EMP{sequence:05d}"
        return candidate
