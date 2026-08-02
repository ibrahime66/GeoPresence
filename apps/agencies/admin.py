from django.contrib import admin

from .models import Agency


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "agency_type", "city", "country", "radius_meters", "is_active")
    list_filter = ("agency_type", "is_active", "country")
    search_fields = ("name", "code", "city")

    def get_queryset(self, request):
        # Vue admin technique : on contourne volontairement le filtrage par
        # tenant courant (aucune session tenant n'existe côté /admin/).
        return Agency.objects.all_tenants()
