"""
Settings pour l'environnement de production (VPS unique : Nginx -> Gunicorn,
cf. deploy/README.md pour la procédure complète).
"""

from .base import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Audit sécurité §11 : Django 4.x valide l'en-tête Origin des requêtes POST
# HTTPS contre cette liste. Dérivé de DJANGO_ALLOWED_HOSTS (schéma https) pour
# ne pas maintenir deux listes en parallèle.
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if h]

# CDC §13.5/§13.6 — n'a de sens que derrière HTTPS, donc absent de base.py.
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Nginx termine le HTTPS et transmet en HTTP à Gunicorn (réseau local) — sans
# cet en-tête, Django croit que chaque requête est en clair et boucle sur
# SECURE_SSL_REDIRECT (redirection infinie).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Fichiers statiques compressés + noms hashés, servis par Gunicorn/WhiteNoise
# directement — pas besoin de configurer Nginx pour /static/. Doit rester
# juste après SecurityMiddleware (recommandation WhiteNoise), pas avant.
MIDDLEWARE = [MIDDLEWARE[0], "whitenoise.middleware.WhiteNoiseMiddleware"] + MIDDLEWARE[1:]  # noqa: F405
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Cache partagé entre les workers Gunicorn — indispensable pour que le rate
# limiting et le déclenchement du CAPTCHA (apps/security/ratelimit.py,
# apps/security/captcha.py) comptent juste : avec le cache mémoire par défaut,
# chaque worker aurait son propre compteur isolé.
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://127.0.0.1:6379/1"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# Suivi des erreurs (Sentry) — inactif tant que SENTRY_DSN est vide, pour ne
# pas bloquer un premier déploiement de test sans compte Sentry.
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        send_default_pii=False,
        traces_sample_rate=0.1,
    )

# Logs Gunicorn/systemd (journalctl -u geopresence) : erreurs applicatives et
# requêtes rejetées par SecurityMiddleware (hôte inconnu, etc.) visibles sans
# dépendre de Sentry.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}
