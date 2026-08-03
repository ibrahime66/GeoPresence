from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.core.views import paginate_queryset
from apps.employees.services import get_active_employee

from .forms import LeaveRequestForm
from .models import Leave
from .services import LeaveRejected, approve_leave, cancel_leave, reject_leave, submit_leave

APPROVER_ROLES = (User.Role.MANAGER, User.Role.ADMIN)


class MyLeavesView(LoginRequiredMixin, TemplateView):
    template_name = "leaves/my_leaves.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = get_active_employee(self.request.user)
        context["employee"] = employee
        if employee is not None:
            qs = Leave.objects.all_tenants().filter(employee=employee).select_related("leave_type").order_by("-start_date")
            context["form"] = LeaveRequestForm(tenant=employee.tenant)
            context.update(paginate_queryset(self.request, qs))
            context["leaves"] = context["page_obj"].object_list
        return context


class SubmitLeaveView(LoginRequiredMixin, View):
    def post(self, request):
        employee = get_active_employee(request.user)
        if employee is None:
            messages.error(request, "Aucun profil employé actif associé à ce compte.")
            return redirect("leaves:my_leaves")

        form = LeaveRequestForm(request.POST, tenant=employee.tenant)
        if not form.is_valid():
            messages.error(request, "Formulaire invalide — vérifiez les champs.")
            return redirect("leaves:my_leaves")

        try:
            submit_leave(
                employee,
                form.cleaned_data["leave_type"],
                form.cleaned_data["start_date"],
                form.cleaned_data["end_date"],
                comment=form.cleaned_data["comment"],
            )
            messages.success(request, "Demande de congé soumise.")
        except LeaveRejected as exc:
            messages.error(request, exc.message)
        return redirect("leaves:my_leaves")


class CancelLeaveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        employee = get_active_employee(request.user)
        leave = get_object_or_404(Leave.objects.all_tenants(), pk=pk, employee=employee)
        try:
            cancel_leave(leave)
            messages.success(request, "Demande de congé annulée.")
        except LeaveRejected as exc:
            messages.error(request, exc.message)
        return redirect("leaves:my_leaves")


class PendingLeavesView(RoleRequiredMixin, TemplateView):
    allowed_roles = APPROVER_ROLES
    template_name = "leaves/pending_leaves.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = Leave.objects.all_tenants().filter(
            tenant=self.request.user.tenant, status=Leave.Status.PENDING
        ).select_related("employee__user", "leave_type")
        if self.request.user.role == User.Role.MANAGER:
            qs = qs.filter(employee__manager=self.request.user)
        context.update(paginate_queryset(self.request, qs))
        context["leaves"] = context["page_obj"].object_list
        return context


class ReviewLeaveView(RoleRequiredMixin, View):
    allowed_roles = APPROVER_ROLES

    def post(self, request, pk):
        leave = get_object_or_404(Leave.objects.all_tenants(), pk=pk, tenant=request.user.tenant)
        if request.user.role == User.Role.MANAGER and leave.employee.manager_id != request.user.id:
            messages.error(request, "Cette demande ne fait pas partie de votre équipe.")
            return redirect("leaves:pending")

        comment = request.POST.get("comment", "")
        action = request.POST.get("action")
        try:
            if action == "approve":
                approve_leave(leave, request.user, comment)
                messages.success(request, "Demande approuvée.")
            elif action == "reject":
                reject_leave(leave, request.user, comment)
                messages.success(request, "Demande rejetée.")
            else:
                messages.error(request, "Action inconnue.")
        except LeaveRejected as exc:
            messages.error(request, exc.message)
        return redirect("leaves:pending")
