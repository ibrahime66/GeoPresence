from django.urls import path

from . import views

app_name = "leaves"

urlpatterns = [
    path("conges/", views.MyLeavesView.as_view(), name="my_leaves"),
    path("conges/soumettre/", views.SubmitLeaveView.as_view(), name="submit"),
    path("conges/<uuid:pk>/annuler/", views.CancelLeaveView.as_view(), name="cancel"),
    path("conges/en-attente/", views.PendingLeavesView.as_view(), name="pending"),
    path("conges/calendrier/", views.LeaveCalendarView.as_view(), name="calendar"),
    path("conges/historique/", views.LeaveHistoryView.as_view(), name="history"),
    path("conges/historique/export/<str:fmt>/", views.LeaveHistoryExportView.as_view(), name="history_export"),
    path("conges/<uuid:pk>/traiter/", views.ReviewLeaveView.as_view(), name="review"),
]
