from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.absences.models import Absence
from apps.accounts.models import User
from apps.ai.models import AIDailySummary, AIRequestLog
from apps.ai.providers import AIProviderError, get_provider
from apps.attendance.models import Attendance
from apps.tenants.models import Organization


class Command(BaseCommand):
    """CDC §15.3.1 : « Résumé quotidien automatique — envoi chaque matin d'un
    résumé des absences, retards et anomalies de la veille. » À exécuter une
    fois par jour, après le début de journée (aucune tâche planifiée ne le
    fait encore — Celery/Redis absents) :
        0 7 * * *  cd /app && python manage.py generate_ai_daily_summary
    """

    help = "Génère et envoie le résumé quotidien GeoIA (absences/retards de la veille) pour chaque organisation active."

    def handle(self, *args, **options):
        if not (settings.AI_ENABLED and settings.AI_API_KEY):
            self.stdout.write("GeoIA n'est pas configuré (AI_ENABLED/AI_API_KEY) — aucun résumé généré.")
            return

        sent = 0
        for tenant in Organization.objects.filter(status=Organization.Status.ACTIVE):
            # RM-HOR (fuseau horaire) : "hier" doit être calculé dans le fuseau
            # de CHAQUE organisation, pas celui du serveur — cette commande ne
            # passe jamais par TenantMiddleware (pas de requête HTTP), donc le
            # fuseau doit être activé explicitement ici, tenant par tenant.
            # Sans ça, clock_date/Absence.date (posés selon le fuseau de
            # l'organisation) et le "hier" utilisé pour les interroger ici
            # pouvaient désigner deux jours différents.
            timezone.activate(tenant.timezone)
            try:
                yesterday = timezone.localdate() - timedelta(days=1)
                if self._generate_for_tenant(tenant, yesterday):
                    sent += 1
            finally:
                timezone.deactivate()

        self.stdout.write(self.style.SUCCESS(f"{sent} résumé(s) quotidien(s) généré(s)."))

    def _generate_for_tenant(self, tenant, yesterday):
        if AIDailySummary.objects.filter(tenant=tenant, date=yesterday).exists():
            return False

        late_count = Attendance.objects.all_tenants().filter(
            tenant=tenant, clock_date=yesterday, clock_type=Attendance.ClockType.ARRIVAL,
            status=Attendance.Status.LATE,
        ).count()
        absent_reasons = list(
            Absence.objects.all_tenants().filter(tenant=tenant, date=yesterday)
            .values_list("reason__name", flat=True)
        )
        data_summary = (
            f"Organisation : {tenant.display_name}. Date : {yesterday:%d/%m/%Y}.\n"
            f"Retards enregistrés : {late_count}.\n"
            f"Absences signalées : {len(absent_reasons)} "
            f"({', '.join(absent_reasons) if absent_reasons else 'aucune'})."
        )

        try:
            provider = get_provider(settings.AI_PROVIDER, settings.AI_API_KEY)
            content, tokens_used = provider.chat(
                messages=[
                    {"role": "system", "content": (
                        "Tu es GeoIA. Rédige un résumé quotidien de présence en 3-4 phrases maximum, "
                        "concis et actionnable, à destination d'un administrateur RH. "
                        "N'invente aucune donnée en dehors de celle fournie."
                    )},
                    {"role": "user", "content": data_summary},
                ],
                model=settings.AI_MODEL, temperature=settings.AI_TEMPERATURE,
            )
        except AIProviderError as exc:
            AIRequestLog.objects.create(
                tenant=tenant, kind=AIRequestLog.Kind.DAILY_SUMMARY,
                prompt_excerpt=data_summary[:255], success=False, error_message=str(exc)[:255],
            )
            self.stderr.write(f"{tenant.display_name} : échec de génération ({exc}).")
            return False

        AIDailySummary.objects.create(tenant=tenant, date=yesterday, content=content)
        AIRequestLog.objects.create(
            tenant=tenant, kind=AIRequestLog.Kind.DAILY_SUMMARY,
            prompt_excerpt=data_summary[:255], success=True, tokens_used=tokens_used,
        )

        admin_emails = list(
            User.objects.filter(tenant=tenant, role=User.Role.ADMIN, is_active=True)
            .values_list("email", flat=True)
        )
        if admin_emails:
            send_mail(
                subject=f"GeoPresence — Résumé du {yesterday:%d/%m/%Y}",
                message=content,
                from_email=None,
                recipient_list=admin_emails,
            )
        return True
