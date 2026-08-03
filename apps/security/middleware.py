"""CDC §13.5 : en-têtes HTTP de sécurité absents du cœur de Django.

Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options et
Referrer-Policy sont déjà couverts par SecurityMiddleware/XFrameOptionsMiddleware
via les réglages SECURE_* (voir config/settings) — pas besoin de les
dupliquer ici. Ce middleware ajoute ce que Django 4.2 ne fournit pas
nativement : Content-Security-Policy, Permissions-Policy, et le
Cache-Control: no-store sur les pages authentifiées.
"""

CSP_DIRECTIVES = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://hcaptcha.com https://*.hcaptcha.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
    "font-src 'self' https://fonts.gstatic.com; "
    # CDC §7.4 : tuiles OpenStreetMap (carte interactive agences).
    "img-src 'self' data: https://*.tile.openstreetmap.org; "
    # CDC §7.4 : Nominatim (géocodage d'adresse -> coordonnées GPS).
    "connect-src 'self' https://hcaptcha.com https://*.hcaptcha.com https://nominatim.openstreetmap.org; "
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
