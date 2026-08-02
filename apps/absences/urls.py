from django.urls import path

from . import views

app_name = "absences"

urlpatterns = [
    path("absences/", views.MyAbsencesView.as_view(), name="my_absences"),
    path("absences/soumettre/", views.SubmitJustificationView.as_view(), name="submit"),
    path("absences/en-attente/", views.PendingAbsencesView.as_view(), name="pending"),
    path("absences/<uuid:pk>/traiter/", views.ReviewAbsenceView.as_view(), name="review"),
]
