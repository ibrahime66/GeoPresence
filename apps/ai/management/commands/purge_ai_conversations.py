from django.core.management.base import BaseCommand

from apps.ai.services import purge_expired_conversations


class Command(BaseCommand):
    """CDC §15.4 : « L'historique des conversations IA est conservé N jours
    (N configurable) ». À exécuter une fois par jour (aucune tâche planifiée
    ne le fait encore — Celery/Redis absents) :
        30 3 * * *  cd /app && python manage.py purge_ai_conversations
    """

    help = "Supprime les conversations IA plus anciennes que la rétention configurée par organisation."

    def handle(self, *args, **options):
        deleted = purge_expired_conversations()
        self.stdout.write(self.style.SUCCESS(f"{deleted} conversation(s) IA supprimée(s)."))
