import os
import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.backups import crypto
from apps.backups.models import Backup


class Command(BaseCommand):
    """CDC §18.4.4 : restauration à partir d'une sauvegarde.

    Volontairement accessible UNIQUEMENT en ligne de commande (pas de bouton
    web) : une restauration écrase intégralement la base de données courante
    et est irréversible sans une sauvegarde préalable — un risque bien trop
    élevé pour un simple clic dans l'interface Super Admin. Exige une
    confirmation explicite sauf si --yes est passé (usage scripté assumé)."""

    help = "Restaure la base de données à partir d'une sauvegarde chiffrée. DESTRUCTIF — écrase la base courante."

    def add_arguments(self, parser):
        parser.add_argument("backup_id", help="UUID (ou nom de fichier) de la sauvegarde à restaurer.")
        parser.add_argument("--yes", action="store_true", help="Ignore la confirmation interactive.")

    def handle(self, *args, **options):
        if shutil.which("mysql") is None:
            raise CommandError("Le client mysql est introuvable sur ce système.")

        backup = (
            Backup.objects.filter(pk=options["backup_id"]).first()
            or Backup.objects.filter(filename=options["backup_id"]).first()
        )
        if backup is None:
            raise CommandError(f"Sauvegarde introuvable : {options['backup_id']}")
        if backup.status != Backup.Status.SUCCESS:
            raise CommandError("Cette sauvegarde est marquée en échec — restauration refusée.")

        path = Path(settings.BACKUP_DIR) / backup.filename
        if not path.exists():
            raise CommandError(f"Fichier de sauvegarde introuvable : {path}")

        blob = path.read_bytes()
        if crypto.sha256_of(blob) != backup.checksum_sha256:
            raise CommandError("Le checksum ne correspond plus — sauvegarde potentiellement altérée. Restauration refusée.")

        try:
            sql_dump = crypto.decrypt_bytes(blob)
        except crypto.BackupEncryptionError as exc:
            raise CommandError(f"Impossible de déchiffrer la sauvegarde : {exc}") from exc

        db = settings.DATABASES["default"]
        self.stdout.write(
            self.style.WARNING(
                f"⚠️  Ceci va ÉCRASER la base « {db['NAME']} » avec le contenu de « {backup.filename} » "
                f"(créée le {backup.created_at:%d/%m/%Y %H:%M})."
            )
        )
        if not options["yes"]:
            answer = input("Tapez CONFIRMER pour continuer : ")
            if answer.strip() != "CONFIRMER":
                self.stdout.write("Restauration annulée.")
                return

        cmd = [
            "mysql",
            f"--host={db['HOST'] or 'localhost'}",
            f"--port={db['PORT'] or 3306}",
            f"--user={db['USER']}",
            db["NAME"],
        ]
        env = os.environ.copy()
        if db.get("PASSWORD"):
            env["MYSQL_PWD"] = db["PASSWORD"]
        result = subprocess.run(cmd, input=sql_dump, env=env, capture_output=True, timeout=1800)
        if result.returncode != 0:
            raise CommandError(f"La restauration a échoué : {result.stderr.decode(errors='replace')[:2000]}")

        self.stdout.write(self.style.SUCCESS(f"Base de données restaurée depuis « {backup.filename} »."))
