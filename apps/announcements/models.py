from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TenantModel


class Announcement(TenantModel):
    """CDC §3.2.5 : annonces internes créées par l'Administrateur, ciblées par
    agence/département/employés, avec publication et expiration programmables.
    Affichées sur le tableau de bord Employé (CDC §16.4) — le Manager les voit
    aussi, son dashboard combinant la vue employé (cf. apps.core.views)."""

    title = models.CharField("titre", max_length=255)
    content = models.TextField("contenu")
    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="+", verbose_name="créée par"
    )

    # Une annonce sans aucune cible (agences/départements/employés tous vides)
    # est visible par tout le monde — cf. apps.announcements.services.
    agencies = models.ManyToManyField(
        "agencies.Agency", blank=True, related_name="announcements", verbose_name="agences"
    )
    departments = models.ManyToManyField(
        "departments.Department", blank=True, related_name="announcements", verbose_name="départements"
    )
    employees = models.ManyToManyField(
        "employees.Employee", blank=True, related_name="announcements", verbose_name="employés"
    )

    # "Programmer la publication et l'expiration" (CDC §3.2.5) — publish_at
    # dans le futur = brouillon programmé, pas encore visible.
    publish_at = models.DateTimeField("date de publication")
    expire_at = models.DateTimeField("date d'expiration", null=True, blank=True)

    class Meta:
        ordering = ["-publish_at"]
        indexes = [models.Index(fields=["tenant", "publish_at", "expire_at"])]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.expire_at and self.publish_at and self.expire_at <= self.publish_at:
            raise ValidationError("La date d'expiration doit être postérieure à la date de publication.")
