from apps.absences.models import Absence
from apps.accounts.models import User
from apps.leaves.models import Leave

APPROVER_ROLES = (User.Role.MANAGER, User.Role.ADMIN)


def sidebar_counts(request):
    """Alimente les badges de la sidebar (congés/justificatifs à valider) sur
    toutes les pages authentifiées — mêmes règles de périmètre que
    `leaves.PendingLeavesView`/`absences.PendingAbsencesView` (un Manager ne
    voit que sa propre équipe)."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated or user.role not in APPROVER_ROLES:
        return {}
    tenant = user.tenant
    if tenant is None:
        return {}

    leaves_qs = Leave.objects.all_tenants().filter(tenant=tenant, status=Leave.Status.PENDING)
    absences_qs = Absence.objects.all_tenants().filter(tenant=tenant, status=Absence.Status.PENDING_REVIEW)
    if user.role == User.Role.MANAGER:
        leaves_qs = leaves_qs.filter(employee__manager=user)
        absences_qs = absences_qs.filter(employee__manager=user)

    return {
        "pending_leaves_count": leaves_qs.count(),
        "pending_absences_count": absences_qs.count(),
    }


def org_modules(request):
    """Modules activables par organisation (CDC §6.4 étendu) — ex.
    Départements masqué pour une structure plate (pharmacie...). Le type
    d'organisation ne fait que suggérer une valeur par défaut à la création
    (cf. apps.tenants.org_settings.TYPE_DEFAULTS), ce réglage reste modifiable
    ensuite depuis Paramètres.

    Généré à partir de `apps.tenants.org_settings.MODULES` : ajouter un futur
    module qui masque un lien de menu + un champ de formulaire ne demande
    qu'une entrée dans ce registre, pas une modification ici ni dans
    base.html — cf. le commentaire en tête de MODULES."""
    from apps.tenants.org_settings import MODULES

    user = getattr(request, "user", None)
    authenticated_tenant = user.tenant if (user and user.is_authenticated) else None

    from apps.tenants.org_settings import get_org_setting

    enabled = {module["key"]: get_org_setting(authenticated_tenant, module["key"]) for module in MODULES}

    sidebar_links = [
        {
            "enabled": enabled[module["key"]],
            "label": module["sidebar_label"],
            "icon": module["sidebar_icon"],
            "url_name": module["sidebar_url"],
            "match_namespace": module.get("sidebar_match_namespace"),
            "match_url_name": module.get("sidebar_match_url_name"),
        }
        for module in MODULES
    ]

    return {**enabled, "module_sidebar_links": sidebar_links}


def _relative_luminance(hex_color):
    """Formule WCAG de luminance relative — sert uniquement à choisir un texte
    lisible (blanc ou marine foncé) sur la couleur de fond choisie par le
    client, jamais à valider un contraste précis au sens WCAG AA/AAA."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def linearize(channel):
        return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4

    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def _sidebar_text_vars(background_hex):
    """Bascule tout le texte de la sidebar (titres de section, liens,
    libellé de rôle...) entre une palette blanche et une palette marine
    foncé selon que la couleur de fond choisie par le client est sombre ou
    claire — sans ça, une couleur claire rendait le texte illisible."""
    is_light = _relative_luminance(background_hex) > 0.5
    base_rgb = "10, 30, 69" if is_light else "255, 255, 255"
    text_solid = "#0A1E45" if is_light else "#FFFFFF"
    return {
        "org_sidebar_text": text_solid,
        "org_sidebar_text_soft": f"rgba({base_rgb}, 0.75)",
        "org_sidebar_text_faint": f"rgba({base_rgb}, 0.45)",
        "org_sidebar_hover_bg": f"rgba({base_rgb}, 0.06)",
        "org_sidebar_border": f"rgba({base_rgb}, 0.08)",
    }


def org_branding(request):
    """Couleurs de marque (superadmin:organization_form, section « Apparence »)
    appliquées à l'interface de l'organisation courante : couleur principale
    pour le fond du menu latéral, couleur secondaire pour les éléments
    d'action (boutons, liens, états actifs) dans toute l'app — aucune couleur
    pour le Super Admin (pas de tenant)."""
    user = getattr(request, "user", None)
    tenant = user.tenant if (user and user.is_authenticated) else None
    if tenant is None:
        return {}
    context = {
        "org_primary_color": tenant.primary_color,
        "org_secondary_color": tenant.secondary_color,
        "org_accent_text": "#0A1E45" if _relative_luminance(tenant.secondary_color) > 0.5 else "#FFFFFF",
    }
    context.update(_sidebar_text_vars(tenant.primary_color))
    return context


def ai_sidebar(request):
    """CDC §15.3.3 : le lien "Assistant IA" n'apparaît dans la sidebar que si
    l'organisation (ou la plateforme, pour le Super Admin) a activé l'IA pour
    le rôle de l'utilisateur courant — évite un lien mort vers une page qui
    redirigerait immédiatement."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}
    from apps.ai.services import is_ai_available

    return {"ai_available": is_ai_available(user)}
