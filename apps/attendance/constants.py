# Valeurs par défaut de la plateforme (CDC §6.4.2). Un Schedule peut les
# surcharger (schedule.late_tolerance_minutes, etc.) ; sinon ces constantes
# s'appliquent. Deviendront configurables au niveau Organization plus tard.

DEFAULT_LATE_TOLERANCE_MINUTES = 5
DEFAULT_EARLY_LEAVE_TOLERANCE_MINUTES = 5
DEFAULT_OVERTIME_THRESHOLD_MINUTES = 15

# CDC §9.3.4 / ANALYSE-TECHNIQUE §10 : traitement de la photo côté serveur.
PHOTO_MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024
PHOTO_MAX_WIDTH = 640
PHOTO_MAX_HEIGHT = 480
PHOTO_JPEG_QUALITY = 85

# CDC §9.7.3 : délai max entre l'heure du pointage et sa synchronisation en mode hors ligne.
OFFLINE_SYNC_MAX_DELAY_HOURS = 48
