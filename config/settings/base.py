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

# Sauvegardes (CDC §18.4) — clé AES-256 dédiée (encore une fois distincte des
# deux précédentes : la compromission/rotation d'une clé ne doit jamais
# rendre les deux autres catégories de données illisibles). 32 octets bruts,
# encodés en base64 — générer avec :
#   python -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
BACKUP_ENCRYPTION_KEY = env("BACKUP_ENCRYPTION_KEY", default="")
# `or` plutôt qu'un simple `default=` : une variable présente mais vide dans
# .env (cf. .env.example) doit retomber sur le chemin par défaut, pas pointer
# vers un Path("") (= répertoire courant).
BACKUP_DIR = env("BACKUP_DIR", default="") or str(BASE_DIR / "backups")
# CDC §18.4.3 : « au moins deux emplacements distincts ». Laisser vide tant
# qu'aucun second emplacement (volume distant, bucket...) n'est monté —
# la sauvegarde reste alors valide mais sur un seul emplacement local.
BACKUP_SECONDARY_DIR = env("BACKUP_SECONDARY_DIR", default="")

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
    "apps.security",
    "apps.agencies",
    "apps.departments",
    "apps.employees",
    "apps.schedules",
    "apps.attendance",
    "apps.leaves",
    "apps.absences",
    "apps.superadmin",
    "apps.backups",
    "apps.ai",
    "apps.announcements",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "core:home"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # LocaleMiddleware doit se trouver après SessionMiddleware et avant
    # CommonMiddleware (exigence Django) — détecte la langue depuis la
    # session/le cookie/l'en-tête Accept-Language pour les visiteurs anonymes
    # (page de connexion...). UserLanguageMiddleware la surcharge ensuite avec
    # la préférence enregistrée dès qu'un utilisateur est authentifié.
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.accounts.middleware.UserLanguageMiddleware",
    # MessageMiddleware doit précéder tout middleware qui appelle messages.*()
    # (TenantMiddleware signale une organisation suspendue via messages.error) —
    # sinon request._messages n'existe pas encore et l'appel lève MessageFailure.
    "django.contrib.messages.middleware.MessageMiddleware",
    "apps.tenants.middleware.TenantMiddleware",
    "apps.accounts.middleware.ForcePasswordChangeMiddleware",
    "apps.accounts.middleware.SessionActivityMiddleware",
    "apps.security.middleware.SecurityHeadersMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Middleware custom restant (AuditMiddleware générique) sera inséré ici
    # quand il sera développé.
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
                "django.template.context_processors.i18n",
                "apps.core.context_processors.sidebar_counts",
                "apps.core.context_processors.org_modules",
                "apps.core.context_processors.org_branding",
                "apps.core.context_processors.ai_sidebar",
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
    {"NAME": "apps.accounts.validators.PasswordHistoryValidator"},
    {"NAME": "apps.accounts.validators.OrgMinimumLengthValidator"},
]


# Internationalization — le CDC impose FR / EN / AR (dont RTL)
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "fr"

# CDC §24.2. La couverture de traduction est partielle en V1 (structure de
# l'app + parcours de connexion/profil) — voir locale/README.md pour le
# périmètre exact et comment l'étendre.
LANGUAGES = [
    ("fr", "Français"),
    ("en", "English"),
    ("ar", "العربية"),
]
# Langues à écriture de droite à gauche — pilote l'attribut dir="rtl" sur
# <html> (cf. templates/base.html et auth_base.html) et les surcharges CSS
# [dir="rtl"] dans static/css/main.css.
LANGUAGES_BIDI = ["ar"]

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


# En-têtes de sécurité HTTP — CDC §13.5. X-Content-Type-Options et
# X-Frame-Options sont déjà à leurs valeurs sûres par défaut dans Django
# (SecurityMiddleware / XFrameOptionsMiddleware) ; Content-Security-Policy et
# Permissions-Policy sont ajoutés par apps.security.middleware.SecurityHeadersMiddleware
# (pas de support natif dans Django 4.2). HSTS reste réservé à production.py
# (n'a de sens que derrière HTTPS).
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# CAPTCHA hCaptcha (CDC §13.4) — voir apps/security/captcha.py. Laisser vide
# désactive le CAPTCHA partout (pratique en dev local).
HCAPTCHA_SITE_KEY = env("HCAPTCHA_SITE_KEY", default="")
HCAPTCHA_SECRET_KEY = env("HCAPTCHA_SECRET_KEY", default="")

# Assistant GeoIA (CDC §15) — configuration serveur uniquement, jamais via une
# page web : la clé API d'un fournisseur tiers ne doit jamais transiter par un
# formulaire navigateur ni être stockée en base. Laisser AI_API_KEY vide
# désactive l'assistant partout (comportement par défaut en dev local).
AI_ENABLED = env.bool("AI_ENABLED", default=False)
AI_PROVIDER = env("AI_PROVIDER", default="OPENAI")
AI_API_KEY = env("AI_API_KEY", default="")
AI_MODEL = env("AI_MODEL", default="gpt-4o-mini")
AI_TEMPERATURE = env.float("AI_TEMPERATURE", default=0.3)
AI_LANGUAGE = env("AI_LANGUAGE", default="fr")
AI_ROLES_ALLOWED = env.list(
    "AI_ROLES_ALLOWED", default=["SUPER_ADMIN", "ADMIN", "MANAGER", "EMPLOYEE"]
)
AI_MONTHLY_QUOTA = env.int("AI_MONTHLY_QUOTA", default=500)
AI_HISTORY_RETENTION_DAYS = env.int("AI_HISTORY_RETENTION_DAYS", default=30)


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
