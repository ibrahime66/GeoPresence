from django.urls import path

from . import views

app_name = "attendance"

urlpatterns = [
    path("pointage/", views.ClockPageView.as_view(), name="clock_page"),
    path("pointage/historique/", views.AttendanceHistoryView.as_view(), name="history"),
    path("pointage/export/<str:fmt>/", views.AttendanceExportView.as_view(), name="export"),
    path("api/pointage/", views.ClockView.as_view(), name="clock_api"),
    path("q/<uuid:agency_id>/<str:token>/", views.QREntryView.as_view(), name="qr_entry"),
]
