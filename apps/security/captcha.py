"""CAPTCHA hCaptcha (CDC §13.4) — s'affiche après N échecs de connexion et
sur les formulaires publics sensibles (réinitialisation de mot de passe).

hCaptcha est choisi plutôt que Google reCAPTCHA (les deux sont autorisés par
le CDC) car il ne nécessite pas de dépendance Python supplémentaire : la
vérification est un simple appel HTTP à leur API `siteverify`.
"""

import json
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.cache import cache

CACHE_PREFIX = "captcha_fail"
VERIFY_URL = "https://hcaptcha.com/siteverify"
FAILURE_WINDOW_SECONDS = 15 * 60


def is_enabled():
    """Le CAPTCHA est « activable/désactivable par l'Administrateur » (CDC
    §13.4) : en V1, ce réglage est encore une clé de plateforme (variables
    d'environnement HCAPTCHA_SITE_KEY/HCAPTCHA_SECRET_KEY) plutôt qu'un
    paramètre par organisation — tant qu'elles sont vides, l'étape CAPTCHA
    est neutralisée partout au lieu de bloquer les connexions."""
    return bool(getattr(settings, "HCAPTCHA_SITE_KEY", "") and getattr(settings, "HCAPTCHA_SECRET_KEY", ""))


def register_failure(identity):
    cache_key = f"{CACHE_PREFIX}:{identity}"
    try:
        cache.incr(cache_key)
    except ValueError:
        cache.set(cache_key, 1, timeout=FAILURE_WINDOW_SECONDS)


def reset(identity):
    cache.delete(f"{CACHE_PREFIX}:{identity}")


def is_required(identity, *, threshold):
    return cache.get(f"{CACHE_PREFIX}:{identity}", 0) >= threshold


def verify(response_token, remote_ip):
    """Vérifie un jeton hCaptcha auprès de l'API `siteverify`.

    Renvoie toujours True si le CAPTCHA n'est pas configuré (voir
    `is_enabled`). Si le service hCaptcha est injoignable, échoue fermé
    (refuse) plutôt que d'ouvrir une brèche de contournement (Zero Trust,
    CDC §13.1)."""
    if not is_enabled():
        return True
    if not response_token:
        return False

    payload = urllib.parse.urlencode(
        {
            "secret": settings.HCAPTCHA_SECRET_KEY,
            "response": response_token,
            "remoteip": remote_ip or "",
        }
    ).encode()

    try:
        with urllib.request.urlopen(VERIFY_URL, data=payload, timeout=5) as resp:
            result = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return False

    return bool(result.get("success"))
