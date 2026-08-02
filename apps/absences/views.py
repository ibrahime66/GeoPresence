from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.employees.services import get_active_employee

from .forms import JustificationForm
from .models import Absence
from .services import AbsenceRejected, review_absence, submit_justification

APPROVER_ROLES = (User.Role.MANAGER, User.Role.SUPERVISOR, User.Role.ADMIN)


class MyAbsencesView(LoginRequiredMixin, TemplateView):
    template_name = "absences/my_absences.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = get_active_employee(self.request.user)
        context["employee"] = employee
        if employee is not None:
            context["absences"] = Absence.objects.all_tenants().filter(employee=employee).select_related("reason")
            context["form"] = JustificationForm(tenant=employee.tenant)
        return context


class SubmitJustificationView(LoginRequiredMixin, View):
    def post(self, request):
        employee = get_active_employee(request.user)
        if employee is None:
            messages.error(request, "Aucun profil employé actif associé à ce compte.")
            return redirect("absences:my_absences")

        form = JustificationForm(request.POST, request.FILES, tenant=employee.tenant)
        if not form.is_valid():
            messages.error(request, "Formulaire invalide — vérifiez les champs.")
            return redirect("absences:my_absences")

        try:
            submit_justification(
                employee,
                form.cleaned_data["date"],
                reason=form.cleaned_data["reason"],
                comment=form.cleaned_data["comment"],
                file=form.cleaned_data["file"] or None,
            )
            messages.success(request, "Justificatif soumis.")
        except (AbsenceRejected, ValidationError) as exc:
            message = exc.message if isinstance(exc, AbsenceRejected) else "; ".join(exc.messages)
            messages.error(request, message)
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
        context["absences"] = qs
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
