from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("password/change/", views.ForcePasswordChangeView.as_view(), name="force_password_change"),
    path("password-reset/", views.PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password-reset/envoye/", views.PasswordResetSentView.as_view(), name="password_reset_sent"),
    path(
        "password-reset/confirmer/<uuid:token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("password-reset/termine/", views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("profil/", views.ProfileView.as_view(), name="profile"),
    path("profil/modifier/", views.ProfileUpdateView.as_view(), name="profile_update"),
    path("profil/sessions/<uuid:pk>/revoquer/", views.SessionRevokeView.as_view(), name="session_revoke"),
    path("profil/langue/", views.LanguageUpdateView.as_view(), name="language_update"),
]
