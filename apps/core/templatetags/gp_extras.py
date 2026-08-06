import os

from django import template
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage

register = template.Library()


@register.simple_tag
def static_v(path):
    """Comme {% static %}, mais avec `?v=<mtime>` en suffixe — force le
    navigateur (et le service worker, dont le cache fait correspondance
    exacte d'URL) à refaire une requête réseau dès que le fichier change sur
    disque, sans dépendre d'un versionnage manuel du service worker ni d'un
    vidage de cache côté utilisateur."""
    url = staticfiles_storage.url(path)
    absolute_path = finders.find(path)
    if not absolute_path:
        return url
    try:
        version = int(os.path.getmtime(absolute_path))
    except OSError:
        return url
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}v={version}"


@register.simple_tag(takes_context=True)
def paginate_url(context, page_number):
    """Reconstruit l'URL de pagination en préservant les filtres déjà présents
    dans la query string (ex. `?tenant=...&action=...`) tout en remplaçant
    uniquement `page` — un `request.GET.urlencode` brut dupliquerait ce
    paramètre au lieu de l'écraser."""
    params = context["request"].GET.copy()
    params["page"] = page_number
    return f"?{params.urlencode()}"
