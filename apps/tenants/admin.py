from django.contrib import admin

from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("display_name", "slug", "org_type", "status", "country", "created_at")
    list_filter = ("status", "org_type", "country")
    search_fields = ("display_name", "legal_name", "slug", "email")
    prepopulated_fields = {"slug": ("display_name",)}
