import secrets

from django.contrib import messages
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone as dj_timezone
from django.views import View
from django.views.generic import ListView, TemplateView, UpdateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.accounts.password_policy import record_password
from apps.attendance.models import Attendance
from apps.audit import services as audit
from apps.audit.models import AuditLog
from apps.core import exports
from apps.employees.models import Employee
from apps.tenants.models import Organization
from apps.tenants.org_settings import initial_settings_for_type

from .forms import OrganizationCreateForm, OrganizationUpdateForm

SUPER_ADMIN_ONLY = (User.Role.SUPER_ADMIN,)


class SuperAdminDashboardView(RoleRequiredMixin, TemplateView):
    """CDC §3.1.1 : statistiques globales — jamais de détail opérationnel d'un
    tenant (§3.1.2), uniquement des agrégats."""

    allowed_roles = SUPER_ADMIN_ONLY
    template_name = "superadmin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["org_counts"] = {
            "total": Organization.objects.count(),
            "active": Organization.objects.filter(status=Organization.Status.ACTIVE).count(),
            "suspended": Organization.objects.filter(status=Organization.Status.SUSPENDED).count(),
        }
        context["users_total"] = User.objects.exclude(role=User.Role.SUPER_ADMIN).count()
        context["employees_total"] = Employee.objects.all_tenants().count()
        context["attendances_today"] = Attendance.objects.all_tenants().filter(
            clock_date=dj_timezone.localdate()
        ).count()
        context["recent_organizations"] = Organization.objects.order_by("-created_at")[:5]
        context["recent_audit_logs"] = AuditLog.objects.select_related("tenant")[:10]
        return context


class OrganizationListView(RoleRequiredMixin, ListView):
    allowed_roles = SUPER_ADMIN_ONLY
    model = Organization
    template_name = "superadmin/organization_list.html"
    context_object_name = "organizations"
    paginate_by = 25

    def get_queryset(self):
        return Organization.objects.order_by("-created_at")


class OrganizationCreateView(RoleRequiredMixin, View):
    """CDC §6.2.3 : crée l'espace tenant + le compte Administrateur principal,
    envoie l'e-mail de bienvenue, journalise dans l'audit global."""

    allowed_roles = SUPER_ADMIN_ONLY
    template_name = "superadmin/organization_form.html"

    def get(self, request):
        return render(request, self.template_name, {"form": OrganizationCreateForm()})

    def post(self, request):
        form = OrganizationCreateForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        org = form.save()
        initial_settings = initial_settings_for_type(org.org_type)
        if initial_settings:
            org.settings = {**(org.settings or {}), **initial_settings}
            org.save(update_fields=["settings"])

        temp_password = secrets.token_urlsafe(10)
        admin_user = User.objects.create_user(
            email=form.cleaned_data["admin_email"],
            password=temp_password,
            tenant=org,
            role=User.Role.ADMIN,
            first_name=form.cleaned_data["admin_first_name"],
            last_name=form.cleaned_data["admin_last_name"],
            must_change_password=True,
        )
        record_password(admin_user)

        send_mail(
            subject="Bienvenue sur GeoPresence",
            message=(
                f"Bonjour {admin_user.first_name},\n\n"
                f"Votre organisation « {org.display_name} » a été créée sur GeoPresence.\n"
                f"E-mail : {admin_user.email}\n"
                f"Mot de passe temporaire : {temp_password}\n\n"
                "Connectez-vous et changez votre mot de passe dès la première connexion."
            ),
            from_email=None,
            recipient_list=[admin_user.email],
        )

        audit.log_event(
            request, audit.CREATE_ORGANIZATION, AuditLog.Result.SUCCESS, user=request.user, tenant=org,
            description=f"Organisation « {org.display_name} » créée.",
        )
        messages.success(request, f"Organisation créée. Accès administrateur envoyés à {admin_user.email}.")
        return redirect("superadmin:organization_list")


class OrganizationUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = SUPER_ADMIN_ONLY
    model = Organization
    form_class = OrganizationUpdateForm
    template_name = "superadmin/organization_form.html"
    success_url = reverse_lazy("superadmin:organization_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        audit.log_event(
            self.request, audit.UPDATE_ORGANIZATION, AuditLog.Result.SUCCESS, user=self.request.user,
            tenant=self.object, description=f"Organisation « {self.object.display_name} » modifiée.",
        )
        return response


class OrganizationSuspendView(RoleRequiredMixin, View):
    """RM-ORG-003 : la suspension est immédiate — TenantMiddleware déconnecte
    tous les utilisateurs du tenant dès leur prochaine requête."""

    allowed_roles = SUPER_ADMIN_ONLY

    def post(self, request, pk):
        org = get_object_or_404(Organization, pk=pk)
        org.status = Organization.Status.SUSPENDED
        org.save(update_fields=["status"])
        audit.log_event(
            request, audit.SUSPEND_ORGANIZATION, AuditLog.Result.SUCCESS, user=request.user, tenant=org,
            description=f"Organisation « {org.display_name} » suspendue.",
        )
        messages.success(request, f"Organisation « {org.display_name} » suspendue.")
        return redirect("superadmin:organization_list")


class OrganizationReactivateView(RoleRequiredMixin, View):
    allowed_roles = SUPER_ADMIN_ONLY

    def post(self, request, pk):
        org = get_object_or_404(Organization, pk=pk)
        org.status = Organization.Status.ACTIVE
        org.save(update_fields=["status"])
        audit.log_event(
            request, audit.REACTIVATE_ORGANIZATION, AuditLog.Result.SUCCESS, user=request.user, tenant=org,
            description=f"Organisation « {org.display_name} » réactivée.",
        )
        messages.success(request, f"Organisation « {org.display_name} » réactivée.")
        return redirect("superadmin:organization_list")


class OrganizationDeleteView(RoleRequiredMixin, View):
    """CDC §3.1.1/§6.3 : suppression définitive d'une organisation. Implémentée
    comme un changement de statut (DELETED) plutôt qu'un DELETE SQL réel — les
    données restent en base (traçabilité, obligations légales de conservation
    CDC §24.3) mais l'organisation est totalement et définitivement inaccessible
    (TenantMiddleware bloque tout accès, comme pour une suspension)."""

    allowed_roles = SUPER_ADMIN_ONLY

    def post(self, request, pk):
        org = get_object_or_404(Organization, pk=pk)
        org.status = Organization.Status.DELETED
        org.save(update_fields=["status"])
        audit.log_event(
            request, audit.DELETE_ORGANIZATION, AuditLog.Result.SUCCESS, user=request.user, tenant=org,
            description=f"Organisation « {org.display_name} » supprimée.",
        )
        messages.success(request, f"Organisation « {org.display_name} » supprimée.")
        return redirect("superadmin:organization_list")


class AuditLogListView(RoleRequiredMixin, ListView):
    """CDC §3.1.1 : journal d'audit global, toutes organisations confondues."""

    allowed_roles = SUPER_ADMIN_ONLY
    model = AuditLog
    template_name = "superadmin/audit_log_list.html"
    context_object_name = "logs"
    paginate_by = 50

    def get_queryset(self):
        qs = AuditLog.objects.select_related("tenant", "user")
        tenant_id = self.request.GET.get("tenant")
        if tenant_id:
            qs = qs.filter(tenant_id=tenant_id)
        action = self.request.GET.get("action")
        if action:
            qs = qs.filter(action=action)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organizations"] = Organization.objects.order_by("display_name")
        context["actions"] = AuditLog.objects.order_by().values_list("action", flat=True).distinct()
        context["selected_tenant"] = self.request.GET.get("tenant", "")
        context["selected_action"] = self.request.GET.get("action", "")
        return context


class AuditLogExportView(RoleRequiredMixin, View):
    """CDC §18.3 : export du journal d'audit — mêmes filtres (organisation,
    action) que la liste, sans pagination (export complet du résultat filtré)."""

    allowed_roles = SUPER_ADMIN_ONLY
    HEADERS = ["Horodatage", "Action", "Résultat", "Organisation", "Utilisateur", "Rôle", "Description", "IP"]

    def get(self, request, fmt):
        qs = AuditLog.objects.select_related("tenant", "user")
        tenant_id = request.GET.get("tenant")
        if tenant_id:
            qs = qs.filter(tenant_id=tenant_id)
        action = request.GET.get("action")
        if action:
            qs = qs.filter(action=action)

        rows = [
            [
                log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                log.action,
                log.get_result_display(),
                log.tenant.display_name if log.tenant else "",
                log.user_email,
                log.user_role,
                log.description,
                log.ip_address or "",
            ]
            for log in qs[:10000]  # garde-fou : export complet mais borné
        ]
        filename_base = f"audit_{dj_timezone.localdate().isoformat()}"

        if fmt == "csv":
            response = exports.export_csv(f"{filename_base}.csv", self.HEADERS, rows)
        elif fmt == "xlsx":
            response = exports.export_xlsx(f"{filename_base}.xlsx", self.HEADERS, rows, sheet_title="Audit")
        else:
            raise Http404("Format d'export inconnu.")

        audit.log_event(
            request, audit.EXPORT_DATA, AuditLog.Result.SUCCESS, user=request.user,
            description=f"Export journal d'audit ({fmt}, {len(rows)} lignes)",
        )
        return response
