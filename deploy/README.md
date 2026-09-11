# Déploiement GeoPresence sur un VPS Ubuntu 22.04

Procédure pour un VPS neuf (testée pour un seul serveur — Nginx + Gunicorn +
MySQL + Redis, tous sur la même machine). Toutes les commandes précédées de
`#` s'exécutent en `root`, celles précédées de `$` sous l'utilisateur
`geopresence`.

## 1. Nom de domaine (important, à lire avant de commencer)

Le site force le HTTPS en production (`SECURE_SSL_REDIRECT`), et un
certificat HTTPS gratuit (Let's Encrypt) exige un **nom de domaine** — pas
une simple adresse IP.

- **Tu as déjà un domaine** → pointe un enregistrement DNS `A` vers l'IP du
  VPS, utilise ce domaine partout ci-dessous.
- **Pas encore de domaine, juste pour tester** → utilise un domaine gratuit
  basé sur ton IP via [nip.io](https://nip.io) : si l'IP du VPS est
  `203.0.113.10`, ton "domaine" est `203-0-113-10.nip.io`. Ça résout
  automatiquement vers l'IP et Let's Encrypt l'accepte sans problème.

## 2. Paquets système

```
# apt update && apt upgrade -y
# apt install -y python3-venv python3-dev build-essential pkg-config \
    libmysqlclient-dev git nginx redis-server mysql-server \
    certbot python3-certbot-nginx
```

⚠️ Ne jamais installer `libmariadb3` ni `default-libmysqlclient-dev` — ça
force la désinstallation de `mysql-server` (conflit apt). Utiliser uniquement
`libmysqlclient-dev` comme ci-dessus.

## 3. Base de données

```
# mysql_secure_installation
# mysql -u root -p
```
```sql
CREATE DATABASE geopresence_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'geopresence'@'localhost' IDENTIFIED BY 'UN_MOT_DE_PASSE_FORT';
GRANT ALL PRIVILEGES ON geopresence_db.* TO 'geopresence'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 4. Utilisateur système + code

```
# adduser --system --group --home /home/geopresence --shell /bin/bash geopresence
# su - geopresence
$ git clone git@github.com:ibrahime66/GeoPresence.git app
$ cd app
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements/production.txt
```

(Si le clone SSH échoue faute de clé déployée sur GitHub, transférer le code
depuis ta machine avec `rsync -av --exclude venv --exclude staticfiles ./ geopresence@IP:/home/geopresence/app/`.)

## 5. Configuration (`.env`)

```
$ cp deploy/.env.production.example .env
$ nano .env
```

Renseigner au minimum : `DJANGO_SECRET_KEY`, `FIELD_ENCRYPTION_KEY`,
`DJANGO_ALLOWED_HOSTS` (ton domaine, cf. étape 1), `DB_PASSWORD`,
`BACKUP_ENCRYPTION_KEY`. Les commandes pour générer chaque clé sont dans les
commentaires du fichier.

## 6. Base de données Django + fichiers statiques

`manage.py` lit `.env` (donc `DJANGO_SETTINGS_MODULE=config.settings.production`)
avant de choisir les réglages — pas besoin d'exporter quoi que ce soit à la main.

```
$ python manage.py migrate
$ python manage.py collectstatic --noinput
$ python manage.py createsuperuser
```

## 7. Gunicorn (service systemd)

```
# cp /home/geopresence/app/deploy/geopresence.service /etc/systemd/system/
# systemctl daemon-reload
# systemctl enable --now geopresence
# systemctl status geopresence
```

## 8. Nginx

```
# cp /home/geopresence/app/deploy/nginx.conf /etc/nginx/sites-available/geopresence
# nano /etc/nginx/sites-available/geopresence   # remplacer TON_DOMAINE
# ln -s /etc/nginx/sites-available/geopresence /etc/nginx/sites-enabled/
# rm /etc/nginx/sites-enabled/default
# nginx -t
# systemctl reload nginx
```

## 9. HTTPS

```
# certbot --nginx -d TON_DOMAINE
```

Certbot modifie automatiquement la config Nginx pour rediriger vers HTTPS et
programme le renouvellement automatique.

## 10. Vérification

- `https://TON_DOMAINE/health/` doit répondre `{"status": "healthy", ...}`.
- `https://TON_DOMAINE/accounts/login/` doit afficher la page de connexion.

## Mettre à jour le site après une modification du code

```
$ cd /home/geopresence/app
$ git pull
$ source venv/bin/activate
$ pip install -r requirements/production.txt
$ python manage.py migrate
$ python manage.py collectstatic --noinput
# systemctl reload geopresence
```

`reload` (HUP) recharge Gunicorn **sans coupure** : la socket reste ouverte,
les workers finissent leurs requêtes en cours. À utiliser pour tout
déploiement de code/templates.

Un `systemctl restart` complet (≈ 2 s d'indisponibilité, erreurs 502 pour les
visiteurs en cours de navigation) n'est nécessaire **que** si `deploy/gunicorn.conf.py`
ou le fichier `.env` ont changé.
