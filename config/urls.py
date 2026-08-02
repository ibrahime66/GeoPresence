from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("", include("apps.attendance.urls")),
    path("", include("apps.leaves.urls")),
    path("", include("apps.absences.urls")),
    path("", include("apps.agencies.urls")),
    path("", include("apps.departments.urls")),
    path("", include("apps.schedules.urls")),
    path("", include("apps.employees.urls")),
    path("", include("apps.superadmin.urls")),
    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
