"""CDC §15.2 : couche d'abstraction fournisseur IA — chaque provider expose la
même interface `chat(messages, model, temperature) -> (text, tokens_used)`,
ce qui permet d'ajouter Anthropic/Mistral/Ollama plus tard (cf. models.py)
sans toucher au reste du module. Implémenté avec urllib (stdlib) plutôt que le
SDK officiel `openai` pour ne pas ajouter de dépendance tierce pour un seul
appel HTTP JSON."""

import json
import urllib.error
import urllib.request


class AIProviderError(Exception):
    """Erreur réseau/API du fournisseur — toujours interceptée par
    apps.ai.services et journalisée plutôt que remontée en 500."""


class _OpenAICompatibleProvider:
    """Base pour tout fournisseur exposant une API "chat completions" au
    format OpenAI (OpenAI lui-même, mais aussi OpenRouter, Mistral, etc.) —
    seuls l'URL de base et le nom affiché dans les messages d'erreur changent
    d'un sous-classe à l'autre."""

    api_base = None
    display_name = "IA"
    timeout_seconds = 30
    extra_headers = {}

    def __init__(self, api_key):
        if not api_key:
            raise AIProviderError(f"Aucune clé API {self.display_name} configurée.")
        self.api_key = api_key

    def chat(self, messages, model, temperature):
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": float(temperature),
            "max_tokens": 800,
        }).encode("utf-8")
        request = urllib.request.Request(
            self.api_base,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                **self.extra_headers,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            raise AIProviderError(f"Erreur {self.display_name} ({exc.code}) : {detail}") from exc
        except urllib.error.URLError as exc:
            raise AIProviderError(f"{self.display_name} injoignable : {exc.reason}") from exc

        try:
            text = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:
            raise AIProviderError(f"Réponse {self.display_name} inattendue (pas de contenu).") from exc
        tokens_used = data.get("usage", {}).get("total_tokens")
        return text, tokens_used


class OpenAIProvider(_OpenAICompatibleProvider):
    api_base = "https://api.openai.com/v1/chat/completions"
    display_name = "OpenAI"


class OpenRouterProvider(_OpenAICompatibleProvider):
    """https://openrouter.ai — agrégateur multi-modèles, API compatible
    OpenAI. Les identifiants de modèle sont préfixés par le fournisseur
    d'origine (ex. "openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet")."""

    api_base = "https://openrouter.ai/api/v1/chat/completions"
    display_name = "OpenRouter"
    extra_headers = {"X-Title": "GeoPresence"}


PROVIDERS = {
    "OPENAI": OpenAIProvider,
    "OPENROUTER": OpenRouterProvider,
}


def get_provider(provider_code, api_key):
    try:
        provider_class = PROVIDERS[provider_code]
    except KeyError as exc:
        raise AIProviderError(f"Fournisseur IA inconnu : {provider_code}") from exc
    return provider_class(api_key)
