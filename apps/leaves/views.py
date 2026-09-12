import calendar as calendar_module
from collections import defaultdict
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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

from .forms import LeaveRequestForm
from .models import Leave
from .services import LeaveRejected, approve_leave, cancel_leave, reject_leave, submit_leave

APPROVER_ROLES = (User.Role.MANAGER, User.Role.ADMIN)


def _filtered_history_queryset(request):
    """Filtres partagés par LeaveHistoryView et LeaveHistoryExportView —
    l'export doit toujours refléter exactement ce que l'écran affiche."""
    qs = Leave.objects.all_tenants().filter(
        tenant=request.user.tenant
    ).exclude(status=Leave.Status.PENDING).select_related("employee__user", "leave_type", "reviewed_by")
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
        qs = qs.filter(start_date__gte=date_from)
    date_to = request.GET.get("au", "")
    if date_to:
        qs = qs.filter(end_date__lte=date_to)

    return qs.order_by("-reviewed_at", "-start_date")


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
            messages.error(request, "Formulaire invalide, vérifiez les champs.")
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


class LeaveCalendarView(RoleRequiredMixin, TemplateView):
    """Vue mois des congés approuvés — un tableau liste les demandes mais ne
    montre pas visuellement qui est absent quand ; cette grille répond
    directement à "qui est en congé cette semaine-là", ce qu'un tableau
    oblige à reconstituer mentalement demande par demande. Mêmes règles de
    périmètre que PendingLeavesView/LeaveHistoryView (un Manager ne voit que
    son équipe). Ne montre que les congés APPROUVÉS : une demande en attente
    n'est pas encore une absence certaine, l'afficher ici induirait en
    erreur sur qui est réellement absent."""

    allowed_roles = APPROVER_ROLES
    template_name = "leaves/leave_calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        today = timezone.localdate()

        try:
            first_day = datetime.strptime(request.GET.get("mois", ""), "%Y-%m").date().replace(day=1)
        except ValueError:
            first_day = today.replace(day=1)
        last_day = first_day.replace(day=calendar_module.monthrange(first_day.year, first_day.month)[1])

        # Grille complète en semaines (lundi -> dimanche), donc incluant
        # quelques jours du mois précédent/suivant pour ne pas couper une
        # semaine en deux visuellement.
        month_dates = list(calendar_module.Calendar(firstweekday=0).itermonthdates(first_day.year, first_day.month))
        grid_start, grid_end = month_dates[0], month_dates[-1]

        leaves_qs = Leave.objects.all_tenants().filter(
            tenant=request.user.tenant, status=Leave.Status.APPROVED,
            start_date__lte=grid_end, end_date__gte=grid_start,
        ).select_related("employee__user", "leave_type").order_by("employee__user__first_name")
        if request.user.role == User.Role.MANAGER:
            leaves_qs = leaves_qs.filter(employee__manager=request.user)

        leaves_by_day = defaultdict(list)
        for leave in leaves_qs:
            day = max(leave.start_date, grid_start)
            end = min(leave.end_date, grid_end)
            while day <= end:
                leaves_by_day[day].append(leave)
                day += timedelta(days=1)

        weeks, week = [], []
        for day in month_dates:
            week.append({
                "date": day,
                "in_month": day.month == first_day.month,
                "is_today": day == today,
                "is_weekend": day.weekday() >= 5,
                "leaves": leaves_by_day.get(day, []),
            })
            if len(week) == 7:
                weeks.append(week)
                week = []

        context.update({
            "weeks": weeks,
            "current_month": first_day,
            "prev_month": (first_day - timedelta(days=1)).replace(day=1),
            "next_month": last_day + timedelta(days=1),
            "current_month_param": first_day.strftime("%Y-%m"),
            "is_current_month": first_day == today.replace(day=1),
            "leaves_this_month_count": leaves_qs.filter(start_date__lte=last_day, end_date__gte=first_day).count(),
        })
        return context


class LeaveHistoryView(RoleRequiredMixin, TemplateView):
    """Demandes déjà traitées (approuvées/rejetées/annulées) — pendant
    longtemps la seule vue admin/manager était PendingLeavesView, filtrée sur
    le statut EN ATTENTE : une fois une demande traitée, elle disparaissait
    purement et simplement du champ de vision de l'admin, sans aucun moyen de
    la retrouver ensuite (hors accès direct à la base). Cette vue comble ce
    trou — mêmes règles de périmètre que PendingLeavesView (un Manager ne voit
    que son équipe)."""

    allowed_roles = APPROVER_ROLES
    template_name = "leaves/leave_history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = _filtered_history_queryset(self.request)
        status = self.request.GET.get("statut", "")
        employee_id = self.request.GET.get("employe", "")
        date_from = self.request.GET.get("du", "")
        date_to = self.request.GET.get("au", "")
        context.update(paginate_queryset(self.request, qs))
        context["leaves"] = context["page_obj"].object_list
        context["status_choices"] = [c for c in Leave.Status.choices if c[0] != Leave.Status.PENDING]

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


class LeaveHistoryExportView(RoleRequiredMixin, View):
    """Export de l'historique des congés (CSV/Excel/PDF) — mêmes filtres que
    LeaveHistoryView."""

    allowed_roles = APPROVER_ROLES

    HEADERS = ["Employé", "Type", "Du", "Au", "Jours", "Statut", "Décidé par", "Décidé le", "Commentaire"]

    def get(self, request, fmt):
        leaves = _filtered_history_queryset(request)
        rows = [
            [
                str(leave.employee),
                leave.leave_type.name,
                leave.start_date.isoformat(),
                leave.end_date.isoformat(),
                leave.working_days,
                leave.get_status_display(),
                str(leave.reviewed_by) if leave.reviewed_by else "",
                timezone.localtime(leave.reviewed_at).strftime("%d/%m/%Y %H:%M") if leave.reviewed_at else "",
                leave.reviewer_comment,
            ]
            for leave in leaves
        ]
        filename_base = f"conges_{request.tenant.slug}_{timezone.localdate().isoformat()}"

        if fmt == "csv":
            response = exports.export_csv(f"{filename_base}.csv", self.HEADERS, rows)
        elif fmt == "xlsx":
            response = exports.export_xlsx(f"{filename_base}.xlsx", self.HEADERS, rows, sheet_title="Congés")
        elif fmt == "pdf":
            response = exports.export_pdf(
                f"{filename_base}.pdf", "Historique des congés", self.HEADERS, rows,
                subtitle=f"{request.tenant.display_name} · {timezone.localdate():%d/%m/%Y}",
            )
        else:
            raise Http404("Format d'export inconnu.")

        audit.log_event(
            request, audit.EXPORT_DATA, AuditLog.Result.SUCCESS, user=request.user,
            description=f"Export congés ({fmt}, {len(rows)} lignes)",
        )
        return response
