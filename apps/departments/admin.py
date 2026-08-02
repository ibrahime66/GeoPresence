from django.contrib import admin

from .models import Department, Position


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    search_fields = ("name", "code")

    def get_queryset(self, request):
        return Department.objects.all_tenants()


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)

    def get_queryset(self, request):
        return Position.objects.all_tenants()
