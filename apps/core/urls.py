from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("robots.txt", views.RobotsTxtView.as_view(), name="robots_txt"),
    path("google11cfdbf23fe92380.html", views.GoogleSiteVerificationView.as_view(), name="google_site_verification"),
    path("sitemap.xml", views.SitemapXmlView.as_view(), name="sitemap_xml"),
    path("", views.HomeView.as_view(), name="home"),
    path("secteurs/<slug:slug>/", views.SectorLandingView.as_view(), name="sector"),
    path("confidentialite/", views.PrivacyView.as_view(), name="privacy"),
    path("conditions-utilisation/", views.TermsView.as_view(), name="terms"),
    path("faq/", views.FaqView.as_view(), name="faq"),
    path("dashboard/", views.DashboardPlaceholderView.as_view(), name="dashboard"),
    path("menu/organisation/", views.OrganisationMenuView.as_view(), name="menu_organisation"),
    path("menu/validations/", views.ValidationsMenuView.as_view(), name="menu_validations"),
    path("menu/mon-espace/", views.WorkspaceMenuView.as_view(), name="menu_workspace"),
    path("service-worker.js", views.ServiceWorkerView.as_view(), name="service_worker"),
]
