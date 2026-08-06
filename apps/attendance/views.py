import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from apps.audit import services as audit
from apps.audit.models import AuditLog
from apps.employees.services import get_active_employee

from . import services
from .forms import ClockForm
from .models import Attendance
from .services import ClockRejected


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
