"""Politique de rétention (GFS simplifié) — CDC §18.4.1 : 7 sauvegardes
quotidiennes, 4 hebdomadaires, 3 mensuelles. Ne s'applique qu'aux sauvegardes
AUTOMATIQUES — une sauvegarde manuelle est une action explicite de
l'utilisateur, jamais supprimée automatiquement."""

from pathlib import Path

from django.conf import settings

from .models import Backup

DAILY_KEEP = 7
WEEKLY_KEEP = 4
MONTHLY_KEEP = 3


def apply_retention():
    successful = list(
        Backup.objects.filter(status=Backup.Status.SUCCESS, is_manual=False).order_by("-created_at")
    )

    keep_ids = {b.id for b in successful[:DAILY_KEEP]}

    seen_weeks = set()
    for b in successful:
        week_key = b.created_at.isocalendar()[:2]
        if week_key not in seen_weeks and len(seen_weeks) < WEEKLY_KEEP:
            seen_weeks.add(week_key)
            keep_ids.add(b.id)

    seen_months = set()
    for b in successful:
        month_key = (b.created_at.year, b.created_at.month)
        if month_key not in seen_months and len(seen_months) < MONTHLY_KEEP:
            seen_months.add(month_key)
            keep_ids.add(b.id)

    for backup in successful:
        if backup.id in keep_ids:
            continue
        _delete_files(backup)
        backup.delete()


def _delete_files(backup):
    for path_str in (str(Path(settings.BACKUP_DIR) / backup.filename), backup.secondary_path):
        if not path_str:
            continue
        path = Path(path_str)
        if path.exists():
            path.unlink(missing_ok=True)
