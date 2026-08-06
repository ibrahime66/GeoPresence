import secrets

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, UpdateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.accounts.password_policy import record_password
from apps.audit import services as audit
from apps.audit.models import AuditLog
from apps.core import exports
from apps.core.views import DEFAULT_PAGE_SIZE, TenantFormMixin, TenantQuerysetMixin

from . import import_utils
from .forms import EmployeeCreateForm, EmployeeImportForm, EmployeeUpdateForm
from .models import Employee
from .services import sync_user_active_state

ADMIN_ONLY = (User.Role.ADMIN,)
IMPORT_SESSION_KEY = "employee_import_pending"


class EmployeeListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ADMIN_ONLY
    model = Employee
    template_name = "employees/employee_list.html"
    context_object_name = "employees"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return super().get_queryset().select_related("user", "department", "position", "primary_agency")


class EmployeeCreateView(RoleRequiredMixin, View):
    """CDC §11.3.2 : crée le User (mot de passe temporaire, changement forcé à
    la première connexion — déjà géré par le module accounts) ET le profil
    Employee, puis envoie l'e-mail de bienvenue."""

    allowed_roles = ADMIN_ONLY
    template_name = "employees/employee_create_form.html"

    def get(self, request):
        return render(request, self.template_name, {"form": EmployeeCreateForm(tenant=request.tenant)})

    def post(self, request):
        form = EmployeeCreateForm(request.POST, tenant=request.tenant)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        temp_password = secrets.token_urlsafe(10)
        user = User.objects.create_user(
            email=form.cleaned_data["email"],
            password=temp_password,
            tenant=request.tenant,
            role=form.cleaned_data["role"],
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            must_change_password=True,
        )
        record_password(user)

        employee = Employee(
            tenant=request.tenant,
            user=user,
            # .get() plutôt que [...] : ces deux champs sont retirés du
            # formulaire (apply_module_gating) quand le module Départements/
            # Postes est désactivé pour l'organisation — absents de
            # cleaned_data dans ce cas, pas juste vides.
            department=form.cleaned_data.get("department"),
            position=form.cleaned_data.get("position"),
            primary_agency=form.cleaned_data["primary_agency"],
            manager=form.cleaned_data["manager"],
            contract_type=form.cleaned_data["contract_type"],
            hire_date=form.cleaned_data["hire_date"],
            annual_leave_days=form.cleaned_data["annual_leave_days"],
        )
        try:
            employee.full_clean()
        except ValidationError as exc:
            user.delete()
            for errors in exc.message_dict.values():
                for error in errors:
                    form.add_error(None, error)
            return render(request, self.template_name, {"form": form})

        employee.save()

        send_mail(
            subject="Bienvenue sur GeoPresence",
            message=(
                f"Bonjour {user.first_name},\n\n"
                f"Votre compte a été créé sur GeoPresence.\n"
                f"E-mail : {user.email}\n"
                f"Mot de passe temporaire : {temp_password}\n\n"
                "Connectez-vous et changez votre mot de passe dès la première connexion."
            ),
            from_email=None,
            recipient_list=[user.email],
        )
        messages.success(request, f"Employé créé. Accès envoyés par e-mail à {user.email}.")
        return redirect("employees:list")


class EmployeeUpdateView(RoleRequiredMixin, TenantFormMixin, UpdateView):
    allowed_roles = ADMIN_ONLY
    model = Employee
    form_class = EmployeeUpdateForm
    template_name = "employees/employee_form.html"
    success_url = reverse_lazy("employees:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        sync_user_active_state(self.object)
        return response


class EmployeeExportView(RoleRequiredMixin, TenantQuerysetMixin, View):
    """CDC §3.2.4/§18.3 : export de la liste des employés en CSV/Excel/PDF."""

    allowed_roles = ADMIN_ONLY
    model = Employee

    HEADERS = [
        "Matricule", "Nom", "Prénom", "E-mail", "Rôle", "Département", "Poste",
        "Agence", "Type de contrat", "Date d'entrée", "Statut",
    ]

    def get(self, request, fmt):
        employees = (
            self.get_queryset()
            .select_related("user", "department", "position", "primary_agency")
            .order_by("matricule")
        )
        rows = [
            [
                e.matricule,
                e.user.last_name,
                e.user.first_name,
                e.user.email,
                e.user.get_role_display(),
                e.department.name if e.department else "",
                e.position.title if e.position else "",
                e.primary_agency.name,
                e.get_contract_type_display(),
                e.hire_date.isoformat(),
                e.get_status_display(),
            ]
            for e in employees
        ]
        filename_base = f"employes_{request.tenant.slug}_{timezone.localdate().isoformat()}"

        if fmt == "csv":
            response = exports.export_csv(f"{filename_base}.csv", self.HEADERS, rows)
        elif fmt == "xlsx":
            response = exports.export_xlsx(f"{filename_base}.xlsx", self.HEADERS, rows, sheet_title="Employés")
        elif fmt == "pdf":
            response = exports.export_pdf(
                f"{filename_base}.pdf", "Liste des employés", self.HEADERS, rows,
                subtitle=f"{request.tenant.display_name} — {timezone.localdate():%d/%m/%Y}",
            )
        else:
            raise Http404("Format d'export inconnu.")

        audit.log_event(
            request, audit.EXPORT_DATA, AuditLog.Result.SUCCESS, user=request.user,
            description=f"Export employés ({fmt}, {len(rows)} lignes)",
        )
        return response


class EmployeeStatusChangeView(RoleRequiredMixin, TenantQuerysetMixin, View):
    """CDC §3.2.3/§11.4 : actions rapides Suspendre/Réactiver/Archiver depuis
    la liste, sans passer par le formulaire d'édition complet."""

    allowed_roles = ADMIN_ONLY
    model = Employee
    success_url = reverse_lazy("employees:list")

    TARGET_STATUS = {
        "suspend": Employee.Status.SUSPENDED,
        "activate": Employee.Status.ACTIVE,
        "archive": Employee.Status.ARCHIVED,
    }

    def post(self, request, pk, action):
        target = self.TARGET_STATUS.get(action)
        if target is None:
            raise Http404("Action inconnue.")
        employee = get_object_or_404(self.get_queryset().select_related("user"), pk=pk)
        employee.status = target
        employee.save(update_fields=["status"])
        sync_user_active_state(employee)
        messages.success(request, f"Statut de {employee.user.full_name or employee.user.email} mis à jour.")
        return redirect(self.success_url)


class EmployeeRevokeSessionsView(RoleRequiredMixin, TenantQuerysetMixin, View):
    """CDC §5.6.2 : « L'Administrateur peut révoquer toutes les sessions d'un
    utilisateur » — indépendamment de toute suspension (ex. appareil suspecté
    compromis, sans vouloir bloquer l'accès futur de l'employé)."""

    allowed_roles = ADMIN_ONLY
    model = Employee
    success_url = reverse_lazy("employees:list")

    def post(self, request, pk):
        from apps.accounts.sessions import revoke_all_sessions

        employee = get_object_or_404(self.get_queryset().select_related("user"), pk=pk)
        revoke_all_sessions(employee.user)
        messages.success(request, f"Toutes les sessions de {employee.user.full_name or employee.user.email} ont été révoquées.")
        return redirect(self.success_url)


class EmployeeImportTemplateView(RoleRequiredMixin, View):
    """CDC §11.5 point 65 : modèle de fichier téléchargeable, colonnes et
    format attendus (une ligne d'exemple)."""

    allowed_roles = ADMIN_ONLY

    def get(self, request):
        return exports.export_csv(
            "modele_import_employes.csv", import_utils.COLUMNS, [import_utils.TEMPLATE_EXAMPLE_ROW]
        )


class EmployeeImportView(RoleRequiredMixin, View):
    """CDC §11.5 : étapes 65-67 — upload, validation ligne par ligne avec
    rapport d'erreurs, aperçu avant import définitif. La confirmation
    (étape 68) est gérée par `EmployeeImportConfirmView`."""

    allowed_roles = ADMIN_ONLY
    template_name = "employees/employee_import.html"

    def get(self, request):
        return render(request, self.template_name, {"form": EmployeeImportForm(), "columns": import_utils.COLUMNS})

    def post(self, request):
        form = EmployeeImportForm(request.POST, request.FILES)
        context = {"form": form, "columns": import_utils.COLUMNS}
        if not form.is_valid():
            return render(request, self.template_name, context)

        try:
            raw_rows = import_utils.parse_upload(form.cleaned_data["file"])
        except import_utils.ImportFileError as exc:
            form.add_error("file", str(exc))
            return render(request, self.template_name, context)

        if not raw_rows:
            form.add_error("file", "Le fichier ne contient aucune ligne de données.")
            return render(request, self.template_name, context)

        valid_rows, invalid_rows = import_utils.validate_rows(raw_rows, request.tenant)
        request.session[IMPORT_SESSION_KEY] = {"tenant_id": str(request.tenant.id), "rows": valid_rows}

        return render(
            request,
            "employees/employee_import_preview.html",
            {
                "valid_rows": valid_rows,
                "invalid_rows": invalid_rows,
                "total": len(raw_rows),
            },
        )


class EmployeeImportConfirmView(RoleRequiredMixin, View):
    allowed_roles = ADMIN_ONLY

    def post(self, request):
        pending = request.session.get(IMPORT_SESSION_KEY)
        if not pending or pending.get("tenant_id") != str(request.tenant.id):
            messages.error(request, "Aucun import en attente de confirmation.")
            return redirect("employees:import")

        created, failed = import_utils.commit_import(request.tenant, pending["rows"])
        del request.session[IMPORT_SESSION_KEY]

        audit.log_event(
            request, audit.IMPORT_DATA, AuditLog.Result.SUCCESS, user=request.user,
            description=f"Import employés : {len(created)} créés, {len(failed)} échecs",
        )

        if created:
            messages.success(request, f"{len(created)} employé(s) importé(s) avec succès.")
        if failed:
            details = "; ".join(f"ligne {f['row']} ({f['email']}) : {f['error']}" for f in failed)
            messages.error(request, f"{len(failed)} ligne(s) n'ont pas pu être importées — {details}")
        if not created and not failed:
            messages.warning(request, "Aucune ligne à importer.")
        return redirect("employees:list")
