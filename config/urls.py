from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Bascule de langue pour les visiteurs anonymes (page de connexion...) —
    # CDC §24.2. Vue standard Django (django.views.i18n.set_language),
    # POST-only, stocke le choix en session. Les utilisateurs authentifiés
    # ont leur propre préférence (User.language, cf. UserLanguageMiddleware)
    # qui prévaut de toute façon dès la connexion suivante.
    path("i18n/", include("django.conf.urls.i18n")),
    path("accounts/", include("apps.accounts.urls")),
    path("", include("apps.attendance.urls")),
    path("", include("apps.leaves.urls")),
    path("", include("apps.absences.urls")),
    path("", include("apps.agencies.urls")),
    path("", include("apps.departments.urls")),
    path("", include("apps.schedules.urls")),
    path("", include("apps.employees.urls")),
    path("", include("apps.superadmin.urls")),
    path("", include("apps.backups.urls")),
    path("", include("apps.tenants.urls")),
    path("", include("apps.ai.urls")),
    path("", include("apps.announcements.urls")),
    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
