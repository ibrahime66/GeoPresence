from django.urls import path

from . import views

app_name = "schedules"

urlpatterns = [
    path("horaires/", views.ScheduleListView.as_view(), name="list"),
    path("horaires/nouveau/", views.ScheduleFormView.as_view(), name="create"),
    path("horaires/<uuid:pk>/modifier/", views.ScheduleFormView.as_view(), name="update"),
    path("horaires/<uuid:pk>/basculer/", views.ScheduleToggleActiveView.as_view(), name="toggle_active"),
    path("horaires/salles-sans-professeur/", views.UnstaffedSlotsView.as_view(), name="unstaffed"),
    path("horaires/planning-salles/", views.RoomPlanningView.as_view(), name="room_planning"),
    path("horaires/presence-enseignants/", views.TeacherPresenceView.as_view(), name="teacher_presence"),
    path("horaires/presence-enseignants/export/<str:fmt>/", views.TeacherPresenceExportView.as_view(), name="teacher_presence_export"),
    path("horaires/creneau/<uuid:slot_id>/exception/", views.SlotExceptionView.as_view(), name="slot_exception"),
]
