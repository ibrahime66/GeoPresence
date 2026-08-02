from django.contrib import admin

from .models import Holiday, Leave, LeaveType


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "is_recurring")

    def get_queryset(self, request):
        return Holiday.objects.all_tenants()


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "deducts_from_balance", "requires_justification", "is_active")
    search_fields = ("name",)

    def get_queryset(self, request):
        return LeaveType.objects.all_tenants()


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "start_date", "end_date", "working_days", "status")
    list_filter = ("status", "leave_type")
    search_fields = ("employee__matricule", "employee__user__email")
    autocomplete_fields = ("employee", "leave_type", "reviewed_by")
    readonly_fields = ("working_days",)

    def get_queryset(self, request):
        return Leave.objects.all_tenants()
