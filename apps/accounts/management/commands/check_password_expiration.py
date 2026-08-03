from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.constants import PASSWORD_EXPIRATION_WARNING_DAYS
from apps.accounts.password_policy import password_expires_at

User = get_user_model()


class Command(BaseCommand):
    """CDC §13.2.1 : « Avertissement 7 jours avant expiration » du mot de
    passe (durée d'expiration elle-même configurable par organisation, cf.
    apps.tenants.org_settings). À exécuter une fois par jour (aucune tâche
    planifiée ne le fait encore — Celery/Redis absents) :
        0 7 * * *  cd /app && python manage.py check_password_expiration
    """

    help = "Envoie un e-mail d'avertissement aux comptes dont le mot de passe expire dans N jours."

    def handle(self, *args, **options):
        today = timezone.localdate()
        target_date = today + timedelta(days=PASSWORD_EXPIRATION_WARNING_DAYS)

        candidates = User.objects.filter(
            is_active=True,
            last_password_change__isnull=False,
            must_change_password=False,
        )

        sent = 0
        for user in candidates:
            expires_at = password_expires_at(user)
            if expires_at is None or expires_at.date() != target_date:
                continue
            send_mail(
                subject="Votre mot de passe GeoPresence expire bientôt",
                message=(
                    f"Bonjour {user.first_name or user.email},\n\n"
                    f"Votre mot de passe expirera le {expires_at:%d/%m/%Y} "
                    f"(dans {PASSWORD_EXPIRATION_WARNING_DAYS} jours). "
                    "Changez-le dès maintenant depuis votre profil pour éviter toute interruption d'accès."
                ),
                from_email=None,
                recipient_list=[user.email],
            )
            sent += 1

        self.stdout.write(self.style.SUCCESS(f"{sent} avertissement(s) envoyé(s)."))
