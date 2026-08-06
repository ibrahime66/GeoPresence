from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("", views.HomeView.as_view(), name="home"),
    path("dashboard/", views.DashboardPlaceholderView.as_view(), name="dashboard"),
    path("service-worker.js", views.ServiceWorkerView.as_view(), name="service_worker"),
]
