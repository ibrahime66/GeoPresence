from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "clock_type", "clock_date", "server_time", "status", "mode", "is_validated")
    list_filter = ("clock_type", "status", "mode", "is_validated", "agency")
    search_fields = ("employee__matricule", "employee__user__email")
    date_hierarchy = "clock_date"
    readonly_fields = [f.name for f in Attendance._meta.fields if f.name not in ("is_validated", "validated_by", "notes")]

    def get_queryset(self, request):
        return Attendance.objects.all_tenants()
