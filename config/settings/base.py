"""
Django settings communs à tous les environnements (development, staging, production).
Ne jamais mettre de secrets en dur ici : tout passe par les variables d'environnement (.env).
"""

from pathlib import Path

import environ

# BASE_DIR pointe vers la racine du projet (contient manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")

# Clé de chiffrement des champs sensibles (RM-SEC-004) — distincte de SECRET_KEY
# à dessein : une rotation de SECRET_KEY (déconnecte les sessions) ne doit
# jamais rendre les données chiffrées illisibles, et inversement.
FIELD_ENCRYPTION_KEY = env("FIELD_ENCRYPTION_KEY")

DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])


# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
]

# Les apps métier restantes (agencies, employees, attendance, ...) seront ajoutées
# ici sprint par sprint, au fur et à mesure de leur création.
LOCAL_APPS = [
    "apps.core",
    "apps.tenants",
    "apps.accounts",
    "apps.audit",
    "apps.agencies",
    "apps.departments",
    "apps.employees",
    "apps.schedules",
    "apps.attendance",
    "apps.leaves",
    "apps.absences",
    "apps.superadmin",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "accounts:login"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # MessageMiddleware doit précéder tout middleware qui appelle messages.*()
    # (TenantMiddleware signale une organisation suspendue via messages.error) —
    # sinon request._messages n'existe pas encore et l'appel lève MessageFailure.
    "django.contrib.messages.middleware.MessageMiddleware",
    "apps.tenants.middleware.TenantMiddleware",
    "apps.accounts.middleware.ForcePasswordChangeMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Middlewares custom restants (SecurityHeadersMiddleware, AuditMiddleware
    # générique) seront insérés ici quand ils seront développés.
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database — MySQL 8 / InnoDB (imposé par le CDC)
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        "CONN_MAX_AGE": 60,
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Password hashing — Argon2id imposé par le CDC §13.2.2.

PASSWORD_HASHERS = [
    "apps.accounts.hashers.PresenceArgon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]


# Password validation — règles de complexité CDC §13.2.1.
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "apps.accounts.validators.UppercaseValidator"},
    {"NAME": "apps.accounts.validators.LowercaseValidator"},
    {"NAME": "apps.accounts.validators.DigitValidator"},
    {"NAME": "apps.accounts.validators.SpecialCharacterValidator"},
    {"NAME": "apps.accounts.validators.PersonalInfoValidator"},
]


# Internationalization — le CDC impose FR / EN / AR (dont RTL)
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "fr"

# Les timestamps (pointages, audit) sont stockés en UTC et convertis à l'affichage
# selon le fuseau horaire de chaque organisation.
TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = [BASE_DIR / "locale"]


# Static & media files

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


# Sessions & cookies — CDC §5.6.1. SESSION_COOKIE_SECURE/CSRF_COOKIE_SECURE
# passent à True en staging/production (nécessite HTTPS, absent en dev local).

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SAMESITE = "Strict"
# Approxime l'expiration par inactivité (CDC : 30 min par défaut) en repoussant
# l'expiration à chaque requête. La durée absolue de session (8h employé / 2h
# admin) est fixée explicitement au login via request.session.set_expiry().
SESSION_SAVE_EVERY_REQUEST = True


# E-mail — SMTP réel (Gmail par défaut) si EMAIL_HOST_USER est renseigné dans
# .env, sinon repli sur la console (rien n'est réellement envoyé). C'est ce
# repli qui explique qu'aucun e-mail n'était jamais reçu jusqu'ici : le
# backend "console" se contente d'afficher le message dans le terminal.
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@geopresence.local")

EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
    EMAIL_PORT = env.int("EMAIL_PORT", default=587)
    EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Messages framework — aligne les tags Django sur les classes d'alerte Bootstrap 5.
from django.contrib.messages import constants as message_constants  # noqa: E402

MESSAGE_TAGS = {
    message_constants.ERROR: "danger",
}
