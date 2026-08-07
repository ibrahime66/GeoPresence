from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("", views.HomeView.as_view(), name="home"),
    path("confidentialite/", views.PrivacyView.as_view(), name="privacy"),
    path("conditions-utilisation/", views.TermsView.as_view(), name="terms"),
    path("faq/", views.FaqView.as_view(), name="faq"),
    path("dashboard/", views.DashboardPlaceholderView.as_view(), name="dashboard"),
    path("service-worker.js", views.ServiceWorkerView.as_view(), name="service_worker"),
]
