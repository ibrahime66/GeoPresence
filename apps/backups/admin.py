from django.contrib import admin

from .models import Backup


@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ("filename", "created_at", "status", "is_manual", "size_bytes", "last_verification_ok")
    list_filter = ("status", "is_manual", "last_verification_ok")
    search_fields = ("filename", "comment")
    readonly_fields = [f.name for f in Backup._meta.fields if f.name not in ("comment",)]
