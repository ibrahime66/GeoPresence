from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def paginate_url(context, page_number):
    """Reconstruit l'URL de pagination en préservant les filtres déjà présents
    dans la query string (ex. `?tenant=...&action=...`) tout en remplaçant
    uniquement `page` — un `request.GET.urlencode` brut dupliquerait ce
    paramètre au lieu de l'écraser."""
    params = context["request"].GET.copy()
    params["page"] = page_number
    return f"?{params.urlencode()}"
