from django.urls import path

from . import views

app_name = "tenants"

urlpatterns = [
    path("organisation/parametres/", views.OrganizationSettingsView.as_view(), name="settings"),
    path("organisation/onboarding/masquer/", views.OnboardingDismissView.as_view(), name="onboarding_dismiss"),
]
