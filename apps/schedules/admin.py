from django.contrib import admin

from .models import EmployeeScheduleAssignment, Schedule, ScheduleSlot


class ScheduleSlotInline(admin.TabularInline):
    model = ScheduleSlot
    extra = 1
    fields = ("weekday", "start_time", "end_time", "break_start_time", "break_end_time")


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("name", "schedule_type", "is_active")
    list_filter = ("schedule_type", "is_active")
    search_fields = ("name",)
    inlines = [ScheduleSlotInline]

    def get_queryset(self, request):
        return Schedule.objects.all_tenants()


@admin.register(EmployeeScheduleAssignment)
class EmployeeScheduleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("employee", "schedule", "valid_from", "valid_until")
    list_filter = ("schedule",)
    autocomplete_fields = ("employee", "schedule")

    def get_queryset(self, request):
        return EmployeeScheduleAssignment.objects.all_tenants()
