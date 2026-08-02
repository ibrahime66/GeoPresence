import uuid

from django.db import models

from apps.core.context import get_current_tenant


class UUIDModel(models.Model):
    """PK en UUID plutôt qu'auto-increment, pour éviter les ID séquentiels devinables
    et faciliter la génération côté client (mode offline)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantManager(models.Manager):
    """Filtre automatiquement par le tenant courant (RM-ORG-004 : isolation
    cross-tenant absolue). Fail-secure : si aucun tenant n'est actif dans le
    contexte de la requête (ex. Super Admin, cf. RM-ORG-005), la queryset par
    défaut est VIDE plutôt que de tout renvoyer."""

    def get_queryset(self):
        tenant = get_current_tenant()
        qs = super().get_queryset()
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)

    def all_tenants(self):
        """Contourne explicitement le filtrage — réservé aux accès Super Admin
        documentés et exceptionnels (RM-ORG-005), jamais utilisé par défaut."""
        return super().get_queryset()


class TenantModel(UUIDModel, TimeStampedModel):
    """Base pour tout modèle métier appartenant à une organisation (Agence,
    Employé, Pointage, ...). related_name='+' : pas d'accesseur inverse générique
    depuis Organization — on interroge toujours via le manager scopé au tenant
    courant plutôt que via organization.<related_name>."""

    tenant = models.ForeignKey(
        "tenants.Organization", on_delete=models.CASCADE, related_name="+", db_index=True
    )

    objects = TenantManager()
    # Manager non filtré, utilisé par Django en interne pour les relations
    # inverses (ex. schedule.slots.all()) et les cascades de suppression.
    # Sans ça, ces accès hériteraient du filtrage par tenant courant alors que
    # le tenant est déjà sans ambiguïté connu via l'objet parent — cf. RM-ORG-004,
    # le filtrage sert à protéger les requêtes de premier niveau (Model.objects.*),
    # pas la navigation entre objets déjà résolus.
    all_objects = models.Manager()

    class Meta:
        abstract = True
        # default_manager_name : utilisé par Django pour les relations inverses
        # (schedule.slots.all()). base_manager_name : utilisé pour les cascades
        # de suppression. Les deux doivent pointer vers le manager NON filtré —
        # sinon Django perdrait silencieusement des lignes lors de ces accès
        # internes, alors que le tenant est déjà sans ambiguïté celui de l'objet
        # parent (cf. commentaire sur all_objects ci-dessus).
        default_manager_name = "all_objects"
        base_manager_name = "all_objects"
        indexes = [
            models.Index(fields=["tenant", "created_at"], name="%(app_label)s_%(class)s_tc_idx"),
        ]
