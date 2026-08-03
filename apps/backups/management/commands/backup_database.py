import os
import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.accounts.models import User
from apps.backups import crypto
from apps.backups.models import Backup
from apps.backups.retention import apply_retention


class Command(BaseCommand):
    """CDC §18.4.1/§18.4.2 : sauvegarde complète de la base de données,
    chiffrée (AES-256-GCM) et vérifiée par checksum SHA-256.

    Aucune tâche planifiée (Celery/Redis absents, cf. requirements/production.txt)
    ne déclenche encore cette commande automatiquement — à brancher sur cron :
        0 2 * * *  cd /app && python manage.py backup_database
    Seul le dump complet est implémenté (pas de sauvegarde différentielle
    6h — nécessiterait un archivage des binlogs MySQL, hors périmètre actuel).
    """

    help = "Sauvegarde chiffrée complète de la base de données MySQL."

    def add_arguments(self, parser):
        parser.add_argument("--comment", default="", help="Commentaire libre (sauvegarde manuelle).")
        parser.add_argument("--manual", action="store_true", help="Marque la sauvegarde comme déclenchée manuellement.")
        parser.add_argument("--user-id", default=None, help="UUID de l'utilisateur à l'origine (sauvegarde manuelle).")

    def handle(self, *args, **options):
        if shutil.which("mysqldump") is None:
            raise CommandError("mysqldump introuvable sur ce système — impossible de sauvegarder.")

        db = settings.DATABASES["default"]
        now = timezone.now()
        filename = f"backup_{now:%Y%m%d_%H%M%S}.sql.enc"
        backup_dir = Path(settings.BACKUP_DIR)
        backup_dir.mkdir(parents=True, exist_ok=True)
        dest_path = backup_dir / filename

        triggered_by = None
        if options.get("user_id"):
            triggered_by = User.objects.filter(pk=options["user_id"]).first()

        try:
            dump = self._run_mysqldump(db)
            encrypted = crypto.encrypt_bytes(dump)
            checksum = crypto.sha256_of(encrypted)
            dest_path.write_bytes(encrypted)

            secondary_path = ""
            if settings.BACKUP_SECONDARY_DIR:
                secondary_dir = Path(settings.BACKUP_SECONDARY_DIR)
                secondary_dir.mkdir(parents=True, exist_ok=True)
                secondary_full = secondary_dir / filename
                secondary_full.write_bytes(encrypted)
                secondary_path = str(secondary_full)

            backup = Backup.objects.create(
                filename=filename,
                size_bytes=len(encrypted),
                checksum_sha256=checksum,
                is_manual=options["manual"],
                triggered_by=triggered_by,
                comment=options["comment"],
                status=Backup.Status.SUCCESS,
                secondary_path=secondary_path,
                last_verified_at=now,
                last_verification_ok=True,
            )
        except Exception as exc:  # noqa: BLE001 — toute erreur doit être journalisée puis notifiée, pas juste tracée.
            Backup.objects.create(
                filename=filename,
                is_manual=options["manual"],
                triggered_by=triggered_by,
                comment=options["comment"],
                status=Backup.Status.FAILED,
                error_message=str(exc)[:2000],
            )
            self._notify(success=False, detail=str(exc))
            raise CommandError(f"Échec de la sauvegarde : {exc}") from exc

        if not options["manual"]:
            apply_retention()
        self._notify(success=True, detail=f"{filename} ({backup.size_bytes} octets)")
        self.stdout.write(self.style.SUCCESS(f"Sauvegarde créée : {filename} ({backup.size_bytes} octets)."))

    @staticmethod
    def _run_mysqldump(db):
        cmd = [
            "mysqldump",
            f"--host={db['HOST'] or 'localhost'}",
            f"--port={db['PORT'] or 3306}",
            f"--user={db['USER']}",
            "--single-transaction",
            "--routines",
            "--triggers",
            db["NAME"],
        ]
        env = os.environ.copy()
        if db.get("PASSWORD"):
            env["MYSQL_PWD"] = db["PASSWORD"]  # évite d'exposer le mot de passe dans la liste des process.
        result = subprocess.run(cmd, env=env, capture_output=True, timeout=1800)
        if result.returncode != 0:
            raise CommandError(f"mysqldump a échoué : {result.stderr.decode(errors='replace')[:2000]}")
        return result.stdout

    @staticmethod
    def _notify(success, detail):
        """CDC §17.2 : 'Sauvegarde réussie'/'Sauvegarde échouée' -> Super Admin.
        Canal SMS de la table CDC non disponible (aucun fournisseur configuré) —
        e-mail uniquement."""
        recipients = list(User.objects.filter(role=User.Role.SUPER_ADMIN, is_active=True).values_list("email", flat=True))
        if not recipients:
            return
        subject = "Sauvegarde GeoPresence réussie" if success else "ÉCHEC de la sauvegarde GeoPresence"
        message = f"{'Succès' if success else 'Échec'} — {detail}"
        send_mail(subject=subject, message=message, from_email=None, recipient_list=recipients)
