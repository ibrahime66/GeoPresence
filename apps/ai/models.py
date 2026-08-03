from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel

# CDC §15.2/§15.4 : le fournisseur, la clé API, le modèle, les rôles
# autorisés, le quota et la rétention sont des réglages serveur
# (settings.AI_*, sourcés de .env) — volontairement PAS de modèle de
# configuration en base : une clé API tierce ne doit jamais transiter par un
# formulaire web ni être stockée/affichée via le navigateur.


class AIConversation(UUIDModel, TimeStampedModel):
    """Fil de discussion avec l'assistant. tenant nullable pour les
    conversations du Super Admin (périmètre plateforme, CDC §15.3.3)."""

    tenant = models.ForeignKey(
        "tenants.Organization", on_delete=models.SET_NULL, related_name="+", null=True, blank=True, db_index=True,
    )
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="ai_conversations")
    title = models.CharField(max_length=140, blank=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["tenant", "user", "updated_at"])]

    def __str__(self):
        return self.title or str(self.id)


class AIMessage(UUIDModel):
    class Role(models.TextChoices):
        USER = "USER", "Utilisateur"
        ASSISTANT = "ASSISTANT", "Assistant"

    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    # Questions de suivi suggérées par le modèle à la fin de sa réponse
    # (ASSISTANT uniquement) — affichées comme boutons cliquables sous le
    # dernier message pour guider la conversation, cf. apps.ai.services.ask.
    suggestions = models.JSONField(default=list, blank=True)
    tokens_used = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class AIRequestLog(UUIDModel):
    """CDC §15.4 : traçabilité de toutes les requêtes IA (qui a demandé quoi,
    quand) — journal dédié (détail technique : tokens, échecs) distinct du
    journal d'audit global, qui reçoit en parallèle un événement résumé
    (cf. apps.audit.services, action AI_QUESTION_ASKED)."""

    class Kind(models.TextChoices):
        CHAT = "CHAT", "Question assistant"
        DAILY_SUMMARY = "DAILY_SUMMARY", "Résumé quotidien"

    tenant = models.ForeignKey(
        "tenants.Organization", on_delete=models.SET_NULL, related_name="+", null=True, blank=True, db_index=True,
    )
    user = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, related_name="+", null=True, blank=True,
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.CHAT)
    # Extrait tronqué de la question — pas la donnée complète envoyée au
    # fournisseur (CDC §15.4 : "le contexte envoyé à l'IA est strictement
    # limité", on n'en garde qu'un aperçu à des fins d'audit, pas une copie).
    prompt_excerpt = models.CharField(max_length=255, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.CharField(max_length=255, blank=True)
    tokens_used = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["tenant", "created_at"])]


class AIDailySummary(UUIDModel):
    """CDC §15.3.1 : résumé quotidien automatique (absences, retards,
    anomalies de la veille), généré par apps.ai.management.commands.
    generate_ai_daily_summary."""

    tenant = models.ForeignKey("tenants.Organization", on_delete=models.CASCADE, related_name="+")
    date = models.DateField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        constraints = [models.UniqueConstraint(fields=["tenant", "date"], name="ai_one_summary_per_tenant_day")]
