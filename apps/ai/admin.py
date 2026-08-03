from django.contrib import admin

from .models import AIRequestLog


@admin.register(AIRequestLog)
class AIRequestLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "tenant", "user", "kind", "success", "tokens_used")
    list_filter = ("kind", "success", "tenant")
    search_fields = ("prompt_excerpt", "error_message")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
