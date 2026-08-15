from django.conf import settings

from apps.absences.models import Absence
from apps.accounts.models import User
from apps.leaves.models import Leave

APPROVER_ROLES = (User.Role.MANAGER, User.Role.ADMIN)


def analytics(request):
    """Identifiant Google Analytics (GA4), lu depuis l'environnement — vide
    par défaut, donc aucun script ni cookie tant que GA_MEASUREMENT_ID n'est
    pas configuré. N'est effectivement rendu que par core/_landing_base.html
    (pages vitrine publiques), jamais dans l'application authentifiée."""
    return {"ga_measurement_id": getattr(settings, "GA_MEASUREMENT_ID", "")}


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
