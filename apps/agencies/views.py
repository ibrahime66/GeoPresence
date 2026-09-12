from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.core.views import DEFAULT_PAGE_SIZE, TenantFormMixin, TenantQuerysetMixin, ToggleActiveView

from . import services
from .forms import AgencyForm
from .models import Agency

ADMIN_ONLY = (User.Role.ADMIN,)


class AgencyListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ADMIN_ONLY
    model = Agency
    template_name = "agencies/agency_list.html"
    context_object_name = "agencies"
    paginate_by = DEFAULT_PAGE_SIZE


class AgencyCreateView(RoleRequiredMixin, TenantFormMixin, CreateView):
    allowed_roles = ADMIN_ONLY
    model = Agency
    form_class = AgencyForm
    template_name = "agencies/agency_form.html"
    success_url = reverse_lazy("agencies:list")


class AgencyUpdateView(RoleRequiredMixin, TenantFormMixin, UpdateView):
    allowed_roles = ADMIN_ONLY
    model = Agency
    form_class = AgencyForm
    template_name = "agencies/agency_form.html"
    success_url = reverse_lazy("agencies:list")


class AgencyToggleActiveView(ToggleActiveView):
    """CDC §7.3 : activer/désactiver une agence — une agence désactivée
    n'accepte plus aucun pointage."""

    allowed_roles = ADMIN_ONLY
    model = Agency
    success_url = reverse_lazy("agencies:list")


class AgencyQRView(RoleRequiredMixin, TenantQuerysetMixin, DetailView):
    """RM-QR-001 : encart imprimable à afficher sur site. Le QR ne fait que
    présélectionner l'agence sur l'écran de pointage — la vérification GPS
    habituelle s'applique ensuite normalement (cf. attendance.views.QREntryView)."""

    allowed_roles = ADMIN_ONLY
    model = Agency
    template_name = "agencies/agency_qr.html"
    context_object_name = "agency"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scan_url = services.qr_scan_url(self.request, self.object)
        context["qr_scan_url"] = scan_url
        context["qr_image_data_uri"] = services.qr_code_data_uri(scan_url)
        return context


class AgencyQRRegenerateView(RoleRequiredMixin, TenantQuerysetMixin, View):
    """Invalide immédiatement toute affiche imprimée existante pour cette
    agence (perte, vol, doute de compromission) — un nouveau QR doit être
    réimprimé et recollé après cette action."""

    allowed_roles = ADMIN_ONLY
    model = Agency

    def post(self, request, *args, **kwargs):
        agency = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        agency.regenerate_qr_token()
        messages.success(
            request,
            f"Nouveau code QR généré pour {agency.name}. L'ancienne affiche imprimée ne fonctionne plus.",
        )
        return redirect("agencies:qr", pk=agency.pk)
