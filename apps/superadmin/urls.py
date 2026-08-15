from django.urls import path

from . import views

app_name = "superadmin"

urlpatterns = [
    path("superadmin/", views.SuperAdminDashboardView.as_view(), name="dashboard"),
    path("superadmin/organisations/", views.OrganizationListView.as_view(), name="organization_list"),
    path("superadmin/organisations/nouvelle/", views.OrganizationCreateView.as_view(), name="organization_create"),
    path("superadmin/organisations/<uuid:pk>/modifier/", views.OrganizationUpdateView.as_view(), name="organization_update"),
    path("superadmin/organisations/<uuid:pk>/suspendre/", views.OrganizationSuspendView.as_view(), name="organization_suspend"),
    path("superadmin/organisations/<uuid:pk>/reactiver/", views.OrganizationReactivateView.as_view(), name="organization_reactivate"),
    path("superadmin/organisations/<uuid:pk>/supprimer/", views.OrganizationDeleteView.as_view(), name="organization_delete"),
    path("superadmin/audit/", views.AuditLogListView.as_view(), name="audit_log_list"),
    path("superadmin/audit/export/<str:fmt>/", views.AuditLogExportView.as_view(), name="audit_log_export"),
    path("superadmin/plus/", views.MoreMenuView.as_view(), name="more_menu"),
]
