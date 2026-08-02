# Valeurs par défaut de la plateforme (CDC §6.4.3 / §13.3.1). Deviendront des
# paramètres configurables par organisation quand le modèle OrganizationSettings
# sera construit — pour l'instant, valeurs plateforme fixes.

MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

PASSWORD_RESET_TOKEN_LIFETIME_MINUTES = 30

SESSION_DURATION_ADMIN_SECONDS = 2 * 3600
SESSION_DURATION_DEFAULT_SECONDS = 8 * 3600

ADMIN_ROLES = {"SUPER_ADMIN", "ADMIN"}
