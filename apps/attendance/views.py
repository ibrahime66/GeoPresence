import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
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

from . import services
from .forms import ClockForm
from .models import Attendance
from .services import ClockRejected

APPROVER_ROLES = (User.Role.MANAGER, User.Role.ADMIN)


def _detect_device_type(user_agent):
    ua = (user_agent or "").lower()
    if "tablet" in ua or "ipad" in ua:
        return "Tablet"
    if "mobi" in ua:
        return "Mobile"
    return "Desktop"


class ClockPageView(LoginRequiredMixin, TemplateView):
    template_name = "attendance/clock.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = get_active_employee(self.request.user)
        context["employee"] = employee
        if employee is not None:
            clock_type, clock_date, slot = services.get_clock_status(employee)
            context["next_clock_type"] = clock_type
            context["next_clock_date"] = clock_date
            context["next_clock_slot"] = slot
            context["today_attendances"] = Attendance.objects.all_tenants().filter(
                employee=employee, clock_date=clock_date
            ).order_by("server_time")
            # json.dumps plutôt qu'une interpolation directe de gabarit : les
            # DecimalField latitude/longitude s'afficheraient avec le
            # séparateur décimal localisé (virgule en fr-FR) via {{ }}, ce qui
            # casserait le JSON produit pour clock.js.
            context["agency_zones_json"] = json.dumps(
                [
                    {
                        "label": zone["label"],
                        "latitude": float(zone["latitude"]),
                        "longitude": float(zone["longitude"]),
                        "radius": zone["radius"],
                    }
                    for zone in employee.primary_agency.zones()
                ]
            )
        return context


class ClockView(LoginRequiredMixin, View):
    """CDC §9.3.6 : re-validation complète côté serveur, quoi que le client
    ait déjà vérifié (défense en profondeur)."""

    def post(self, request):
        # Vérif 2 — compte utilisateur actif (Vérif 1 = LoginRequiredMixin,
        # Vérif 3 = organisation active déjà garantie par TenantMiddleware).
        if not request.user.is_active:
            return JsonResponse({"error": "Compte suspendu."}, status=403)

        # Vérif 4 — profil employé actif.
        employee = get_active_employee(request.user)
        if employee is None:
            return JsonResponse({"error": "Aucun profil employé actif associé à ce compte."}, status=403)

        # Vérif 5/6/7 — GPS/caméra : la présence des données dans la requête
        # EST la preuve que le navigateur les a fournies (impossibles à obtenir
        # sinon) ; leur absence est gérée par la validation du formulaire.
        form = ClockForm(request.POST)
        if not form.is_valid():
            return JsonResponse({"error": "Données de pointage invalides.", "details": form.errors}, status=400)

        user_agent = request.META.get("HTTP_USER_AGENT", "")

        try:
            attendance = services.clock(
                employee,
                form.cleaned_data["clock_type"],
                latitude=form.cleaned_data["latitude"],
                longitude=form.cleaned_data["longitude"],
                gps_accuracy=form.cleaned_data.get("gps_accuracy"),
                is_gps_mocked=form.cleaned_data.get("is_gps_mocked", False),
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=user_agent,
                device_type=_detect_device_type(user_agent),
                client_time=form.cleaned_data.get("client_time"),
                mode=form.cleaned_data.get("mode") or Attendance.Mode.ONLINE,
            )
        except ClockRejected as exc:
            audit.log_event(
                request,
                audit.CLOCK_REJECTED,
                AuditLog.Result.FAILURE,
                user=request.user,
                description=f"{form.cleaned_data['clock_type']} — {exc.code}",
                error=exc.message,
            )
            return JsonResponse({"error": exc.message, "code": exc.code}, status=422)

        audit.log_event(
            request,
            audit.CLOCK_SUCCESS,
            AuditLog.Result.SUCCESS,
            user=request.user,
            description=f"{attendance.clock_type} — {attendance.status}",
        )
        return JsonResponse(
            {
                "clock_type": attendance.clock_type,
                "status": attendance.status,
                "status_display": attendance.get_status_display(),
                "server_time": attendance.server_time.isoformat(),
                "late_minutes": attendance.late_minutes,
                "early_leave_minutes": attendance.early_leave_minutes,
                "overtime_minutes": attendance.overtime_minutes,
                "agency": attendance.agency.name,
            }
        )


def _filtered_attendance_queryset(request):
    """Filtres partagés par AttendanceHistoryView et AttendanceExportView —
    l'export doit toujours refléter exactement ce que l'écran affiche. Même
    périmètre que PendingLeavesView/PendingAbsencesView (un Manager ne voit
    que son équipe)."""
    qs = Attendance.objects.all_tenants().filter(
        tenant=request.user.tenant
    ).select_related("employee__user", "agency")
    if request.user.role == User.Role.MANAGER:
        qs = qs.filter(employee__manager=request.user)

    employee_id = request.GET.get("employe", "")
    if employee_id:
        qs = qs.filter(employee_id=employee_id)
    clock_type = request.GET.get("type", "")
    if clock_type:
        qs = qs.filter(clock_type=clock_type)
    date_from = request.GET.get("du", "")
    if date_from:
        qs = qs.filter(clock_date__gte=date_from)
    date_to = request.GET.get("au", "")
    if date_to:
        qs = qs.filter(clock_date__lte=date_to)

    return qs.order_by("-clock_date", "-server_time")


class AttendanceHistoryView(RoleRequiredMixin, TemplateView):
    """CDC §18.3 : historique des pointages consultable par l'Admin/Manager,
    base de toute feuille de présence — jusqu'ici seule ClockPageView
    existait (vue du jour, pour l'employé lui-même), sans aucun écran pour
    consulter/filtrer l'historique complet côté encadrement."""

    allowed_roles = APPROVER_ROLES
    template_name = "attendance/attendance_history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = _filtered_attendance_queryset(self.request)
        context.update(paginate_queryset(self.request, qs))
        context["attendances"] = context["page_obj"].object_list
        context["type_choices"] = Attendance.ClockType.choices

        from apps.employees.models import Employee

        employees_qs = Employee.objects.all_tenants().filter(tenant=self.request.user.tenant).select_related("user")
        if self.request.user.role == User.Role.MANAGER:
            employees_qs = employees_qs.filter(manager=self.request.user)
        context["employee_choices"] = employees_qs.order_by("user__first_name", "user__last_name")
        context["selected_employee"] = self.request.GET.get("employe", "")
        context["selected_type"] = self.request.GET.get("type", "")
        context["selected_du"] = self.request.GET.get("du", "")
        context["selected_au"] = self.request.GET.get("au", "")
        return context


class AttendanceExportView(RoleRequiredMixin, View):
    """Export de l'historique des pointages (CSV/Excel/PDF) — mêmes filtres
    que AttendanceHistoryView, pour servir de feuille de présence exploitable
    en paie sans ressaisie manuelle."""

    allowed_roles = APPROVER_ROLES

    HEADERS = [
        "Employé", "Date", "Type", "Heure", "Statut", "Agence",
        "Retard (min)", "Départ anticipé (min)", "Heures sup. (min)",
    ]

    def get(self, request, fmt):
        attendances = _filtered_attendance_queryset(request)
        rows = [
            [
                str(a.employee),
                a.clock_date.isoformat(),
                a.get_clock_type_display(),
                timezone.localtime(a.server_time).strftime("%H:%M"),
                a.get_status_display(),
                a.agency.name,
                a.late_minutes or "",
                a.early_leave_minutes or "",
                a.overtime_minutes or "",
            ]
            for a in attendances
        ]
        filename_base = f"pointages_{request.tenant.slug}_{timezone.localdate().isoformat()}"

        if fmt == "csv":
            response = exports.export_csv(f"{filename_base}.csv", self.HEADERS, rows)
        elif fmt == "xlsx":
            response = exports.export_xlsx(f"{filename_base}.xlsx", self.HEADERS, rows, sheet_title="Pointages")
        elif fmt == "pdf":
            response = exports.export_pdf(
                f"{filename_base}.pdf", "Historique des pointages", self.HEADERS, rows,
                subtitle=f"{request.tenant.display_name} · {timezone.localdate():%d/%m/%Y}",
            )
        else:
            raise Http404("Format d'export inconnu.")

        audit.log_event(
            request, audit.EXPORT_DATA, AuditLog.Result.SUCCESS, user=request.user,
            description=f"Export pointages ({fmt}, {len(rows)} lignes)",
        )
        return response
