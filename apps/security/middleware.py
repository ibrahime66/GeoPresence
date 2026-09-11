"""CDC §13.5 : en-têtes HTTP de sécurité absents du cœur de Django.

Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options et
Referrer-Policy sont déjà couverts par SecurityMiddleware/XFrameOptionsMiddleware
via les réglages SECURE_* (voir config/settings) — pas besoin de les
dupliquer ici. Ce middleware ajoute ce que Django 4.2 ne fournit pas
nativement : Content-Security-Policy, Permissions-Policy, et le
Cache-Control: no-store sur les pages authentifiées.

`RealClientIPMiddleware` (ci-dessous) répare `REMOTE_ADDR` derrière le
reverse-proxy Nginx (audit sécurité §1) : sans lui, tout le code qui lit
`request.META["REMOTE_ADDR"]` (rate-limiting, journal d'audit, IP des
pointages, IP des sessions) ne voit que l'IP du proxy (127.0.0.1).
"""

from django.conf import settings

# IP des proxys de confiance : seul un `REMOTE_ADDR` dans cette liste autorise
# à faire confiance aux en-têtes X-Real-IP / X-Forwarded-For. Par défaut, le
# loopback (déploiement mono-serveur Nginx -> Gunicorn, cf. deploy/README.md).
TRUSTED_PROXY_IPS = getattr(settings, "TRUSTED_PROXY_IPS", ["127.0.0.1", "::1"])


class RealClientIPMiddleware:
    """Réécrit `request.META["REMOTE_ADDR"]` avec l'IP réelle du client quand
    la requête vient d'un proxy de confiance.

    On lit `X-Real-IP` (posé par Nginx à partir de `$remote_addr` — toujours
    l'IP du pair immédiat, donc du vrai client puisque Nginx est en bordure)
    plutôt que le premier élément de `X-Forwarded-For` : ce dernier est
    contrôlable par le client (Nginx APPEND son IP, l'attaquant peut préfixer
    une valeur falsifiée). En dernier recours, on prend le DERNIER élément de
    X-Forwarded-For (celui ajouté par notre proxy), jamais le premier.

    Ne fait rien si `REMOTE_ADDR` n'est pas un proxy de confiance : en
    développement (`runserver`, connexion directe) le comportement est
    inchangé, et une requête qui atteindrait Gunicorn sans passer par Nginx
    ne peut pas usurper d'IP."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        peer = request.META.get("REMOTE_ADDR")
        if peer in TRUSTED_PROXY_IPS:
            real_ip = request.META.get("HTTP_X_REAL_IP", "").strip()
            if not real_ip:
                forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
                real_ip = forwarded.split(",")[-1].strip() if forwarded else ""
            if real_ip:
                request.META["REMOTE_ADDR"] = real_ip
        return self.get_response(request)

CSP_DIRECTIVES = (
    "default-src 'self'; "
    # Google Analytics (GA4, pages vitrine publiques uniquement — voir
    # apps.core.context_processors.analytics) : gtag.js + balise de mesure.
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://hcaptcha.com https://*.hcaptcha.com "
    "https://www.googletagmanager.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
    "font-src 'self' https://fonts.gstatic.com; "
    # CDC §7.4 : tuiles OpenStreetMap (carte interactive agences).
    "img-src 'self' data: https://*.tile.openstreetmap.org; "
    # CDC §7.4 : Nominatim (géocodage d'adresse -> coordonnées GPS).
    "connect-src 'self' https://hcaptcha.com https://*.hcaptcha.com https://nominatim.openstreetmap.org "
    "https://www.google-analytics.com https://*.analytics.google.com https://www.googletagmanager.com; "
    "frame-src https://hcaptcha.com https://*.hcaptcha.com; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)

# CDC §13.5 : géolocalisation uniquement pour l'app elle-même (pointage via
# carte GPS interactive) — plus de photo au pointage, donc plus d'accès caméra.
PERMISSIONS_POLICY = "camera=(), geolocation=(self), microphone=()"

EXEMPT_PATH_PREFIXES = ("/static/", "/media/")


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path_info.startswith(EXEMPT_PATH_PREFIXES):
            return response

        response.setdefault("Content-Security-Policy", CSP_DIRECTIVES)
        response.setdefault("Permissions-Policy", PERMISSIONS_POLICY)

        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            response["Cache-Control"] = "no-store"

        return response
