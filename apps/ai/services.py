"""CDC §15.3.3/§15.4 : orchestration de l'assistant conversationnel — sélection
du provider, application du quota et des rôles autorisés, journalisation de
chaque requête (audit + log dédié), avant de déléguer l'appel réseau lui-même
à apps.ai.providers.

Configuration exclusivement côté serveur (settings.AI_*, sourcés de .env) —
aucune page web ne permet de saisir ou d'afficher la clé API : elle ne
transite jamais par le navigateur ni n'est stockée en base (cf. discussion
avec l'utilisateur, la clé d'un fournisseur tiers est aussi sensible qu'un
mot de passe applicatif)."""

import json
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.audit import services as audit

from . import context as ai_context
from .models import AIConversation, AIMessage, AIRequestLog
from .providers import AIProviderError, get_provider


MAX_HISTORY_MESSAGES = 12  # derniers messages ré-envoyés comme historique de conversation.

# Marqueur de fin de réponse suivi d'un tableau JSON de suggestions — jamais
# affiché tel quel : apps.ai.services._split_answer_and_suggestions le
# découpe avant stockage/affichage (cf. ask()).
SUGGESTIONS_MARKER = "###SUGGESTIONS###"

SYSTEM_PROMPT_HEADER = (
    "Tu es GeoIA, l'assistant intégré à GeoPresence, une plateforme de gestion "
    "de présence. Réponds UNIQUEMENT à partir des données de contexte fournies "
    "ci-dessous — n'invente jamais de chiffre. Si l'information demandée n'y "
    "figure pas, dis-le clairement plutôt que de deviner. Sois concis. "
    "Réponds dans la langue suivante : {language}.\n\n"
    "Termine TOUJOURS ta réponse par la ligne exacte {marker} suivie d'un "
    "tableau JSON (et rien d'autre après) de 3 courtes questions de suivi "
    "pertinentes que l'utilisateur pourrait poser ensuite, dans la même langue. "
    'Exemple de fin : {marker}\n["Question 1 ?", "Question 2 ?", "Question 3 ?"]'
    "\n\n--- Données ---\n{context}"
)

LANGUAGE_LABELS = {"fr": "Français", "en": "English", "ar": "العربية"}

STARTER_SUGGESTIONS = {
    "EMPLOYEE": [
        "Quel est mon solde de congés ?",
        "Ai-je des retards ce mois-ci ?",
        "Quel était mon dernier pointage ?",
    ],
    "MANAGER": [
        "Combien de membres de mon équipe sont présents aujourd'hui ?",
        "Ai-je des demandes de congé en attente ?",
        "Qui a le plus de retards dans mon équipe ce mois-ci ?",
    ],
    "ADMIN": [
        "Quel est le taux de présence de l'organisation aujourd'hui ?",
        "Combien de demandes de congé sont en attente ?",
        "Qui sont les employés avec le plus de retards ce mois-ci ?",
    ],
    "SUPER_ADMIN": [
        "Combien d'organisations sont actives sur la plateforme ?",
        "Combien de pointages ont eu lieu aujourd'hui, toutes organisations confondues ?",
        "Y a-t-il des organisations suspendues ?",
    ],
}


def get_starter_suggestions(user):
    """Questions proposées au démarrage d'une nouvelle conversation (avant
    tout échange) — statiques par rôle, contrairement aux suggestions de
    suivi qui sont générées dynamiquement par le modèle (cf. ask())."""
    return STARTER_SUGGESTIONS.get(user.role, [])


def _split_answer_and_suggestions(raw_text):
    """Sépare le texte de réponse affiché des suggestions de suivi générées
    par le modèle (cf. SYSTEM_PROMPT_HEADER). Best-effort : si le modèle n'a
    pas respecté le format, on garde tout le texte tel quel plutôt que de
    perdre du contenu, et on renvoie une liste de suggestions vide."""
    if SUGGESTIONS_MARKER not in raw_text:
        return raw_text.strip(), []

    answer, _, tail = raw_text.partition(SUGGESTIONS_MARKER)
    # Tolère tout ce que le modèle place entre le marqueur et le tableau JSON
    # (retour à la ligne réel, espace, ou séquence d'échappement littérale
    # mal formée) — on repart du premier "[" trouvé plutôt que d'exiger un
    # format exact.
    bracket_index = tail.find("[")
    if bracket_index == -1:
        return raw_text.strip(), []

    try:
        suggestions = json.loads(tail[bracket_index:].strip())
        if not isinstance(suggestions, list):
            return raw_text.strip(), []
        suggestions = [str(s).strip() for s in suggestions if str(s).strip()][:3]
    except (ValueError, TypeError):
        return raw_text.strip(), []

    return answer.strip(), suggestions


class AIQuotaExceeded(Exception):
    pass


class AINotAvailable(Exception):
    pass


def is_configured():
    return bool(settings.AI_ENABLED and settings.AI_API_KEY)


def is_ai_available(user):
    if not is_configured():
        return False
    return user.role in (settings.AI_ROLES_ALLOWED or [])


def _quota_scope(user):
    return None if user.role == "SUPER_ADMIN" else user.tenant


def check_quota(user):
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    used = AIRequestLog.objects.filter(
        tenant=_quota_scope(user), kind=AIRequestLog.Kind.CHAT, created_at__gte=month_start,
    ).count()
    if used >= settings.AI_MONTHLY_QUOTA:
        raise AIQuotaExceeded(f"Quota mensuel de {settings.AI_MONTHLY_QUOTA} requêtes GeoIA atteint pour ce mois.")


def ask(user, conversation, question, request=None):
    """Pose `question` dans `conversation`, journalise et renvoie le texte de
    réponse. Lève AINotAvailable / AIQuotaExceeded / AIProviderError — à
    charge de la vue de les transformer en message utilisateur."""
    tenant = None if user.role == "SUPER_ADMIN" else user.tenant
    if not is_configured():
        raise AINotAvailable("GeoIA n'est pas configuré sur cette instance.")
    if user.role not in (settings.AI_ROLES_ALLOWED or []):
        raise AINotAvailable("Votre rôle n'a pas accès à GeoIA.")

    check_quota(user)

    system_prompt = SYSTEM_PROMPT_HEADER.format(
        language=LANGUAGE_LABELS.get(settings.AI_LANGUAGE, settings.AI_LANGUAGE),
        context=ai_context.build_context(user),
        marker=SUGGESTIONS_MARKER,
    )
    history = list(conversation.messages.order_by("-created_at")[:MAX_HISTORY_MESSAGES])[::-1]
    messages = [{"role": "system", "content": system_prompt}]
    for m in history:
        messages.append({"role": "user" if m.role == AIMessage.Role.USER else "assistant", "content": m.content})
    messages.append({"role": "user", "content": question})

    AIMessage.objects.create(conversation=conversation, role=AIMessage.Role.USER, content=question)

    try:
        provider = get_provider(settings.AI_PROVIDER, settings.AI_API_KEY)
        answer, tokens_used = provider.chat(messages, model=settings.AI_MODEL, temperature=settings.AI_TEMPERATURE)
    except AIProviderError as exc:
        AIRequestLog.objects.create(
            tenant=tenant, user=user, kind=AIRequestLog.Kind.CHAT, prompt_excerpt=question[:255],
            success=False, error_message=str(exc)[:255],
        )
        if request is not None:
            audit.log_event(
                request, audit.AI_QUESTION_ASKED, audit.AuditLog.Result.FAILURE, user=user, tenant=tenant,
                description="Question posée à GeoIA", error=str(exc)[:255],
            )
        raise

    answer, suggestions = _split_answer_and_suggestions(answer)
    AIMessage.objects.create(
        conversation=conversation, role=AIMessage.Role.ASSISTANT, content=answer,
        suggestions=suggestions, tokens_used=tokens_used,
    )
    conversation.save(update_fields=["updated_at"])
    if not conversation.title:
        conversation.title = question[:140]
        conversation.save(update_fields=["title"])

    AIRequestLog.objects.create(
        tenant=tenant, user=user, kind=AIRequestLog.Kind.CHAT, prompt_excerpt=question[:255],
        success=True, tokens_used=tokens_used,
    )
    if request is not None:
        audit.log_event(
            request, audit.AI_QUESTION_ASKED, audit.AuditLog.Result.SUCCESS, user=user, tenant=tenant,
            description="Question posée à GeoIA",
        )
    return answer


def purge_expired_conversations():
    """Cron quotidien (CDC §15.4 : historique conservé N jours) — supprime les
    conversations plus anciennes que settings.AI_HISTORY_RETENTION_DAYS."""
    cutoff = timezone.now() - timedelta(days=settings.AI_HISTORY_RETENTION_DAYS)
    deleted, _ = AIConversation.objects.filter(updated_at__lt=cutoff).delete()
    return deleted
