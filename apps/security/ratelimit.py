"""Limitation de débit par IP (CDC §13.3.1 : max 10 tentatives/minute/IP).

Basé sur le cache Django (LocMemCache en dev, Redis prévu en production —
cf. ANALYSE-TECHNIQUE §2.2). Le compteur est une simple fenêtre fixe : le
premier appel pour une clé pose le TTL, les suivants l'incrémentent sans le
renouveler, donc la fenêtre glisse au maximum de `window_seconds` secondes.
"""

from django.core.cache import cache

CACHE_PREFIX = "ratelimit"


def get_client_ip(request):
    return request.META.get("REMOTE_ADDR")


def hit(bucket, key, *, limit, window_seconds):
    """Enregistre une tentative pour `key` dans `bucket` et indique si la
    limite est dépassée. Retourne True si la tentative doit être bloquée."""
    cache_key = f"{CACHE_PREFIX}:{bucket}:{key}"
    try:
        count = cache.incr(cache_key)
    except ValueError:
        cache.set(cache_key, 1, timeout=window_seconds)
        count = 1
    return count > limit
