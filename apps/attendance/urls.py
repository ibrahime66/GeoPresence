from django.urls import path

from . import views

app_name = "attendance"

urlpatterns = [
    path("pointage/", views.ClockPageView.as_view(), name="clock_page"),
    path("api/pointage/", views.ClockView.as_view(), name="clock_api"),
]
