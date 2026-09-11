"""Config Gunicorn — lancé par le service systemd deploy/geopresence.service.
Écoute en local uniquement (127.0.0.1) : seul Nginx, sur la même machine,
doit pouvoir parler à Gunicorn — jamais exposé directement sur Internet."""

import multiprocessing

bind = "127.0.0.1:8000"

# Formule standard Gunicorn (2 x CPU + 1) — largement suffisant pour une PME,
# à revoir seulement si `htop` montre les workers saturés en usage réel.
workers = multiprocessing.cpu_count() * 2 + 1

# Analyse de charge 2026-09 : sur le VPS actuel (1 vCPU), des workers `sync`
# (le défaut) ne traitent qu'UNE requête à la fois chacun — 3 workers = 3
# requêtes en vol max, alors que l'essentiel du temps d'une requête Django
# est de l'attente réseau (MySQL, Redis), pas du calcul. `gthread` fait
# tourner plusieurs requêtes par worker sur des threads : ~3 workers × 8
# threads = 24 requêtes en vol pour le même nombre de process (donc la même
# empreinte mémoire), sans rien changer au code applicatif (le contexte
# tenant thread-local d'apps.core.context est déjà par-thread et nettoyé en
# fin de requête, cf. TenantMiddleware).
worker_class = "gthread"
threads = 8

# Tue et redémarre un worker qui bloque plus de 30s (ex. requête base de
# données qui ne répond plus) — évite qu'une requête lente gèle un worker
# indéfiniment.
timeout = 30

accesslog = "-"
errorlog = "-"
