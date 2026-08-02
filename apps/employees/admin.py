from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("matricule", "user", "department", "position", "primary_agency", "contract_type", "status")
    list_filter = ("status", "contract_type", "department", "primary_agency")
    search_fields = ("matricule", "user__email", "user__first_name", "user__last_name")
    autocomplete_fields = ("user", "department", "position", "primary_agency", "manager")
    filter_horizontal = ("secondary_agencies",)

    def get_queryset(self, request):
        return Employee.objects.all_tenants()
