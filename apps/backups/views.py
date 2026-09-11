from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.core.management import call_command
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User

from .models import Backup

SUPER_ADMIN_ONLY = (User.Role.SUPER_ADMIN,)


class BackupListView(RoleRequiredMixin, ListView):
    allowed_roles = SUPER_ADMIN_ONLY
    model = Backup
    template_name = "backups/backup_list.html"
    context_object_name = "backups"
    paginate_by = 25


class BackupCreateView(RoleRequiredMixin, View):
    """CDC §18.4.2 : déclenchement manuel. Synchrone (pas de Celery
    disponible) — acceptable aux volumes actuels, à revoir si le dump devient
    trop long pour un cycle requête/réponse HTTP."""

    allowed_roles = SUPER_ADMIN_ONLY

    def post(self, request):
        comment = request.POST.get("comment", "")
        try:
            call_command("backup_database", manual=True, comment=comment, user_id=str(request.user.id))
            messages.success(request, "Sauvegarde manuelle créée avec succès.")
        except Exception as exc:  # noqa: BLE001 — toute cause d'échec doit remonter à l'utilisateur.
            messages.error(request, f"Échec de la sauvegarde : {exc}")
        return redirect("backups:list")


class BackupDownloadView(RoleRequiredMixin, View):
    allowed_roles = SUPER_ADMIN_ONLY

    def get(self, request, pk):
        backup = get_object_or_404(Backup, pk=pk, status=Backup.Status.SUCCESS)
        # Audit sécurité §12 : confine le chemin dans BACKUP_DIR même si
        # `filename` (généré par la commande de sauvegarde) contenait un jour
        # une séquence « ../ ».
        backup_dir = Path(settings.BACKUP_DIR).resolve()
        path = (backup_dir / backup.filename).resolve()
        if not path.is_relative_to(backup_dir) or not path.is_file():
            raise Http404("Fichier de sauvegarde introuvable sur le disque.")
        return FileResponse(open(path, "rb"), as_attachment=True, filename=Path(backup.filename).name)
