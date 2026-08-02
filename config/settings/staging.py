"""
Settings pour l'environnement de staging.

Placeholder minimal pour l'instant — sera complété au sprint dédié au déploiement
(Docker, Nginx, headers de sécurité HTTPS, Sentry, etc. décrits dans
docs/ANALYSE-TECHNIQUE.md, chapitres 6, 7 et 18).
"""

from .base import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
