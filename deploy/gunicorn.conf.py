"""Config Gunicorn — lancé par le service systemd deploy/geopresence.service.
Écoute en local uniquement (127.0.0.1) : seul Nginx, sur la même machine,
doit pouvoir parler à Gunicorn — jamais exposé directement sur Internet."""

import multiprocessing

bind = "127.0.0.1:8000"

# Formule standard Gunicorn (2 x CPU + 1) — largement suffisant pour une PME,
# à revoir seulement si `htop` montre les workers saturés en usage réel.
workers = multiprocessing.cpu_count() * 2 + 1

# Tue et redémarre un worker qui bloque plus de 30s (ex. requête base de
# données qui ne répond plus) — évite qu'une requête lente gèle un worker
# indéfiniment.
timeout = 30

accesslog = "-"
errorlog = "-"
