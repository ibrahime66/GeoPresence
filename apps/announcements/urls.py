from django.urls import path

from . import views

app_name = "announcements"

urlpatterns = [
    path("annonces/", views.AnnouncementListView.as_view(), name="list"),
    path("annonces/nouvelle/", views.AnnouncementCreateView.as_view(), name="create"),
    path("annonces/<uuid:pk>/modifier/", views.AnnouncementUpdateView.as_view(), name="update"),
    path("annonces/<uuid:pk>/supprimer/", views.AnnouncementDeleteView.as_view(), name="delete"),
]
