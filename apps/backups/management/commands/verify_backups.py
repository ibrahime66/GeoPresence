from pathlib import Path

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.backups import crypto
from apps.backups.models import Backup


class Command(BaseCommand):
    """CDC §18.4.4 : « test de restauration automatique hebdomadaire ».

    Simplifié en un contrôle d'intégrité (déchiffrement + vérification du
    checksum SHA-256) plutôt qu'une restauration complète sur un
    environnement de test séparé (aucun environnement de ce type disponible
    ici) — détecte déjà la corruption ou l'altération d'une sauvegarde, ce
    qui est le risque principal visé par le CDC à cet endroit.

    À planifier également via cron/Celery Beat, ex. :
        0 3 * * 0  cd /app && python manage.py verify_backups
    """

    help = "Vérifie l'intégrité (déchiffrement + checksum) de la sauvegarde la plus récente."

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true", help="Vérifie toutes les sauvegardes réussies, pas juste la dernière.")

    def handle(self, *args, **options):
        qs = Backup.objects.filter(status=Backup.Status.SUCCESS).order_by("-created_at")
        targets = list(qs) if options["all"] else list(qs[:1])

        if not targets:
            self.stdout.write("Aucune sauvegarde à vérifier.")
            return

        results = []
        for backup in targets:
            ok, detail = self._verify_one(backup)
            backup.last_verified_at = timezone.now()
            backup.last_verification_ok = ok
            backup.save(update_fields=["last_verified_at", "last_verification_ok"])
            results.append((backup, ok, detail))

        self._notify(results)
        for backup, ok, detail in results:
            style = self.style.SUCCESS if ok else self.style.ERROR
            self.stdout.write(style(f"{backup.filename} : {'OK' if ok else 'ÉCHEC'} — {detail}"))

    @staticmethod
    def _verify_one(backup):
        path = Path(settings.BACKUP_DIR) / backup.filename
        if not path.exists():
            return False, "Fichier introuvable sur le disque."
        blob = path.read_bytes()
        if crypto.sha256_of(blob) != backup.checksum_sha256:
            return False, "Le checksum SHA-256 ne correspond plus (fichier altéré)."
        try:
            crypto.decrypt_bytes(blob)
        except crypto.BackupEncryptionError as exc:
            return False, str(exc)
        return True, "Déchiffrement et checksum valides."

    @staticmethod
    def _notify(results):
        failed = [r for r in results if not r[1]]
        if not failed:
            return
        recipients = list(User.objects.filter(role=User.Role.SUPER_ADMIN, is_active=True).values_list("email", flat=True))
        if not recipients:
            return
        lines = "\n".join(f"- {b.filename} : {detail}" for b, ok, detail in failed)
        send_mail(
            subject=f"{len(failed)} sauvegarde(s) GeoPresence en échec de vérification",
            message=f"Le contrôle d'intégrité a échoué pour :\n{lines}",
            from_email=None,
            recipient_list=recipients,
        )
