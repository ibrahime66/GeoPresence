from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = []

# Audit sécurité §2 : l'admin Django (`/admin/login/`) court-circuite tout le
# durcissement anti-brute-force de LoginView (verrouillage progressif,
# rate-limit, CAPTCHA) — ModelBackend ne vérifie que `is_active`. Toute
# l'exploitation d'une organisation passe par l'app `superadmin`, jamais par
# l'admin Django : on ne l'expose donc qu'en développement. En cas de besoin
# ponctuel en prod, passer par `manage.py shell` ou réactiver derrière une
# restriction d'IP Nginx.
if settings.DEBUG:
    urlpatterns += [path("admin/", admin.site.urls)]

urlpatterns += [
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
