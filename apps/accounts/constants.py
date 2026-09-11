# Constantes plateforme qui ne dépendent pas de l'organisation. Les seuils
# de blocage/session/mot de passe eux-mêmes sont désormais des paramètres
# PAR ORGANISATION — cf. apps.tenants.org_settings (CDC §6.4.3) — plus des
# constantes fixes ici.

# Un deuxième verrouillage consécutif (ou plus) est considéré comme "répété"
# et déclenche une alerte aux Administrateurs de l'organisation.
REPEATED_LOCKOUT_THRESHOLD = 2

# CDC §13.4 : CAPTCHA après 3 tentatives échouées sur un même e-mail.
CAPTCHA_FAILURE_THRESHOLD = 3

# CDC §13.3.1 : limitation de débit anti brute-force globale par IP — compte
# les ÉCHECS de connexion uniquement (pas les tentatives réussies, cf. audit
# perf/charge de 2026-09 : de nombreux employés derrière une même IP
# partagée — box d'agence, Wi-Fi d'école... — ne doivent jamais se bloquer
# mutuellement en se connectant normalement). Le verrouillage de compte
# (max_failed_login_attempts, par organisation) et le CAPTCHA par e-mail
# restent la défense principale contre le brute-force ciblé ; ce seuil-ci ne
# fait que couper un scan massif depuis une seule IP.
LOGIN_RATE_LIMIT_MAX_ATTEMPTS = 30
LOGIN_RATE_LIMIT_WINDOW_SECONDS = 60

# Audit sécurité §6 : demandes de réinitialisation de mot de passe par IP.
PWRESET_RATE_LIMIT_MAX = 5
PWRESET_RATE_LIMIT_WINDOW = 3600

PASSWORD_RESET_TOKEN_LIFETIME_MINUTES = 30

# CDC §13.2.1 : avertissement d'expiration — nombre de jours avant échéance,
# fixe (contrairement à la durée d'expiration elle-même, configurable par organisation).
PASSWORD_EXPIRATION_WARNING_DAYS = 7

ADMIN_ROLES = {"SUPER_ADMIN", "ADMIN"}
