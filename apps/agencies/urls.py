from django.urls import path

from . import views

app_name = "agencies"

urlpatterns = [
    path("agences/", views.AgencyListView.as_view(), name="list"),
    path("agences/nouvelle/", views.AgencyCreateView.as_view(), name="create"),
    path("agences/<uuid:pk>/modifier/", views.AgencyUpdateView.as_view(), name="update"),
    path("agences/<uuid:pk>/basculer/", views.AgencyToggleActiveView.as_view(), name="toggle_active"),
]
