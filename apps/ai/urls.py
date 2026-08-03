from django.urls import path

from . import views

app_name = "ai"

urlpatterns = [
    path("ia/", views.AIChatView.as_view(), name="chat"),
    path("ia/<uuid:pk>/", views.AIChatView.as_view(), name="chat_detail"),
]
