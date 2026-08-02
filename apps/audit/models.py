from django.db import models

from apps.core.models import UUIDModel


class AuditLog(UUIDModel):
    """Journal d'audit — CDC §14. Écriture seule (RM-SEC-002/004) : ce modèle
    n'est volontairement jamais mis à jour ni supprimé par le code applicatif,
    et son admin Django est en lecture seule (voir admin.py).

    Version minimale pour ce sprint (événements d'authentification uniquement,
    CDC §14.2.1). Les catégories Utilisateur/Pointage/Données/Documents (§14.2.2-5)
    et l'immutabilité renforcée par triggers MySQL (ANALYSE-TECHNIQUE §5.2)
    viendront avec le sprint dédié à l'audit complet.
    """

    class Result(models.TextChoices):
        SUCCESS = "SUCCESS", "Succès"
        FAILURE = "FAILURE", "Échec"

    tenant = models.ForeignKey(
        "tenants.Organization", null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_logs"
    )
    user = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_logs"
    )
    # Historisé séparément : l'e-mail/rôle de l'utilisateur au moment de l'action
    # doit rester lisible même si le compte est ensuite modifié ou supprimé.
    user_email = models.EmailField(blank=True)
    user_role = models.CharField(max_length=20, blank=True)

    action = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    result = models.CharField(max_length=10, choices=Result.choices)
    details_erreur = models.CharField(max_length=255, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["tenant", "timestamp"]),
            models.Index(fields=["action", "timestamp"]),
        ]

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] {self.action} ({self.result})"

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Le journal d'audit est en écriture seule (RM-SEC-002).")
