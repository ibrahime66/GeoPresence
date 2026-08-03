from django.urls import path

from . import views

app_name = "employees"

urlpatterns = [
    path("employes/", views.EmployeeListView.as_view(), name="list"),
    path("employes/nouveau/", views.EmployeeCreateView.as_view(), name="create"),
    path("employes/<uuid:pk>/modifier/", views.EmployeeUpdateView.as_view(), name="update"),
    path("employes/<uuid:pk>/statut/<str:action>/", views.EmployeeStatusChangeView.as_view(), name="status_change"),
    path("employes/<uuid:pk>/sessions/revoquer/", views.EmployeeRevokeSessionsView.as_view(), name="revoke_sessions"),
    path("employes/export/<str:fmt>/", views.EmployeeExportView.as_view(), name="export"),
    path("employes/importer/", views.EmployeeImportView.as_view(), name="import"),
    path("employes/importer/modele/", views.EmployeeImportTemplateView.as_view(), name="import_template"),
    path("employes/importer/confirmer/", views.EmployeeImportConfirmView.as_view(), name="import_confirm"),
]
