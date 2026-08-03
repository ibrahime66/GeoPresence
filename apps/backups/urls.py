from django.urls import path

from . import views

app_name = "backups"

urlpatterns = [
    path("superadmin/sauvegardes/", views.BackupListView.as_view(), name="list"),
    path("superadmin/sauvegardes/nouvelle/", views.BackupCreateView.as_view(), name="create"),
    path("superadmin/sauvegardes/<uuid:pk>/telecharger/", views.BackupDownloadView.as_view(), name="download"),
]
