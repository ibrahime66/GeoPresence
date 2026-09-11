from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import FormView, TemplateView

from apps.audit import services as audit
from apps.audit.models import AuditLog
from apps.security import captcha, ratelimit
from apps.tenants.models import Organization
from apps.tenants.org_settings import get_org_setting, lockout_duration_minutes

from . import sessions
from .constants import (
    ADMIN_ROLES,
    CAPTCHA_FAILURE_THRESHOLD,
    LOGIN_RATE_LIMIT_MAX_ATTEMPTS,
    LOGIN_RATE_LIMIT_WINDOW_SECONDS,
    PASSWORD_RESET_TOKEN_LIFETIME_MINUTES,
    PWRESET_RATE_LIMIT_MAX,
    PWRESET_RATE_LIMIT_WINDOW,
    REPEATED_LOCKOUT_THRESHOLD,
)
from .forms import BootstrapPasswordChangeForm, BootstrapSetPasswordForm, LoginForm, PasswordResetRequestForm
from .models import PasswordResetToken, UserSession
from .password_policy import record_password

User = get_user_model()

GENERIC_LOGIN_ERROR = "Identifiants incorrects."


def _captcha_context():
    return {
        "captcha_enabled": captcha.is_enabled(),
        "hcaptcha_site_key": getattr(settings, "HCAPTCHA_SITE_KEY", ""),
    }


class LoginView(FormView):
    """CDC §5.2. Toutes les vérifications sont re-décrites étape par étape ;
    les messages restent volontairement génériques quand la révélation d'une
    information (existence du compte...) serait un risque de sécurité."""

    template_name = "accounts/login.html"
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_captcha_context())
        submitted_email = self.request.POST.get("email", "").strip().lower()
        context["show_captcha"] = bool(
            submitted_email and captcha.is_required(submitted_email, threshold=CAPTCHA_FAILURE_THRESHOLD)
        )
        return context

    def form_valid(self, form):
        request = self.request
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        ip = ratelimit.get_client_ip(request)

        # Anti brute-force par IP (CDC §13.3.1) — ne compte que les ÉCHECS
        # (cf. constants.LOGIN_RATE_LIMIT_MAX_ATTEMPTS) : on lit le compteur
        # SANS l'incrémenter ici, pour qu'une simple tentative de connexion
        # (réussie ou non) ne consomme jamais le budget d'une autre personne
        # derrière la même IP partagée. Chaque échec l'incrémente plus bas
        # (cf. `_register_login_failure`).
        if ratelimit.get_count("login_fail_ip", ip) >= LOGIN_RATE_LIMIT_MAX_ATTEMPTS:
            audit.log_event(
                request, audit.LOGIN_FAILURE, AuditLog.Result.FAILURE, description=f"Limite de débit dépassée (IP {ip})"
            )
            form.add_error(None, "Trop de tentatives échouées depuis cette adresse. Réessayez dans une minute.")
            return self.form_invalid(form)

        # CDC §13.4 : CAPTCHA après 3 échecs sur cet e-mail. Neutralisé tant
        # qu'aucune clé hCaptcha n'est configurée (`captcha.is_enabled`).
        if captcha.is_required(email, threshold=CAPTCHA_FAILURE_THRESHOLD):
            if not captcha.verify(request.POST.get("h-captcha-response", ""), ip):
                audit.log_event(
                    request, audit.LOGIN_FAILURE, AuditLog.Result.FAILURE, description="CAPTCHA invalide ou manquant"
                )
                form.add_error(None, "Merci de valider le CAPTCHA avant de continuer.")
                return self.form_invalid(form)

        user = User.objects.filter(email=email).first()

        if user is None:
            # Égalise le temps de réponse avec le cas « e-mail connu, mot de
            # passe faux » (audit sécurité §7) : sans ce hachage bidon, le fait
            # qu'Argon2 ne tourne pas rend un compte inexistant distinguable
            # par simple mesure du temps de réponse (cf. Django #20760).
            User().set_password(password)
            captcha.register_failure(email)
            ratelimit.hit(
                "login_fail_ip", ip, limit=LOGIN_RATE_LIMIT_MAX_ATTEMPTS, window_seconds=LOGIN_RATE_LIMIT_WINDOW_SECONDS
            )
            audit.log_event(
                request, audit.LOGIN_FAILURE, AuditLog.Result.FAILURE, description=f"E-mail inconnu : {email}"
            )
            form.add_error(None, GENERIC_LOGIN_ERROR)
            return self.form_invalid(form)

        if user.tenant_id and user.tenant.status != Organization.Status.ACTIVE:
            captcha.register_failure(email)
            ratelimit.hit(
                "login_fail_ip", ip, limit=LOGIN_RATE_LIMIT_MAX_ATTEMPTS, window_seconds=LOGIN_RATE_LIMIT_WINDOW_SECONDS
            )
            audit.log_event(
                request, audit.LOGIN_FAILURE, AuditLog.Result.FAILURE, user=user, description="Organisation suspendue"
            )
            form.add_error(None, "Votre organisation est temporairement suspendue.")
            return self.form_invalid(form)

        if not user.is_active:
            captcha.register_failure(email)
            ratelimit.hit(
                "login_fail_ip", ip, limit=LOGIN_RATE_LIMIT_MAX_ATTEMPTS, window_seconds=LOGIN_RATE_LIMIT_WINDOW_SECONDS
            )
            audit.log_event(
                request, audit.LOGIN_FAILURE, AuditLog.Result.FAILURE, user=user, description="Compte inactif"
            )
            form.add_error(None, "Votre compte est suspendu. Contactez votre administrateur.")
            return self.form_invalid(form)

        now = timezone.now()
        if user.locked_until and user.locked_until > now:
            captcha.register_failure(email)
            ratelimit.hit(
                "login_fail_ip", ip, limit=LOGIN_RATE_LIMIT_MAX_ATTEMPTS, window_seconds=LOGIN_RATE_LIMIT_WINDOW_SECONDS
            )
            audit.log_event(
                request, audit.LOGIN_FAILURE, AuditLog.Result.FAILURE, user=user, description="Compte verrouillé"
            )
            minutes_left = max(1, int((user.locked_until - now).total_seconds() // 60) + 1)
            form.add_error(None, f"Compte temporairement verrouillé. Réessayez dans {minutes_left} min.")
            return self.form_invalid(form)

        if not user.check_password(password):
            captcha.register_failure(email)
            ratelimit.hit(
                "login_fail_ip", ip, limit=LOGIN_RATE_LIMIT_MAX_ATTEMPTS, window_seconds=LOGIN_RATE_LIMIT_WINDOW_SECONDS
            )
            user.failed_login_attempts += 1
            max_attempts = get_org_setting(user.tenant, "max_failed_login_attempts")
            if user.failed_login_attempts >= max_attempts:
                duration = lockout_duration_minutes(user.tenant, user.lockout_count)
                user.locked_until = now + timedelta(minutes=duration)
                user.failed_login_attempts = 0
                user.lockout_count += 1
                user.save(update_fields=["failed_login_attempts", "locked_until", "lockout_count"])
                audit.log_event(
                    request,
                    audit.ACCOUNT_LOCKED,
                    AuditLog.Result.FAILURE,
                    user=user,
                    description=f"Verrouillage n°{user.lockout_count} après {max_attempts} échecs ({duration} min)",
                )
                self._notify_lockout(user, duration)
                form.add_error(
                    None, f"Compte verrouillé pendant {duration} minutes suite à plusieurs échecs."
                )
            else:
                user.save(update_fields=["failed_login_attempts"])
                audit.log_event(
                    request, audit.LOGIN_FAILURE, AuditLog.Result.FAILURE, user=user, description="Mot de passe incorrect"
                )
                form.add_error(None, GENERIC_LOGIN_ERROR)
            return self.form_invalid(form)

        # Succès.
        captcha.reset(email)
        user.failed_login_attempts = 0
        user.locked_until = None
        user.lockout_count = 0
        user.save(update_fields=["failed_login_attempts", "locked_until", "lockout_count"])

        auth_login(request, user)
        duration_hours_key = "session_duration_admin_hours" if user.role in ADMIN_ROLES else "session_duration_employee_hours"
        request.session.set_expiry(get_org_setting(user.tenant, duration_hours_key) * 3600)
        sessions.register_session(request, user)

        audit.log_event(request, audit.LOGIN_SUCCESS, AuditLog.Result.SUCCESS, user=user)

        if user.must_change_password:
            return redirect("accounts:force_password_change")
        return redirect(self._safe_next_url() or "core:dashboard")

    def _safe_next_url(self):
        """RM-QR-001 (entre autres) : ramène l'utilisateur exactement là où il
        allait avant d'être stoppé par LoginRequiredMixin (ex. scan d'un QR
        d'agence) plutôt que toujours sur le tableau de bord. Validation
        stricte (host/scheme) : `next` est une donnée utilisateur, jamais
        suivie sans vérification (open redirect, CDC sécurité)."""
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={self.request.get_host()}, require_https=self.request.is_secure()
        ):
            return next_url
        return None

    @staticmethod
    def _notify_lockout(user, duration_minutes):
        """CDC §13.3.1 : e-mail à l'utilisateur à chaque verrouillage, et aux
        Administrateurs de l'organisation en cas de blocage répété."""
        send_mail(
            subject="Votre compte GeoPresence a été verrouillé",
            message=render_to_string(
                "accounts/emails/account_locked_email.txt",
                {"user": user, "duration_minutes": duration_minutes},
            ),
            from_email=None,
            recipient_list=[user.email],
        )

        if user.lockout_count >= REPEATED_LOCKOUT_THRESHOLD and user.tenant_id:
            admin_emails = list(
                User.objects.filter(tenant=user.tenant, role=User.Role.ADMIN, is_active=True).values_list(
                    "email", flat=True
                )
            )
            if admin_emails:
                send_mail(
                    subject=f"Verrouillages répétés du compte {user.email}",
                    message=render_to_string(
                        "accounts/emails/account_locked_admin_email.txt",
                        {"user": user, "duration_minutes": duration_minutes, "lockout_count": user.lockout_count},
                    ),
                    from_email=None,
                    recipient_list=admin_emails,
                )


class LogoutView(LoginRequiredMixin, View):
    """Déconnexion volontaire uniquement en POST (CDC §5.3.2) — évite qu'un
    simple lien/image cross-site puisse déclencher une déconnexion (CSRF)."""

    def post(self, request):
        user = request.user
        audit.log_event(request, audit.LOGOUT, AuditLog.Result.SUCCESS, user=user)
        # auth_logout() va flush() la session (supprime la ligne Session
        # Django) — nettoie la ligne de suivi UserSession correspondante
        # avant, sinon elle resterait orpheline (session_key recyclable).
        UserSession.objects.filter(session_key=request.session.session_key).delete()
        auth_logout(request)
        messages.success(request, "Vous avez été déconnecté.")
        return redirect("core:home")


class ForcePasswordChangeView(LoginRequiredMixin, FormView):
    """CDC §5.5 (changement obligatoire à la première connexion) — sert aussi
    de vue de changement de mot de passe volontaire ultérieur (même logique)."""

    template_name = "accounts/force_password_change.html"
    form_class = BootstrapPasswordChangeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        user.must_change_password = False
        user.last_password_change = timezone.now()
        user.save(update_fields=["must_change_password", "last_password_change"])
        record_password(user)
        # Garde la session courante active après le changement (évite une
        # auto-déconnexion surprenante) tout en respectant Django (le hash de
        # session dépend du mot de passe).
        update_session_auth_hash(self.request, user)
        audit.log_event(self.request, audit.PASSWORD_CHANGED, AuditLog.Result.SUCCESS, user=user)
        messages.success(self.request, "Mot de passe mis à jour avec succès.")
        # RM-AUTH-008 : invalide les AUTRES sessions actives de ce compte —
        # la session courante (déjà réhachée ci-dessus) est explicitement épargnée.
        sessions.revoke_all_sessions(user, except_session_key=self.request.session.session_key)
        return redirect("core:dashboard")


class PasswordResetRequestView(FormView):
    """CDC §5.4. Ne révèle jamais si l'e-mail existe (RM-AUTH-005) : la
    redirection est identique dans tous les cas."""

    template_name = "accounts/password_reset_request.html"
    form_class = PasswordResetRequestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_captcha_context())
        return context

    def form_valid(self, form):
        request = self.request
        ip = ratelimit.get_client_ip(request)

        # Audit sécurité §6 : sans limite, ce formulaire public permet de
        # bombarder d'e-mails de réinitialisation n'importe quel compte (et de
        # noyer le journal d'audit). Réponse identique au cas nominal — on ne
        # révèle jamais qu'on a été limité (cohérent avec RM-AUTH-005).
        if ratelimit.hit("pwreset_ip", ip, limit=PWRESET_RATE_LIMIT_MAX, window_seconds=PWRESET_RATE_LIMIT_WINDOW):
            audit.log_event(
                request, audit.PASSWORD_RESET_REQUESTED, AuditLog.Result.FAILURE,
                description=f"Limite de débit dépassée (IP {ip})",
            )
            return redirect("accounts:password_reset_sent")

        # CDC §13.4 : CAPTCHA systématique sur ce formulaire public (pas de
        # seuil de tentatives — neutralisé si hCaptcha n'est pas configuré).
        if captcha.is_enabled() and not captcha.verify(
            request.POST.get("h-captcha-response", ""), ip
        ):
            form.add_error(None, "Merci de valider le CAPTCHA avant de continuer.")
            return self.form_invalid(form)

        email = form.cleaned_data["email"]
        user = User.objects.filter(email=email, is_active=True).first()

        eligible = user is not None and (user.tenant_id is None or user.tenant.status == Organization.Status.ACTIVE)

        if eligible:
            token = PasswordResetToken.issue_for(user)
            reset_url = request.build_absolute_uri(reverse("accounts:password_reset_confirm", args=[token.id]))
            send_mail(
                subject="Réinitialisation de votre mot de passe",
                message=render_to_string(
                    "accounts/emails/password_reset_email.txt",
                    {
                        "user": user,
                        "reset_url": reset_url,
                        "lifetime_minutes": PASSWORD_RESET_TOKEN_LIFETIME_MINUTES,
                    },
                ),
                from_email=None,
                recipient_list=[user.email],
            )
            audit.log_event(request, audit.PASSWORD_RESET_REQUESTED, AuditLog.Result.SUCCESS, user=user)
        else:
            audit.log_event(
                request,
                audit.PASSWORD_RESET_REQUESTED,
                AuditLog.Result.FAILURE,
                description=f"E-mail inconnu ou inéligible : {email}",
            )

        return redirect("accounts:password_reset_sent")


class PasswordResetSentView(TemplateView):
    template_name = "accounts/password_reset_sent.html"


class PasswordResetConfirmView(FormView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = BootstrapSetPasswordForm

    def dispatch(self, request, *args, **kwargs):
        self.reset_token = PasswordResetToken.objects.filter(pk=kwargs["token"]).select_related("user").first()
        self.token_valid = bool(self.reset_token and self.reset_token.is_valid())
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not self.token_valid:
            return render(request, "accounts/password_reset_invalid.html", status=400)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.token_valid:
            return render(request, "accounts/password_reset_invalid.html", status=400)
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.reset_token.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        user.must_change_password = False
        user.last_password_change = timezone.now()
        user.failed_login_attempts = 0
        user.locked_until = None
        user.lockout_count = 0
        user.save(
            update_fields=[
                "must_change_password",
                "last_password_change",
                "failed_login_attempts",
                "locked_until",
                "lockout_count",
            ]
        )
        record_password(user)
        captcha.reset(user.email)
        self.reset_token.used_at = timezone.now()
        self.reset_token.save(update_fields=["used_at"])
        audit.log_event(self.request, audit.PASSWORD_RESET_COMPLETED, AuditLog.Result.SUCCESS, user=user)
        # RM-AUTH-008 : aucune session courante à épargner ici (l'utilisateur
        # n'est pas authentifié pendant un reset de mot de passe) — tout est révoqué.
        sessions.revoke_all_sessions(user)
        return redirect("accounts:password_reset_complete")


class PasswordResetCompleteView(TemplateView):
    template_name = "accounts/password_reset_complete.html"


class ProfileView(LoginRequiredMixin, TemplateView):
    """CDC §3.5.1/§5.6.2 : profil personnel — informations éditables en
    self-service + liste des sessions actives, pour tous les rôles."""

    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        from apps.employees.forms import EmployeeSelfServiceForm
        from apps.employees.services import get_active_employee

        context = super().get_context_data(**kwargs)
        employee = get_active_employee(self.request.user)
        context["employee"] = employee
        if employee is not None:
            context["form"] = EmployeeSelfServiceForm(instance=employee)
        context["sessions"] = self.request.user.sessions.order_by("-last_activity_at")
        context["current_session_key"] = self.request.session.session_key

        from .forms import LanguageForm
        from .password_policy import password_expires_at

        context["password_expires_at"] = password_expires_at(self.request.user)
        context["language_form"] = LanguageForm(instance=self.request.user)
        return context


class ProfileUpdateView(LoginRequiredMixin, View):
    def post(self, request):
        from apps.employees.forms import EmployeeSelfServiceForm
        from apps.employees.services import get_active_employee

        employee = get_active_employee(request.user)
        if employee is None:
            messages.error(request, "Aucun profil employé actif associé à ce compte.")
            return redirect("accounts:profile")

        form = EmployeeSelfServiceForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour.")
        else:
            messages.error(request, "Formulaire invalide, vérifiez les champs.")
        return redirect("accounts:profile")


class SessionRevokeView(LoginRequiredMixin, View):
    """CDC §5.6.2 : l'utilisateur révoque n'importe laquelle de ses sessions
    distantes — jamais la session courante depuis cette page (utiliser
    Déconnexion pour ça, plus explicite)."""

    def post(self, request, pk):
        user_session = get_object_or_404(UserSession, pk=pk, user=request.user)
        if user_session.session_key == request.session.session_key:
            messages.error(request, "Impossible de révoquer votre session actuelle ici, utilisez « Se déconnecter ».")
            return redirect("accounts:profile")
        sessions.revoke_session(user_session)
        messages.success(request, "Session révoquée.")
        return redirect("accounts:profile")


class LanguageUpdateView(LoginRequiredMixin, View):
    """CDC §3.5.1/§24.2 : langue d'affichage — self-service, tous rôles."""

    def post(self, request):
        from .forms import LanguageForm

        form = LanguageForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Langue mise à jour.")
        else:
            messages.error(request, "Langue invalide.")
        return redirect("accounts:profile")
