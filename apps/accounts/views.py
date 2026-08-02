from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import FormView, TemplateView

from apps.audit import services as audit
from apps.audit.models import AuditLog
from apps.tenants.models import Organization

from .constants import (
    ADMIN_ROLES,
    LOCKOUT_DURATION_MINUTES,
    MAX_FAILED_LOGIN_ATTEMPTS,
    PASSWORD_RESET_TOKEN_LIFETIME_MINUTES,
    SESSION_DURATION_ADMIN_SECONDS,
    SESSION_DURATION_DEFAULT_SECONDS,
)
from .forms import BootstrapPasswordChangeForm, BootstrapSetPasswordForm, LoginForm, PasswordResetRequestForm
from .models import PasswordResetToken

User = get_user_model()

GENERIC_LOGIN_ERROR = "Identifiants incorrects."


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

    def form_valid(self, form):
        request = self.request
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        user = User.objects.filter(email=email).first()

        if user is None:
            audit.log_event(
                request, audit.LOGIN_FAILURE, AuditLog.Result.FAILURE, description=f"E-mail inconnu : {email}"
            )
            form.add_error(None, GENERIC_LOGIN_ERROR)
            return self.form_invalid(form)

        if user.tenant_id and user.tenant.status != Organization.Status.ACTIVE:
            audit.log_event(
                request, audit.LOGIN_FAILURE, AuditLog.Result.FAILURE, user=user, description="Organisation suspendue"
            )
            form.add_error(None, "Votre organisation est temporairement suspendue.")
            return self.form_invalid(form)

        if not user.is_active:
            audit.log_event(
                request, audit.LOGIN_FAILURE, AuditLog.Result.FAILURE, user=user, description="Compte inactif"
            )
            form.add_error(None, "Votre compte est suspendu. Contactez votre administrateur.")
            return self.form_invalid(form)

        now = timezone.now()
        if user.locked_until and user.locked_until > now:
            audit.log_event(
                request, audit.LOGIN_FAILURE, AuditLog.Result.FAILURE, user=user, description="Compte verrouillé"
            )
            minutes_left = max(1, int((user.locked_until - now).total_seconds() // 60) + 1)
            form.add_error(None, f"Compte temporairement verrouillé. Réessayez dans {minutes_left} min.")
            return self.form_invalid(form)

        if not user.check_password(password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = now + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                user.failed_login_attempts = 0
                user.save(update_fields=["failed_login_attempts", "locked_until"])
                audit.log_event(
                    request,
                    audit.ACCOUNT_LOCKED,
                    AuditLog.Result.FAILURE,
                    user=user,
                    description=f"Verrouillage après {MAX_FAILED_LOGIN_ATTEMPTS} échecs consécutifs",
                )
                form.add_error(
                    None, f"Compte verrouillé pendant {LOCKOUT_DURATION_MINUTES} minutes suite à plusieurs échecs."
                )
            else:
                user.save(update_fields=["failed_login_attempts"])
                audit.log_event(
                    request, audit.LOGIN_FAILURE, AuditLog.Result.FAILURE, user=user, description="Mot de passe incorrect"
                )
                form.add_error(None, GENERIC_LOGIN_ERROR)
            return self.form_invalid(form)

        # Succès.
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save(update_fields=["failed_login_attempts", "locked_until"])

        auth_login(request, user)
        session_duration = (
            SESSION_DURATION_ADMIN_SECONDS if user.role in ADMIN_ROLES else SESSION_DURATION_DEFAULT_SECONDS
        )
        request.session.set_expiry(session_duration)

        audit.log_event(request, audit.LOGIN_SUCCESS, AuditLog.Result.SUCCESS, user=user)

        if user.must_change_password:
            return redirect("accounts:force_password_change")
        return redirect("core:dashboard")


class LogoutView(LoginRequiredMixin, View):
    """Déconnexion volontaire uniquement en POST (CDC §5.3.2) — évite qu'un
    simple lien/image cross-site puisse déclencher une déconnexion (CSRF)."""

    def post(self, request):
        user = request.user
        audit.log_event(request, audit.LOGOUT, AuditLog.Result.SUCCESS, user=user)
        auth_logout(request)
        messages.success(request, "Vous avez été déconnecté.")
        return redirect("accounts:login")


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
        # Garde la session courante active après le changement (évite une
        # auto-déconnexion surprenante) tout en respectant Django (le hash de
        # session dépend du mot de passe).
        update_session_auth_hash(self.request, user)
        audit.log_event(self.request, audit.PASSWORD_CHANGED, AuditLog.Result.SUCCESS, user=user)
        messages.success(self.request, "Mot de passe mis à jour avec succès.")
        # RM-AUTH-008 : invalider les AUTRES sessions actives de ce compte —
        # nécessite le suivi par-utilisateur des sessions (CDC §5.6.2, module
        # UserSession différé). Non implémenté ici.
        return redirect("core:dashboard")


class PasswordResetRequestView(FormView):
    """CDC §5.4. Ne révèle jamais si l'e-mail existe (RM-AUTH-005) : la
    redirection est identique dans tous les cas."""

    template_name = "accounts/password_reset_request.html"
    form_class = PasswordResetRequestForm

    def form_valid(self, form):
        request = self.request
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
        user.save(
            update_fields=["must_change_password", "last_password_change", "failed_login_attempts", "locked_until"]
        )
        self.reset_token.used_at = timezone.now()
        self.reset_token.save(update_fields=["used_at"])
        audit.log_event(self.request, audit.PASSWORD_RESET_COMPLETED, AuditLog.Result.SUCCESS, user=user)
        # RM-AUTH-008 : invalider toutes les sessions actives de ce compte —
        # même limitation différée que ci-dessus (module UserSession).
        return redirect("accounts:password_reset_complete")


class PasswordResetCompleteView(TemplateView):
    template_name = "accounts/password_reset_complete.html"
