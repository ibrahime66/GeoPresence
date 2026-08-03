"""
Settings pour l'environnement de production.

Placeholder minimal pour l'instant — sera complété au sprint dédié au déploiement
(TLS obligatoire, HSTS, cookies secure, WhiteNoise, Sentry, etc. décrits dans
docs/ANALYSE-TECHNIQUE.md, chapitres 6, 7 et 18). Ne pas déployer en l'état.
"""

from .base import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CDC §13.5/§13.6 — n'a de sens que derrière HTTPS, donc absent de base.py.
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
