"""Settings pour le développement local."""

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# EMAIL_BACKEND est déterminé dynamiquement dans settings/base.py selon que
# EMAIL_HOST_USER/EMAIL_HOST_PASSWORD sont renseignés dans .env ou non.
