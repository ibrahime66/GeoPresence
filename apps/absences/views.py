from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.audit import services as audit
from apps.audit.models import AuditLog
from apps.core import exports
from apps.core.views import paginate_queryset
from apps.employees.services import get_active_employee

from .forms import JustificationForm
from .models import Absence
from .services import AbsenceCancelled, AbsenceRejected, cancel_justification, review_absence, submit_justification

APPROVER_ROLES = (User.Role.MANAGER, User.Role.ADMIN)


def _filtered_history_queryset(request):
    """Filtres partagés par AbsenceHistoryView et AbsenceHistoryExportView —
    l'export doit toujours refléter exactement ce que l'écran affiche."""
    qs = Absence.objects.all_tenants().filter(
        tenant=request.user.tenant
    ).exclude(status=Absence.Status.PENDING_REVIEW).select_related("employee__user", "reason", "reviewed_by")
    if request.user.role == User.Role.MANAGER:
        qs = qs.filter(employee__manager=request.user)

    status = request.GET.get("statut", "")
    if status:
        qs = qs.filter(status=status)
    employee_id = request.GET.get("employe", "")
    if employee_id:
        qs = qs.filter(employee_id=employee_id)
    date_from = request.GET.get("du", "")
    if date_from:
        qs = qs.filter(date__gte=date_from)
    date_to = request.GET.get("au", "")
    if date_to:
        qs = qs.filter(date__lte=date_to)

    return qs.order_by("-reviewed_at", "-date")


class MyAbsencesView(LoginRequiredMixin, TemplateView):
    template_name = "absences/my_absences.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = get_active_employee(self.request.user)
        context["employee"] = employee
        if employee is not None:
            qs = Absence.objects.all_tenants().filter(employee=employee).select_related("reason")
            context["form"] = JustificationForm(tenant=employee.tenant)
            context.update(paginate_queryset(self.request, qs))
            context["absences"] = context["page_obj"].object_list
        return context


class SubmitJustificationView(LoginRequiredMixin, View):
    def post(self, request):
        employee = get_active_employee(request.user)
        if employee is None:
            messages.error(request, "Aucun profil employé actif associé à ce compte.")
            return redirect("absences:my_absences")

        form = JustificationForm(request.POST, tenant=employee.tenant)
        if not form.is_valid():
            details = "; ".join(f"{err}" for errs in form.errors.values() for err in errs)
            messages.error(request, details or "Formulaire invalide, vérifiez les champs.")
            return redirect("absences:my_absences")

        try:
            submit_justification(
                employee,
                form.cleaned_data["date"],
                reason=form.cleaned_data["reason"],
                comment=form.cleaned_data["comment"],
                custom_reason=form.cleaned_data["custom_reason"],
            )
            messages.success(request, "Justificatif soumis.")
        except (AbsenceRejected, ValidationError) as exc:
            message = exc.message if isinstance(exc, AbsenceRejected) else "; ".join(exc.messages)
            messages.error(request, message)
        return redirect("absences:my_absences")


class CancelJustificationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        employee = get_active_employee(request.user)
        absence = get_object_or_404(Absence.objects.all_tenants(), pk=pk, employee=employee)
        try:
            cancel_justification(absence)
            messages.success(request, "Justificatif annulé.")
        except AbsenceCancelled as exc:
            messages.error(request, exc.message)
        return redirect("absences:my_absences")


class PendingAbsencesView(RoleRequiredMixin, TemplateView):
    allowed_roles = APPROVER_ROLES
    template_name = "absences/pending_absences.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = Absence.objects.all_tenants().filter(
            tenant=self.request.user.tenant, status=Absence.Status.PENDING_REVIEW
        ).select_related("employee__user", "reason")
        if self.request.user.role == User.Role.MANAGER:
            qs = qs.filter(employee__manager=self.request.user)
        context.update(paginate_queryset(self.request, qs))
        context["absences"] = context["page_obj"].object_list
        return context


class AbsenceHistoryView(RoleRequiredMixin, TemplateView):
    """Justificatifs déjà traités — comble le même trou que LeaveHistoryView
    côté congés : PendingAbsencesView filtre sur EN ATTENTE DE VALIDATION,
    donc une fois traité un justificatif disparaissait sans aucune trace côté
    admin/manager."""

    allowed_roles = APPROVER_ROLES
    template_name = "absences/absence_history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = _filtered_history_queryset(self.request)
        status = self.request.GET.get("statut", "")
        employee_id = self.request.GET.get("employe", "")
        date_from = self.request.GET.get("du", "")
        date_to = self.request.GET.get("au", "")
        context.update(paginate_queryset(self.request, qs))
        context["absences"] = context["page_obj"].object_list
        context["status_choices"] = [c for c in Absence.Status.choices if c[0] != Absence.Status.PENDING_REVIEW]

        from apps.employees.models import Employee

        employees_qs = Employee.objects.all_tenants().filter(tenant=self.request.user.tenant).select_related("user")
        if self.request.user.role == User.Role.MANAGER:
            employees_qs = employees_qs.filter(manager=self.request.user)
        context["employee_choices"] = employees_qs.order_by("user__first_name", "user__last_name")
        context["selected_status"] = status
        context["selected_employee"] = employee_id
        context["selected_du"] = date_from
        context["selected_au"] = date_to
        return context


class ReviewAbsenceView(RoleRequiredMixin, View):
    allowed_roles = APPROVER_ROLES

    def post(self, request, pk):
        absence = get_object_or_404(Absence.objects.all_tenants(), pk=pk, tenant=request.user.tenant)
        if request.user.role == User.Role.MANAGER and absence.employee.manager_id != request.user.id:
            messages.error(request, "Cette absence ne fait pas partie de votre équipe.")
            return redirect("absences:pending")

        comment = request.POST.get("comment", "")
        action = request.POST.get("action")
        try:
            if action == "approve":
                review_absence(absence, request.user, approve=True, comment=comment)
                messages.success(request, "Absence justifiée.")
            elif action == "reject":
                review_absence(absence, request.user, approve=False, comment=comment)
                messages.success(request, "Justificatif rejeté.")
            else:
                messages.error(request, "Action inconnue.")
        except AbsenceRejected as exc:
            messages.error(request, exc.message)
        return redirect("absences:pending")


class AbsenceHistoryExportView(RoleRequiredMixin, View):
    """Export de l'historique des justificatifs (CSV/Excel/PDF) — mêmes
    filtres que AbsenceHistoryView."""

    allowed_roles = APPROVER_ROLES

    HEADERS = ["Employé", "Date", "Motif", "Statut", "Commentaire employé", "Décidé par", "Décidé le", "Commentaire valideur"]

    def get(self, request, fmt):
        absences = _filtered_history_queryset(request)
        rows = [
            [
                str(absence.employee),
                absence.date.isoformat(),
                absence.display_reason,
                absence.get_status_display(),
                absence.employee_comment,
                str(absence.reviewed_by) if absence.reviewed_by else "",
                timezone.localtime(absence.reviewed_at).strftime("%d/%m/%Y %H:%M") if absence.reviewed_at else "",
                absence.reviewer_comment,
            ]
            for absence in absences
        ]
        filename_base = f"absences_{request.tenant.slug}_{timezone.localdate().isoformat()}"

        if fmt == "csv":
            response = exports.export_csv(f"{filename_base}.csv", self.HEADERS, rows)
        elif fmt == "xlsx":
            response = exports.export_xlsx(f"{filename_base}.xlsx", self.HEADERS, rows, sheet_title="Absences")
        elif fmt == "pdf":
            response = exports.export_pdf(
                f"{filename_base}.pdf", "Historique des absences", self.HEADERS, rows,
                subtitle=f"{request.tenant.display_name} · {timezone.localdate():%d/%m/%Y}",
            )
        else:
            raise Http404("Format d'export inconnu.")

        audit.log_event(
            request, audit.EXPORT_DATA, AuditLog.Result.SUCCESS, user=request.user,
            description=f"Export absences ({fmt}, {len(rows)} lignes)",
        )
        return response
