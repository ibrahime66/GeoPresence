from django.contrib import admin

from .models import Absence, AbsenceReason


@admin.register(AbsenceReason)
class AbsenceReasonAdmin(admin.ModelAdmin):
    list_display = ("name", "requires_certificate", "is_active")
    search_fields = ("name",)

    def get_queryset(self, request):
        return AbsenceReason.objects.all_tenants()


@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "reason", "status", "is_auto_detected")
    list_filter = ("status", "reason", "is_auto_detected")
    search_fields = ("employee__matricule", "employee__user__email")
    autocomplete_fields = ("employee", "reason", "reviewed_by")

    def get_queryset(self, request):
        return Absence.objects.all_tenants()
