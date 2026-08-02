from django.urls import path

from . import views

app_name = "employees"

urlpatterns = [
    path("employes/", views.EmployeeListView.as_view(), name="list"),
    path("employes/nouveau/", views.EmployeeCreateView.as_view(), name="create"),
    path("employes/<uuid:pk>/modifier/", views.EmployeeUpdateView.as_view(), name="update"),
]
