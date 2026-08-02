from django.urls import path

from . import views

app_name = "departments"

urlpatterns = [
    path("departements/", views.DepartmentListView.as_view(), name="list"),
    path("departements/nouveau/", views.DepartmentCreateView.as_view(), name="create"),
    path("departements/<uuid:pk>/modifier/", views.DepartmentUpdateView.as_view(), name="update"),
    path("postes/", views.PositionListView.as_view(), name="position_list"),
    path("postes/nouveau/", views.PositionCreateView.as_view(), name="position_create"),
    path("postes/<uuid:pk>/modifier/", views.PositionUpdateView.as_view(), name="position_update"),
]
