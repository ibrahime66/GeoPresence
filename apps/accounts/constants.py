# Constantes plateforme qui ne dépendent pas de l'organisation. Les seuils
# de blocage/session/mot de passe eux-mêmes sont désormais des paramètres
# PAR ORGANISATION — cf. apps.tenants.org_settings (CDC §6.4.3) — plus des
# constantes fixes ici.

# Un deuxième verrouillage consécutif (ou plus) est considéré comme "répété"
# et déclenche une alerte aux Administrateurs de l'organisation.
REPEATED_LOCKOUT_THRESHOLD = 2

# CDC §13.4 : CAPTCHA après 3 tentatives échouées sur un même e-mail.
CAPTCHA_FAILURE_THRESHOLD = 3

# CDC §13.3.1 : limitation de débit — max 10 tentatives de connexion par
# minute et par IP (protection anti brute-force globale, pas un paramètre
# métier par organisation).
LOGIN_RATE_LIMIT_MAX_ATTEMPTS = 10
LOGIN_RATE_LIMIT_WINDOW_SECONDS = 60

# Audit sécurité §6 : demandes de réinitialisation de mot de passe par IP.
PWRESET_RATE_LIMIT_MAX = 5
PWRESET_RATE_LIMIT_WINDOW = 3600

PASSWORD_RESET_TOKEN_LIFETIME_MINUTES = 30

# CDC §13.2.1 : avertissement d'expiration — nombre de jours avant échéance,
# fixe (contrairement à la durée d'expiration elle-même, configurable par organisation).
PASSWORD_EXPIRATION_WARNING_DAYS = 7

ADMIN_ROLES = {"SUPER_ADMIN", "ADMIN"}
