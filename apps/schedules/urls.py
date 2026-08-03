from django.urls import path

from . import views

app_name = "schedules"

urlpatterns = [
    path("horaires/", views.ScheduleListView.as_view(), name="list"),
    path("horaires/nouveau/", views.ScheduleFormView.as_view(), name="create"),
    path("horaires/<uuid:pk>/modifier/", views.ScheduleFormView.as_view(), name="update"),
    path("horaires/<uuid:pk>/basculer/", views.ScheduleToggleActiveView.as_view(), name="toggle_active"),
]
