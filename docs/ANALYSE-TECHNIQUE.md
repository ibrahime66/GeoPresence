ANALYSE TECHNIQUE
Plateforme SaaS Intelligente de Gestion de Présence

Architecture complète • Python/Django • MySQL 8 • Docker • PWA

Champ	Valeur
Référence	AT-PRESENCE-SAAS-V1.0
Backend	Python 3.11+ / Django 4.2 LTS / Gunicorn
Frontend	Django Templates / Bootstrap 5.3 / JavaScript ES6+
Base de données	MySQL 8.0 InnoDB — utf8mb4
Cache / Queue	Redis 7 / Celery 5
Serveur	Nginx 1.25 / Gunicorn WSGI
Conteneurisation	Docker 24+ / Docker Compose v2
OS	Ubuntu 22.04 LTS
Audience	Architectes, Dev Backend/Frontend, DevOps, DBA, QA, Pentesters

TABLE DES MATIÈRES

Chapitre	Contenu
Chapitre 1	Présentation de l'Architecture — Générale, Physique, Réseau, SaaS, Multi-Tenant
Chapitre 2	Architecture Django — Organisation, Settings, Models, Views, Middleware, Signals
Chapitre 3	Découpage du Projet — 20 applications Django détaillées
Chapitre 4	Architecture Multi-Tenant — Isolation, TenantMiddleware, TenantManager, Sécurité
Chapitre 5	Architecture Base de Données — Schéma, Index, Contraintes, Partitionnement
Chapitre 6	Architecture Docker — Dockerfile, Compose dev/prod, Nginx, Entrypoint
Chapitre 7	Architecture Sécurité — Argon2, RBAC, CSRF, XSS, Rate limiting, OWASP
Chapitre 8	Architecture PWA — Manifest, Service Worker, IndexedDB, Push, Background Sync
Chapitre 9	Architecture Géolocalisation — GPS, Haversine, Geofencing, Mock Detection
Chapitre 10	Architecture Caméra — getUserMedia, Canvas, Pillow, Validation serveur
Chapitre 11	Architecture IA — Provider Pattern, 7 fournisseurs, Isolation tenant, Quota
Chapitre 12	Architecture Notifications — Email, Push, In-app, Celery queues, Templates
Chapitre 13	Architecture Rapports — ReportLab PDF, openpyxl Excel, CSV, Async, Sécurisé
Chapitre 14	Architecture Fichiers — Organisation, X-Accel-Redirect, Rétention, Suppression
Chapitre 15	Performances — Cache Redis, ORM, Index, Pagination, Scalabilité
Chapitre 16	Journalisation — Logs JSON, Sentry, Rotation, Archivage
Chapitre 17	Sauvegardes — Script, Chiffrement AES-256, Rotation, Restauration
Chapitre 18	Déploiement — CI/CD GitHub Actions, Production settings, Nginx
Chapitre 19	Supervision — Health checks, Métriques, Alertes critiques
Chapitre 20	Stratégie de Tests — Unitaires, Intégration, Sécurité, Charge, Standards

CHAPITRE 1 — PRÉSENTATION DE L'ARCHITECTURE

1.1 Architecture générale en couches
Couche	Description
Couche Présentation	Interface responsive Bootstrap 5 + Django Templates + JavaScript ES6+. PWA installable. Rendu SSR pour performance et SEO.
Couche Application	Django 4.2 LTS : logique métier, routing HTTP, auth, permissions, formulaires. 20 apps Django modulaires.
Couche Services	Celery 5 + Redis 7 : tâches asynchrones (rapports, notifications, synchro offline, IA). Scalable horizontalement.
Couche Données	MySQL 8.0 InnoDB (données). Redis (cache + sessions). Stockage fichier local (extensible S3 en V2).
Couche Infrastructure	Docker + Docker Compose. Nginx reverse proxy. Ubuntu 22.04 LTS.
1.2 Justification des choix technologiques
1.2.1 Pourquoi Django 4.2 LTS ?
    • Batteries included : ORM, auth, admin, sessions, CSRF, migrations, templates, i18n natifs.
    • Sécurité by default : protection CSRF, XSS, clickjacking activée dès l'installation.
    • ORM puissant : abstraction MySQL complète, prévention injection SQL automatique.
    • LTS jusqu'en avril 2026 : stabilité garantie pour la durée du projet.
    • Alternatives rejetées : FastAPI (pas de templates/admin natifs), Flask (trop léger, trop de choix manuels).
1.2.2 Pourquoi MySQL 8.0 ?
    • InnoDB : transactions ACID complètes, FK, row-level locking, buffer pool configurable.
    • Fonctionnalités v8 : CTEs, window functions, JSON natif, SKIP LOCKED pour queues, atomic DDL.
    • Contrainte CDC : MySQL imposé. PostgreSQL aurait été excellent (UUID natif, JSONB) mais hors scope.
    • Version 8.0 obligatoire : MySQL 5.7 EOL 2023. CTEs et partitionnement avancé requis.
1.2.3 Pourquoi Django Templates plutôt que React/Vue ?
    • Stack unique : pas de CORS, pas d'API REST à sécuriser séparément, surface d'attaque réduite.
    • Rendu SSR : premier affichage instantané, SEO natif, pas de JavaScript requis pour charger les données.
    • Bootstrap 5 suffit : tableaux de bord, formulaires, graphiques Chart.js couverts sans framework lourd.
    • Migration future facilitée : DRF ajouté progressivement si SPA nécessaire en V2.
1.3 Architecture physique — Conteneurs Docker
Conteneur	Rôle
Nginx 1.25-alpine	Reverse proxy HTTPS. Termination TLS. Fichiers statiques. Rate limiting. Headers sécurité.
Django (Gunicorn)	Application Python. 4 workers sync. Timeout 120s. Max 1000 req/worker avant restart.
Celery Worker	Même image Django. 5 queues spécialisées. 4 concurrents. Tâches async.
Celery Beat	Scheduler tâches périodiques (absences auto, rapports, sauvegardes, nettoyage).
MySQL 8.0	Données persistantes. Volume dédié. my.cnf optimisé. innodb_buffer_pool_size=2G.
Redis 7-alpine	Cache applicatif. Sessions. Broker Celery. Password protégé. AOF persistence.
phpMyAdmin	Développement uniquement (profil Docker). Jamais déployé en production.
1.4 Architecture réseau
Zone	Configuration
Internet → Nginx	Ports 80 (redirect HTTPS) et 443 exposés uniquement. Nginx = seul point d'entrée.
Réseau app_network	Nginx ↔ Django (port 8000). Django ↔ MySQL (3306). Django ↔ Redis (6379). Celery ↔ Redis.
Réseau admin_network	phpMyAdmin ↔ MySQL (dev uniquement). Non déployé en production.
Firewall	UFW : ports 22 (SSH), 80, 443 autorisés. Tout le reste bloqué. Fail2ban sur SSH et login.
TLS	TLS 1.2 min, 1.3 recommandé. HSTS preload. Certificats Let's Encrypt auto-renouvelés.
1.5 Stratégie Multi-Tenant retenue
Option retenue : Shared Database / Shared Schema + colonne tenant_id sur toutes les tables métier. Isolation assurée par TenantMiddleware + TenantManager Django. Coût marginal par nouveau tenant quasi-nul.

Stratégie	Évaluation
Option A — Base dédiée/tenant	Isolation parfaite. REJETÉ : N bases = infrastructure N× plus chère. Migrations complexes. Ingérable > 50 tenants.
Option B — Schéma/tenant (MySQL)	MySQL ne gère pas les schémas comme PostgreSQL. Équivalent à N bases. REJETÉ.
Option C — Préfixe tables	tenant_1_pointages... REJETÉ : explose le nombre de tables. Migrations impossibles à gérer globalement.
Option D retenue	Shared Schema + tenant_id. Simple. Scalable. Maintenable. Isolation via middleware Django.

CHAPITRE 2 — ARCHITECTURE DJANGO

2.1 Structure du projet
presence_saas/
├── config/                    # Configuration modulaire
│   ├── settings/
│   │   ├── base.py            # Settings communs
│   │   ├── development.py     # DEBUG=True, phpMyAdmin, MailHog
│   │   ├── staging.py         # Proche production
│   │   └── production.py      # Optimisé, sécurisé, Sentry
│   ├── urls.py                # URLs racines
│   └── wsgi.py                # Point d'entrée Gunicorn
├── apps/                      # 20 applications Django
│   ├── core/                  # Modèles abstraits, mixins, utils
│   ├── accounts/              # Auth, utilisateurs, sessions
│   ├── tenants/               # Organisations + Middleware
│   ├── agencies/              # Agences + geofencing
│   ├── departments/           # Départements et postes
│   ├── employees/             # Profils employés
│   ├── schedules/             # Horaires de travail
│   ├── attendance/            # Pointages (cœur)
│   ├── absences/              # Absences + justificatifs
│   ├── leaves/                # Congés + soldes
│   ├── notifications/         # Notifications multi-canal
│   ├── reports/               # Rapports PDF/Excel/CSV
│   ├── documents/             # Gestion documentaire
│   ├── dashboard/             # Tableaux de bord
│   ├── audit/                 # Journal d'audit
│   ├── ai/                    # Module IA multi-fournisseurs
│   ├── announcements/         # Annonces internes
│   ├── api/                   # API REST (DRF) pour PWA
│   ├── security/              # Rate limiting, CAPTCHA
│   └── superadmin/            # Interface Super Administrateur
├── templates/                 # Templates globaux + emails HTML
├── static/                    # CSS, JS, PWA manifest, SW
├── locale/                    # i18n (fr, en, ar)
├── requirements/              # base.txt, development.txt, production.txt
├── docker/                    # Dockerfile, nginx.conf, my.cnf
├── scripts/                   # backup.sh, restore.sh, entrypoint.sh
├── .env.example
├── docker-compose.yml         # Dev
├── docker-compose.prod.yml    # Production
└── Makefile

2.2 Settings base.py — Points clés
# config/settings/base.py
import environ
env = environ.Env()
SECRET_KEY = env('DJANGO_SECRET_KEY')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.tenants.middleware.TenantMiddleware',      # Identification tenant
    'apps.security.middleware.SecurityHeadersMiddleware',
    'apps.audit.middleware.AuditMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = {'default': {
    'ENGINE': 'django.db.backends.mysql',
    'OPTIONS': {'charset': 'utf8mb4',
                'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO'},
    'CONN_MAX_AGE': 60,
}}

CACHES = {'default': {
    'BACKEND': 'django.core.cache.backends.redis.RedisCache',
    'LOCATION': env('REDIS_URL', default='redis://redis:6379/0'),
    'KEY_PREFIX': 'presence', 'TIMEOUT': 300,
}}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_AGE = 28800  # 8 heures
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Strict'

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://redis:6379/1')
CELERY_TASK_TIME_LIMIT = 3600  # 1h max par tâche
CELERY_ACKS_LATE = True

AUTH_USER_MODEL = 'accounts.User'
PASSWORD_HASHERS = ['django.contrib.auth.hashers.Argon2PasswordHasher']

LANGUAGES = [('fr','Français'),('en','English'),('ar','العربية')]
USE_TZ = True
TIME_ZONE = 'UTC'

2.3 Middleware — Rôles
Middleware	Rôle
TenantMiddleware (custom)	Identifie le tenant depuis la session/URL. Configure request.tenant. Vérifie statut. Détecte cross-tenant. Injecte dans thread local.
SecurityHeadersMiddleware (custom)	Ajoute CSP, Referrer-Policy, Permissions-Policy, COEP, CORP sur chaque réponse.
AuditMiddleware (custom)	Journalise les requêtes sensibles (POST/PUT/DELETE) dans le journal d'audit.
CsrfViewMiddleware	Token CSRF sur tous les formulaires. Vérifié sur POST/PUT/DELETE/PATCH.
XFrameOptionsMiddleware	X-Frame-Options: DENY sur toutes les réponses.
2.4 Modèle de base abstrait TenantModel
# apps/core/models.py
import uuid
from django.db import models
from apps.tenants.managers import TenantManager

class TenantModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Organization', on_delete=models.CASCADE,
                               related_name='+', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TenantManager()  # Filtre automatique par tenant

    class Meta:
        abstract = True
        indexes = [models.Index(fields=['tenant','created_at'],
                                   name='%(class)s_tenant_created_idx')]

2.5 Class-Based Views avec mixins de sécurité
# apps/core/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class TenantRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request, 'tenant') or not request.tenant:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class RoleRequiredMixin:
    required_roles = []
    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in self.required_roles:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin(LoginRequiredMixin, TenantRequiredMixin, RoleRequiredMixin):
    required_roles = ['ADMIN']

class ManagerRequiredMixin(LoginRequiredMixin, TenantRequiredMixin, RoleRequiredMixin):
    required_roles = ['ADMIN', 'SUPERVISEUR', 'MANAGER']

# Utilisation
class EmployeeListView(ManagerRequiredMixin, ListView):
    model = Employee  # TenantManager filtre automatiquement
    paginate_by = 25
    def get_queryset(self):
        return super().get_queryset().select_related('department','position','agency')

CHAPITRE 3 — DÉCOUPAGE DU PROJET EN APPLICATIONS DJANGO

Le projet est découpé en 20 applications Django modulaires, chacune responsable d'un domaine fonctionnel précis.
Application	Description
core	Fondations partagées : modèles abstraits (TenantModel, TimeStampedModel), mixins Views, utils, validators, context processors, templatetags, exceptions métier.
accounts	Authentification complète : User custom (UUID, role, tenant, failed_attempts, locked_until), sessions sécurisées, PasswordHistory, UserSession, connexion/déconnexion sécurisée, réinitialisation MDP, CAPTCHA.
tenants	Gestion des organisations (tenants) : Organization, OrganizationSettings, Subscription (V2). TenantMiddleware. TenantManager. Cycle de vie : Active → Suspendue → Expirée → Supprimée.
agencies	Sites géographiques : Agency (coordonnées GPS, rayon geofencing, zones supplémentaires JSON), AgencySchedule. Carte Leaflet.js intégrée pour saisie GPS. Test de zone en interface admin.
departments	Structure organisationnelle : Department, Position. Relations avec employees.
employees	Profils employés : Employee (toutes infos personnelles et professionnelles, id_number chiffré AES-256, photo sécurisée, solde congés JSON). EmployeeScheduleHistory. Import CSV/Excel.
schedules	Horaires de travail : Schedule (FIXED/TEAM/CUSTOM/TEACHER), config JSONField. ShiftRotation. TeacherTimetable. TeacherSlot. EmployeeScheduleAssignment. Logique get_effective_schedule().
attendance	Pointages (cœur) : Attendance (GPS, photo, statut, mode ONLINE/OFFLINE, is_gps_mocked). AttendanceService. Vue ClockView. API endpoint DRF. Tâche Celery détection absences.
absences	Absences : Absence (NON_JUSTIFIEE/EN_ATTENTE/JUSTIFIEE). AbsenceJustification. Workflow soumission → validation. Tâche auto detect_absences().
leaves	Congés : LeaveType, Leave (EN_ATTENTE/APPROUVE/REJETE/ANNULE), LeaveBalance. Workflow complet. Calcul jours ouvrables. Gestion jours fériés.
notifications	Notifications multi-canal : Notification, PushSubscription. Tasks Celery : send_email, send_push, send_sms. Templates HTML par tenant. Préférences utilisateur.
reports	Rapports : ReportJob. Générateurs PDF (ReportLab), Excel (openpyxl), CSV. Tâche Celery async. Token URL sécurisé. Nettoyage auto 7 jours.
documents	Gestion documentaire : Document (contrats, diplômes, justificatifs). Vue sécurisée X-Accel-Redirect. Validation MIME. Politique rétention configurable.
dashboard	Tableaux de bord : vues par rôle (Super Admin, Admin, Manager, Employé). KPI temps réel. Graphiques Chart.js. Carte Leaflet.js agences.
audit	Journal d'audit inaltérable : AuditLog (INSERT ONLY). Triggers MySQL BEFORE UPDATE/DELETE. Décorateur @audit_action. AuditMiddleware. Consultation filtrée par rôle.
ai	Module IA : AIProvider, OrganizationAIConfig (clé API chiffrée), AIConversation, AIMessage. Provider Pattern : OpenAI, Anthropic, Mistral, Gemini, Grok, DeepSeek, Ollama. Isolation tenant garantie.
announcements	Annonces internes : Announcement, AnnouncementTarget. Ciblage par agence/département. Programmation publication/expiration. Lien vers notifications push.
api	API REST DRF pour PWA offline : endpoints clock, sync, notifications. SessionAuthentication + TokenAuthentication. Rate limiting DRF. Permission IsTenantMember.
security	Sécurité applicative : rate limiting (django-ratelimit), CAPTCHA (hCaptcha), IP blacklist, alerts. Middleware SecurityHeadersMiddleware (CSP, HSTS...).
superadmin	Interface Super Administrateur : CRUD organisations, statistiques globales, journal audit global, gestion fournisseurs IA, sauvegardes manuelles, monitoring.

CHAPITRE 4 — ARCHITECTURE MULTI-TENANT

4.1 TenantManager — Filtre automatique QuerySet
# apps/tenants/managers.py
import threading
from django.db import models

_thread_locals = threading.local()

def get_current_tenant(): return getattr(_thread_locals, 'tenant', None)
def set_current_tenant(t): _thread_locals.tenant = t
def clear_current_tenant(): _thread_locals.tenant = None

class TenantManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        tenant = get_current_tenant()
        return qs.filter(tenant=tenant) if tenant else qs

    def all_tenants(self):  # Réservé Super Admin
        return super().get_queryset()

4.2 TenantMiddleware — Implémentation sécurisée
# apps/tenants/middleware.py
import logging
from django.http import Http404, JsonResponse
from django.core.exceptions import PermissionDenied
from .models import Organization
from .managers import set_current_tenant, clear_current_tenant

logger = logging.getLogger('apps.security')

class TenantMiddleware:
    EXCLUDED = ('/superadmin/','/static/','/media/','/health/','/favicon.ico')
    PUBLIC   = ('/login/','/logout/','/password-reset/')

    def __init__(self, get_response): self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(self.EXCLUDED):
            return self.get_response(request)

        tenant = self._resolve(request)

        if tenant:
            if tenant.status == Organization.Status.SUSPENDED:
                raise PermissionDenied('Organisation suspendue.')
            if tenant.status == Organization.Status.DELETED:
                raise Http404

            # Vérification cross-tenant
            if request.user.is_authenticated and not request.user.is_superuser:
                if str(request.user.tenant_id) != str(tenant.id):
                    logger.error(f'CROSS-TENANT ATTEMPT user={request.user.id} target={tenant.id}')
                    from apps.security.alerts import send_security_alert
                    send_security_alert.delay('CROSS_TENANT', {
                        'user_id': str(request.user.id), 'target': str(tenant.id),
                        'path': request.path})
                    raise PermissionDenied('Accès refusé.')

            request.tenant = tenant
            set_current_tenant(tenant)

        try:
            return self.get_response(request)
        finally:
            clear_current_tenant()

    def _resolve(self, request):
        if request.user.is_authenticated and hasattr(request.user,'tenant'):
            return request.user.tenant
        slug = getattr(request.resolver_match,'kwargs',{}).get('tenant_slug')
        if slug:
            return Organization.objects.get(slug=slug, status=Organization.Status.ACTIVE)
        return None

4.3 Défense en profondeur multi-tenant
Niveau	Mesure
Niveau 1 — Middleware	Vérifie appartenance tenant sur chaque requête. Cross-tenant → 403 + alerte.
Niveau 2 — Manager	TenantManager filtre automatiquement tout QuerySet par tenant actif.
Niveau 3 — DRF Permissions	IsTenantMember vérifie sur chaque endpoint API l'appartenance au tenant.
Niveau 4 — Tests	Suite de tests vérifiant systématiquement qu'un user du tenant A ne voit pas les données du tenant B.
Niveau 5 — Audit	Toutes les tentatives cross-tenant sont journalisées et alertent le Super Admin.
4.4 Cache tenant-aware
# Clés de cache préfixées par tenant — isolation garantie
def tenant_cache_key(tenant_id, key):
    return f'tenant:{tenant_id}:{key}'

# Invalidation ciblée d'un tenant
def invalidate_tenant_cache(tenant_id):
    from django_redis import get_redis_connection
    redis = get_redis_connection('default')
    keys = redis.keys(f'presence:1:tenant:{tenant_id}:*')
    if keys: redis.delete(*keys)

CHAPITRE 5 — ARCHITECTURE BASE DE DONNÉES

5.1 Configuration MySQL 8.0 optimisée
# my.cnf
[mysqld]
character-set-server    = utf8mb4
collation-server        = utf8mb4_unicode_ci
innodb_buffer_pool_size = 2G          # 70% RAM disponible
innodb_buffer_pool_instances = 4
innodb_log_file_size    = 512M
innodb_flush_log_at_trx_commit = 1   # Durabilité ACID
innodb_file_per_table   = 1
max_connections         = 200
slow_query_log          = 1
slow_query_log_file     = /var/log/mysql/slow.log
long_query_time         = 1
log_bin                 = mysql-bin
binlog_format           = ROW
expire_logs_days        = 7
default_time_zone       = '+00:00'
sql_mode = STRICT_TRANS_TABLES,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO

5.2 Tables principales — Schéma
-- Table organizations
CREATE TABLE organizations (
    id              CHAR(36) PRIMARY KEY,
    slug            VARCHAR(100) NOT NULL UNIQUE,
    name            VARCHAR(255) NOT NULL,
    org_type        ENUM('COMPANY','SCHOOL','UNIVERSITY','HOSPITAL','RESTAURANT',
                         'PHARMACY','NGO','ADMIN','ASSOCIATION','OTHER') NOT NULL,
    timezone        VARCHAR(50)  NOT NULL DEFAULT 'UTC',
    language        ENUM('fr','en','ar') NOT NULL DEFAULT 'fr',
    status          ENUM('ACTIVE','SUSPENDED','EXPIRED','DELETED') NOT NULL DEFAULT 'ACTIVE',
    settings        JSON NOT NULL DEFAULT ('{}'),
    created_at      DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table attendances (pointages) — cœur du système
CREATE TABLE attendances (
    id              CHAR(36) PRIMARY KEY,
    tenant_id       CHAR(36) NOT NULL,
    employee_id     CHAR(36) NOT NULL,
    agency_id       CHAR(36) NOT NULL,
    clock_type      ENUM('ARRIVEE','DEPART') NOT NULL,
    clock_date      DATE NOT NULL,
    server_time     DATETIME(6) NOT NULL,
    client_time     DATETIME(6),
    latitude        DECIMAL(10,7) NOT NULL,
    longitude       DECIMAL(10,7) NOT NULL,
    gps_accuracy    DECIMAL(8,2),
    photo_path      VARCHAR(500) NOT NULL,
    ip_address      VARCHAR(45),
    delay_minutes   SMALLINT,
    early_leave_minutes SMALLINT,
    overtime_minutes SMALLINT,
    status          ENUM('ON_TIME','LATE','EARLY_LEAVE','OVERTIME',
                         'OUT_OF_SCHEDULE','PENDING_VALIDATION','MANUAL') NOT NULL,
    mode            ENUM('ONLINE','OFFLINE') NOT NULL DEFAULT 'ONLINE',
    is_gps_mocked   TINYINT(1) NOT NULL DEFAULT 0,
    created_at      DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    FOREIGN KEY (tenant_id)   REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (agency_id)   REFERENCES agencies(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY RANGE(YEAR(clock_date)) (
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p2026 VALUES LESS THAN (2027),
    PARTITION pfuture VALUES LESS THAN MAXVALUE
);

-- Index essentiels
CREATE INDEX idx_att_tenant_date     ON attendances(tenant_id, clock_date);
CREATE INDEX idx_att_employee_date   ON attendances(tenant_id, employee_id, clock_date);
CREATE INDEX idx_att_agency_date     ON attendances(tenant_id, agency_id, clock_date);
CREATE INDEX idx_att_status          ON attendances(tenant_id, status, clock_date);

-- Table audit_logs — INALTÉRABLE via triggers
CREATE TABLE audit_logs (
    id           CHAR(36) PRIMARY KEY,
    tenant_id    CHAR(36),
    user_email   VARCHAR(254) NOT NULL,
    user_role    VARCHAR(20)  NOT NULL,
    category     VARCHAR(50)  NOT NULL,
    action       VARCHAR(100) NOT NULL,
    object_type  VARCHAR(100),
    object_id    CHAR(36),
    values_before JSON,
    values_after  JSON,
    ip_address   VARCHAR(45),
    result       ENUM('SUCCESS','FAILURE','WARNING') NOT NULL DEFAULT 'SUCCESS',
    timestamp    DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB;

-- Triggers immutabilité
DELIMITER //
CREATE TRIGGER prevent_audit_update BEFORE UPDATE ON audit_logs
FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Audit logs are immutable';
END //
CREATE TRIGGER prevent_audit_delete BEFORE DELETE ON audit_logs
FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Audit logs cannot be deleted';
END //
DELIMITER ;

5.3 Stratégie d'indexation
Type	Implémentation
Index PK UUID	CHAR(36) sur toutes les tables. Générés côté Python (uuid4) pour éviter le bottleneck MySQL.
Index composés critiques	(tenant_id, clock_date), (tenant_id, employee_id, clock_date), (tenant_id, status, clock_date) sur attendances.
Index FULLTEXT	employees(first_name, last_name, email) pour recherche rapide.
audit_logs(description) pour recherche dans les logs.
Partitionnement	attendances et audit_logs partitionnés RANGE par YEAR(date). Requêtes historiques 10× plus rapides.
Monitoring	sys.schema_unused_indexes, sys.schema_redundant_indexes. Revue mensuelle des plans EXPLAIN.
5.4 Transactions atomiques
# Exemple : création pointage avec verrou anti-doublon
from django.db import transaction

def create_attendance_atomic(employee, data):
    with transaction.atomic():
        # Verrou pessimiste pour éviter les doublons simultanés
        emp = Employee.objects.select_for_update(nowait=True).get(id=employee.id)

        if Attendance.objects.filter(
            employee=emp, clock_date=data['date'], clock_type=data['type']
        ).exists():
            raise DuplicateClockingError('Pointage déjà enregistré.')

        return Attendance.objects.create(**data)

CHAPITRE 6 — ARCHITECTURE DOCKER

6.1 Dockerfile Django
FROM python:3.11-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc default-libmysqlclient-dev pkg-config curl netcat-traditional gettext \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -r presence && useradd -r -g presence presence
WORKDIR /app

COPY requirements/production.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

COPY --chown=presence:presence . .
RUN mkdir -p /app/media /app/staticfiles /var/log/presence \
    && chown -R presence:presence /app /var/log/presence

USER presence
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn","config.wsgi:application","--bind","0.0.0.0:8000",
     "--workers","4","--timeout","120","--max-requests","1000"]

6.2 entrypoint.sh
#!/bin/bash
set -e
# Attendre MySQL
while ! nc -z $MYSQL_HOST ${MYSQL_PORT:-3306}; do sleep 2; done
# Attendre Redis
while ! nc -z redis 6379; do sleep 2; done
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py compilemessages
python manage.py ensure_superuser
exec "$@"

6.3 docker-compose.yml (développement)
version: '3.9'
services:
  web:
    build: { context: ., dockerfile: docker/django/Dockerfile }
    command: python manage.py runserver 0.0.0.0:8000
    volumes: [.:/app, media_files:/app/media]
    ports: ['8000:8000']
    env_file: [.env]
    environment: [DJANGO_SETTINGS_MODULE=config.settings.development]
    depends_on: { mysql: {condition: service_healthy}, redis: {condition: service_healthy} }
    networks: [app_network]

  celery:
    build: { context: ., dockerfile: docker/django/Dockerfile }
    command: celery -A config worker -l info -Q default,notifications,reports,ai,sync --concurrency=4
    volumes: [.:/app, media_files:/app/media]
    env_file: [.env]
    depends_on: [web, redis]
    networks: [app_network]

  celery-beat:
    command: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    networks: [app_network]

  mysql:
    image: mysql:8.0
    volumes: [mysql_data:/var/lib/mysql, ./docker/mysql/my.cnf:/etc/mysql/conf.d/my.cnf:ro]
    environment: { MYSQL_ROOT_PASSWORD: '${MYSQL_ROOT_PASSWORD}',
                   MYSQL_DATABASE: '${MYSQL_DATABASE}',
                   MYSQL_USER: '${MYSQL_USER}', MYSQL_PASSWORD: '${MYSQL_PASSWORD}' }
    healthcheck:
      test: ['CMD','mysqladmin','ping','-h','localhost']
      interval: 10s  timeout: 5s  retries: 5
    ports: ['3306:3306']  # Dev only
    networks: [app_network]

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes: [redis_data:/data]
    networks: [app_network]

  phpmyadmin:
    image: phpmyadmin:latest
    environment: { PMA_HOST: mysql }
    ports: ['8080:80']
    profiles: [dev]  # docker compose --profile dev up
    networks: [app_network]

volumes:
  mysql_data: redis_data: media_files: static_files: backups:
networks:
  app_network: { driver: bridge }

6.4 Nginx configuration production
upstream django { server web:8000; keepalive 32; }

server {
    listen 80; server_name mondomaine.com;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://$host$request_uri; }
}

server {
    listen 443 ssl http2; server_name mondomaine.com;
    ssl_certificate     /etc/letsencrypt/live/mondomaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mondomaine.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    add_header Strict-Transport-Security 'max-age=31536000; includeSubDomains; preload' always;
    add_header X-Frame-Options 'DENY' always;
    add_header X-Content-Type-Options 'nosniff' always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net;" always;
    add_header Permissions-Policy 'camera=(self), geolocation=(self), microphone=()' always;
    client_max_body_size 10m;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    location /static/ { alias /var/www/static/; expires 1y; add_header Cache-Control 'public, immutable'; }
    location /protected-media/ { internal; alias /var/www/media/; }
    location /login/ { limit_req zone=login burst=10 nodelay; proxy_pass http://django; }
    location / { proxy_pass http://django; proxy_set_header Host $host; }
}

CHAPITRE 7 — ARCHITECTURE DE SÉCURITÉ

Sécurité par conception — OWASP ASVS Level 2. Défense en profondeur sur 6 niveaux : Réseau, Infrastructure, Application, Données, Utilisateur, Audit.

7.1 Hachage Argon2id
# settings/base.py
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Recommandé OWASP
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Fallback
]
# Paramètres Argon2id : time_cost=2, memory_cost=65536KB, parallelism=2

7.2 Connexion sécurisée avec protection brute force
# apps/accounts/views.py
from django.core.cache import cache
from apps.audit.utils import log_event

class SecureLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        email = request.POST.get('username','').lower().strip()
        ip = self._get_ip(request)

        # Rate limiting par IP
        ip_key = f'login_ip:{ip}'
        if cache.get(ip_key, 0) >= 10:
            return self._fail(request, 'Trop de tentatives.')

        # CAPTCHA après 3 tentatives par email
        user_key = f'login_user:{email}'
        if cache.get(user_key, 0) >= 3:
            if not verify_captcha(request.POST.get('h-captcha-response',''), ip):
                return self._fail(request, 'CAPTCHA invalide.')

        user = authenticate(request, username=email, password=request.POST.get('password',''))

        if user is None:
            cache.set(ip_key, cache.get(ip_key,0)+1, 900)
            cache.set(user_key, cache.get(user_key,0)+1, 900)
            self._increment_failed_attempts(email)
            log_event(action='LOGIN_FAILED', user_email=email, ip=ip, result='FAILURE')
            return self._fail(request, 'Identifiants incorrects.')

        if user.locked_until and user.locked_until > timezone.now():
            return self._fail(request, 'Compte temporairement verrouillé.')

        request.session.cycle_key()  # Anti session fixation
        login(request, user)
        cache.delete(ip_key); cache.delete(user_key)
        log_event(action='LOGIN_SUCCESS', user=user, ip=ip)
        return redirect('dashboard:index' if not user.force_password_change else 'accounts:force-change')

7.3 RBAC — Permissions par rôle
ROLE_PERMISSIONS = {
    'SUPER_ADMIN': {'*'},
    'ADMIN':   {'attendance.view_all','attendance.modify','employee.create',
               'employee.modify','schedule.manage','agency.manage',
               'leave.approve','absence.validate','report.generate',
               'audit.view','ai.use','ai.configure','settings.manage'},
    'SUPERVISEUR': {'attendance.view_department','leave.approve_department',
                    'report.generate_department','ai.use'},
    'MANAGER': {'attendance.view_team','leave.approve_team',
               'absence.validate_team','ai.use'},
    'EMPLOYE': {'attendance.clock','attendance.view_own',
               'leave.request','absence.justify_own','profile.update_own'},
}

7.4 Protections CSRF, XSS, Clickjacking, SQL Injection
Menace	Protection
CSRF	CsrfViewMiddleware global. {% csrf_token %} dans tous les formulaires. Cookie SameSite=Strict. Header X-CSRFToken pour AJAX.
XSS	Échappement auto Django templates. CSP stricte via Nginx. Bibliothèque bleach pour champs HTML riches.
Clickjacking	X-Frame-Options: DENY. CSP frame-ancestors 'none'. XFrameOptionsMiddleware Django.
SQL Injection	ORM Django exclusif. Zéro SQL brut (ou cursor.execute avec params uniquement). Mode SQL strict MySQL. Bandit SAST en CI.
Upload sécurisé	Validation MIME python-magic server-side. Renommage UUID. Stockage hors racine web. Accès via X-Accel-Redirect.
7.5 En-têtes HTTP de sécurité
En-tête	Valeur et rôle
Strict-Transport-Security	max-age=31536000; includeSubDomains; preload — Force HTTPS 1 an.
Content-Security-Policy	default-src 'self'. script-src 'self' + CDN whitelist. frame-ancestors 'none'.
X-Frame-Options	DENY — Empêche l'intégration dans iframe.
X-Content-Type-Options	nosniff — Empêche le MIME sniffing.
Referrer-Policy	strict-origin-when-cross-origin.
Permissions-Policy	camera=(self), geolocation=(self), microphone=() — Restreint les API navigateur.

CHAPITRE 8 — ARCHITECTURE PWA

8.1 manifest.json
// static/pwa/manifest.json
{
  "name": "Présence SaaS",
  "short_name": "Présence",
  "start_url": "/dashboard/?pwa=1",
  "display": "standalone",
  "background_color": "#0D2137",
  "theme_color": "#1565C0",
  "orientation": "portrait-primary",
  "scope": "/",
  "icons": [
    {"src":"/static/images/icons/icon-192.png","sizes":"192x192","type":"image/png","purpose":"any maskable"},
    {"src":"/static/images/icons/icon-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}
  ],
  "shortcuts": [
    {"name":"Pointer mon arrivée","url":"/attendance/clock/?type=IN"},
    {"name":"Pointer mon départ","url":"/attendance/clock/?type=OUT"}
  ]
}

8.2 Service Worker — Stratégies de cache et offline
// static/pwa/service-worker.js
const CACHE = 'presence-v1.0';
const STATIC = ['/','/dashboard/','/attendance/clock/','/static/css/main.css','/offline.html'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(STATIC)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ).then(() => self.clients.claim()));
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (url.pathname.startsWith('/api/v1/attendance/'))
    event.respondWith(networkFirstWithOffline(event.request));
  else if (url.pathname.startsWith('/static/'))
    event.respondWith(caches.match(event.request).then(r => r || fetch(event.request)));
  else if (event.request.destination === 'document')
    event.respondWith(fetch(event.request).catch(() => caches.match('/offline.html')));
});

async function networkFirstWithOffline(request) {
  try { return await fetch(request.clone()); }
  catch {
    if (request.method === 'POST') {
      const body = await request.clone().json();
      await storeOfflineClock(body);
      return new Response(JSON.stringify({status:'offline',offline:true}),
        {headers:{'Content-Type':'application/json'}});
    }
    return new Response(JSON.stringify({error:'Hors ligne'}), {status:503});
  }
}

// IndexedDB pour stockage offline chiffré
async function storeOfflineClock(data) {
  const db = await openDB();
  const tx = db.transaction('pending_clocks','readwrite');
  tx.objectStore('pending_clocks').add({...data, stored_at: new Date().toISOString()});
}

// Synchronisation arrière-plan
self.addEventListener('sync', e => {
  if (e.tag === 'sync-clocks') e.waitUntil(syncPendingClocks());
});

// Notifications push
self.addEventListener('push', e => {
  const d = e.data?.json() || {};
  e.waitUntil(self.registration.showNotification(d.title, {
    body: d.body, icon: '/static/images/icons/icon-192.png',
    tag: d.tag, data: {url: d.url || '/dashboard/'},
  }));
});

CHAPITRE 9 — ARCHITECTURE GÉOLOCALISATION

9.1 Acquisition GPS côté client
// static/js/geolocation.js
class GeolocationService {
  constructor() {
    this.opts = { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 };
  }
  async getCurrentPosition() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation)
        return reject({code:'UNSUPPORTED',message:'GPS non supporté.'});
      navigator.geolocation.getCurrentPosition(
        pos => resolve({ latitude: pos.coords.latitude,
                         longitude: pos.coords.longitude,
                         accuracy: pos.coords.accuracy,
                         isMock: pos.coords.isMock ?? false }),
        err => reject([
          null,
          {code:'PERMISSION_DENIED', message:'Permission GPS refusée.'},
          {code:'UNAVAILABLE',       message:'GPS indisponible.'},
          {code:'TIMEOUT',           message:'GPS trop lent.'},
        ][err.code]),
        this.opts
      );
    });
  }
}

9.2 Formule Haversine et GeofencingService (Python)
# apps/agencies/utils.py
import math
from dataclasses import dataclass
from typing import Tuple, List

@dataclass
class GeoZone:
    latitude: float
    longitude: float
    radius_meters: float
    name: str = ''

def haversine_distance(lat1,lon1,lat2,lon2) -> float:
    R = 6371000  # mètres
    p1,p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2-lat1)
    dl = math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

class GeofencingService:
    GPS_TOLERANCE = 30  # mètres

    def validate_employee_position(self, employee, lat, lon, accuracy, is_mock) -> dict:
        if is_mock:
            return {'valid':False, 'reason':'GPS_SIMULATED'}
        zones = self._get_zones(employee)
        if not zones:
            return {'valid':False, 'reason':'NO_ZONES_CONFIGURED'}
        for zone in zones:
            d = haversine_distance(lat, lon, zone.latitude, zone.longitude)
            effective = zone.radius_meters + self.GPS_TOLERANCE + max(0, accuracy-30)
            if d <= effective:
                return {'valid':True, 'distance':round(d,2), 'zone':zone.name}
        min_d = min(haversine_distance(lat,lon,z.latitude,z.longitude) for z in zones)
        return {'valid':False, 'reason':'OUT_OF_ZONE', 'distance':round(min_d,2)}

    def _get_zones(self, employee) -> List[GeoZone]:
        zones = []
        for ag in [employee.main_agency] + list(employee.secondary_agencies.all()):
            if ag and ag.status == 'ACTIVE':
                zones.append(GeoZone(float(ag.latitude),float(ag.longitude),float(ag.gps_radius),ag.name))
                for ez in (ag.extra_zones or []):
                    zones.append(GeoZone(ez['lat'],ez['lng'],ez['radius'],f"{ag.name}/(extra)"))
        return zones

CHAPITRE 10 — ARCHITECTURE CAMÉRA

10.1 Capture photo côté client
// static/js/camera.js
class CameraService {
  async initialize(videoId) {
    this.video = document.getElementById(videoId);
    this.canvas = document.createElement('canvas');
    this.stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width:{ideal:640}, height:{ideal:480} },
      audio: false
    });
    this.video.srcObject = this.stream;
    await this.video.play();
  }

  capture(quality=0.85) {
    this.canvas.width  = Math.min(this.video.videoWidth,  640);
    this.canvas.height = Math.min(this.video.videoHeight, 480);
    const ctx = this.canvas.getContext('2d');
    ctx.scale(-1,1);  // Miroir caméra frontale
    ctx.drawImage(this.video, -this.canvas.width, 0, this.canvas.width, this.canvas.height);
    ctx.scale(-1,1);
    return this.canvas.toDataURL('image/jpeg', quality);
  }

  stop() { this.stream?.getTracks().forEach(t => t.stop()); }
}

10.2 Validation et stockage serveur
# apps/attendance/services/photo_service.py
import os, uuid, base64
import magic
from PIL import Image
from io import BytesIO
from django.conf import settings

ALLOWED_MIME = {'image/jpeg','image/png'}
MAX_SIZE = 5 * 1024 * 1024

class PhotoService:
    def process_and_save(self, photo_b64, clock_date) -> str:
        raw = base64.b64decode(photo_b64.split(',')[-1])
        if len(raw) > MAX_SIZE: raise ValueError('Photo trop volumineuse.')
        if magic.from_buffer(raw, mime=True) not in ALLOWED_MIME:
            raise ValueError('Type MIME non autorisé.')
        img = Image.open(BytesIO(raw))
        img.verify()
        img = Image.open(BytesIO(raw))
        img.thumbnail((640,480), Image.LANCZOS)
        if img.mode != 'RGB': img = img.convert('RGB')
        out = BytesIO()
        img.save(out, 'JPEG', quality=85, optimize=True)
        rel = f'attendance-photos/{clock_date[:7]}/{clock_date}/{uuid.uuid4()}.jpg'
        full = os.path.join(settings.MEDIA_ROOT, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full,'wb').write(out.getvalue())
        return rel

CHAPITRE 11 — ARCHITECTURE INTELLIGENCE ARTIFICIELLE

Provider Pattern : interface abstraite commune masquant les différences entre APIs des 7 fournisseurs IA. Isolation tenant garantie architecturalement : aucune donnée cross-tenant possible dans les prompts.

11.1 Fournisseurs supportés
Fournisseur	Modèles et caractéristiques
OpenAI	Modèles : gpt-4o, gpt-4o-mini, gpt-3.5-turbo. API REST. Meilleure performance globale.
Anthropic (Claude)	Modèles : claude-3-5-sonnet, claude-3-haiku. Excellent pour l'analyse de données.
Mistral AI	Modèles : mistral-large, mistral-small. Open source partiel. RGPD EU.
Google Gemini	Modèles : gemini-1.5-pro, gemini-1.5-flash. Multimodal.
Grok (xAI)	Modèles : grok-2. API compatible OpenAI.
DeepSeek	Modèles : deepseek-chat, deepseek-coder. Très économique.
Ollama	Modèles locaux (llama3.2, mistral, phi3). Zéro fuite de données. Pour organisations très sensibles.
11.2 Provider Pattern — Interface abstraite
# apps/ai/providers/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

@dataclass
class AIMessage: role: str; content: str

@dataclass
class AIResponse: content: str; tokens_used: int; model: str; provider: str

class BaseAIProvider(ABC):
    def __init__(self, api_key, model, timeout=30, temperature=0.3, max_tokens=2000, **kw):
        self.api_key=api_key; self.model=model; self.timeout=timeout
        self.temperature=temperature; self.max_tokens=max_tokens

    @abstractmethod
    def chat(self, messages: List[AIMessage]) -> AIResponse: pass


# apps/ai/providers/registry.py
PROVIDER_REGISTRY = {
    'openai':    OpenAIProvider,
    'anthropic': AnthropicProvider,
    'mistral':   MistralProvider,
    'gemini':    GeminiProvider,
    'grok':      GrokProvider,
    'deepseek':  DeepSeekProvider,
    'ollama':    OllamaProvider,
}
def get_provider(name, api_key, model, **kw):
    return PROVIDER_REGISTRY[name](api_key=api_key, model=model, **kw)

11.3 AIService — Isolation tenant stricte
# apps/ai/services/ai_service.py
class AIService:
    SYSTEM = 'Tu es un assistant RH pour {org}. Données : données de {org} uniquement. Langue : {lang}.'

    def __init__(self, tenant):
        self.tenant = tenant
        self.config = OrganizationAIConfig.objects.get(tenant=tenant, is_active=True)
        self.provider = get_provider(self.config.provider_name,
                                     self.config.get_decrypted_api_key(),
                                     self.config.model_name)

    def chat(self, user, question):
        self._check_quota()
        # CRITIQUE : contexte strictement limité au self.tenant via TenantManager
        context = self._build_context(user)
        msgs = [AIMessage('system', self.SYSTEM.format(org=self.tenant.name,lang=self.tenant.language)),
                AIMessage('system', f'Données: {context}'),
                AIMessage('user', question)]
        response = self.provider.chat(msgs)
        self._log(user, question, response)
        self._update_quota(response.tokens_used)
        return response.content

    def _build_context(self, user):
        # Toutes ces requêtes passent par TenantManager (filtré par self.tenant)
        from django.db.models import Count, Avg, Q
        from django.utils import timezone
        today = timezone.now().date()
        return {
            'employees_active': Employee.objects.filter(status='ACTIVE').count(),
            'present_today':    Attendance.objects.filter(clock_date=today).count(),
            'late_today':       Attendance.objects.filter(clock_date=today,status='LATE').count(),
        }  # Jamais de données d'un autre tenant

CHAPITRE 12 — ARCHITECTURE NOTIFICATIONS

Canal	Implémentation
E-mail (SMTP)	Templates HTML Django personnalisés tenant (logo, couleurs). Envoi via Celery async. Retry ×3. Providers : SendGrid, Mailgun, SMTP propre.
Notification push	Web Push API + VAPID. Service Worker. Tokens par appareil. Nettoyage automatique tokens expirés (HTTP 410).
Notification in-app	Modèle Notification en base. Badge compteur dans interface. Polling JS ou WebSocket futur.
SMS (optionnel)	Twilio. Configurable par tenant. Réservé aux alertes critiques.
12.1 Tâches Celery de notification
# apps/notifications/tasks.py
from celery import shared_task
from pywebpush import webpush, WebPushException

@shared_task(bind=True, max_retries=3, default_retry_delay=60, queue='notifications')
def send_email_notification(self, notification_id):
    from apps.notifications.models import Notification
    try:
        notif = Notification.objects.select_related('recipient__tenant').get(id=notification_id)
        ctx = {'tenant_name': notif.recipient.tenant.name,
               'primary_color': notif.recipient.tenant.primary_color,
               'recipient_name': notif.recipient.get_full_name(),
               'body': notif.body, 'action_url': notif.action_url}
        html = render_to_string(f'emails/{notif.template_name}.html', ctx)
        msg = EmailMultiAlternatives(subject=notif.subject,
            from_email=f'{notif.recipient.tenant.name} <noreply@mondomaine.com>',
            to=[notif.recipient.email])
        msg.attach_alternative(html, 'text/html')
        msg.send()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2**self.request.retries*60)

@shared_task(bind=True, max_retries=3, queue='notifications')
def send_push_notification(self, notification_id):
    notif = Notification.objects.get(id=notification_id)
    for sub in PushSubscription.objects.filter(user=notif.recipient, is_active=True):
        try:
            webpush(subscription_info=sub.subscription_data,
                    data=json.dumps({'title':notif.subject,'body':notif.short_body,'url':notif.action_url}),
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={'sub':f'mailto:{settings.VAPID_ADMIN_EMAIL}'})
        except WebPushException as e:
            if e.response and e.response.status_code == 410:
                sub.is_active = False; sub.save()

12.2 Files Celery spécialisées
Queue	Rôle
default	Tâches générales légères.
notifications	Emails, push, SMS — isolé pour prioriser les alertes.
reports	Génération PDF/Excel/CSV — peut prendre plusieurs minutes.
ai	Appels API IA — timeout potentiellement long (30s).
sync	Synchronisation pointages offline — haute priorité.

CHAPITRE 13 — ARCHITECTURE DES RAPPORTS

13.1 Flux de génération asynchrone
Étape	Détail
1. Déclenchement	Utilisateur configure rapport (type, période, filtres, format). Tâche envoyée à Celery. Message 'En cours...' immédiat.
2. Celery génère	ReportLab (PDF), openpyxl (Excel), csv (CSV) en arrière-plan. Timeout 5 minutes.
3. Notification	Celery notifie via in-app + e-mail : 'Votre rapport est prêt.'
4. Téléchargement	URL sécurisée avec token UUID (valide 7 jours). Servie via X-Accel-Redirect Nginx.
5. Nettoyage	Tâche Beat quotidienne supprime les exports > 7 jours.
13.2 Génération PDF — ReportLab
# apps/reports/generators/pdf_generator.py
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from io import BytesIO
import uuid, os

class AttendanceReportPDF:
    def generate(self, tenant, queryset, filters) -> str:
        buf = BytesIO()
        doc = SimpleDocTemplate(buf)
        story = []
        primary = colors.HexColor(tenant.primary_color or '#1565C0')
        data = [['Employé','Date','Type','Heure','Statut','Retard(min)']]
        for att in queryset.select_related('employee'):
            data.append([att.employee.get_full_name(), str(att.clock_date),
                          att.clock_type, str(att.server_time.strftime('%H:%M')),
                          att.status, str(att.delay_minutes or 0)])
        tbl = Table(data, repeatRows=1)
        tbl.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0), primary),
            ('TEXTCOLOR',(0,0),(-1,0), colors.white),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F5F5F5')]),
            ('GRID',(0,0),(-1,-1),0.5,colors.grey),
        ]))
        story.append(tbl)
        doc.build(story)
        rel = f'exports/{tenant.id}/{uuid.uuid4()}.pdf'
        full = os.path.join(settings.MEDIA_ROOT, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full,'wb').write(buf.getvalue())
        return rel

CHAPITRE 14 — ARCHITECTURE DES FICHIERS

14.1 Organisation du stockage
media/                           # MEDIA_ROOT — hors racine web
├── organizations/{tenant_id}/
│   └── logo/                   # Logo organisation
├── employees/{tenant_id}/{emp_id}/
│   ├── profile_photo/
│   ├── contracts/              # Contrats de travail
│   ├── diplomas/               # Diplômes
│   └── documents/              # Autres documents RH
├── attendance-photos/{tenant_id}/YYYY/MM/DD/
│   └── {uuid}.jpg              # Nom UUID non devinable
├── absence-justificatifs/{tenant_id}/{emp_id}/
│   └── {uuid}.pdf/jpg
└── exports/{tenant_id}/YYYY/MM/
    └── {uuid}.pdf/xlsx/csv     # Nettoyés après 7 jours

14.2 Accès sécurisé — X-Accel-Redirect
# apps/documents/views.py
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
import os

@login_required
def serve_protected_file(request, file_path):
    # 1. Vérifier que le fichier appartient au tenant
    if not file_path.startswith(str(request.tenant.id)):
        if 'attendance-photos' not in file_path:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied

    # 2. Vérifier existence
    full = os.path.join(settings.MEDIA_ROOT, file_path)
    if not os.path.isfile(full): raise Http404

    # 3. Retourner X-Accel-Redirect (Nginx sert le fichier directement)
    response = HttpResponse()
    response['X-Accel-Redirect'] = f'/protected-media/{file_path}'
    response['Content-Type'] = ''
    return response

14.3 Politique de rétention
Type	Politique
Photos de pointage	Conservation légale (3-5 ans selon pays). Tâche Celery mensuelle de nettoyage.
Justificatifs absence	5 ans (archives sociales). Accès lecture seule après archivage.
Contrats et documents RH	5 ans après fin de contrat. Téléchargement par l'employé sur sa période active.
Rapports générés	7 jours. Suppression automatique tâche Beat quotidienne.
Logo / fichiers org	Toute la durée de vie du tenant. Supprimés à la suppression du tenant.

CHAPITRE 15 — PERFORMANCES

15.1 Stratégie de cache Redis
# apps/core/cache.py
from django.core.cache import cache
from functools import wraps

def tenant_cache_key(tenant_id, key):
    return f'tenant:{tenant_id}:{key}'

CACHE_TIMEOUTS = {
    'schedules':       3600,
    'agencies':        3600,
    'holidays':        86400,
    'org_settings':    600,
    'attendance_stats':300,
    'dashboard_kpis':  60,
    'user_permissions':900,
}

def cache_tenant_data(key_template, timeout=300):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            tenant_id = str(self.tenant.id) if hasattr(self, 'tenant') else 'global'
            cache_key = tenant_cache_key(tenant_id, key_template.format(*args, **kwargs))
            result = cache.get(cache_key)
            if result is None:
                result = func(self, *args, **kwargs)
                cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

def invalidate_tenant_cache(tenant_id, pattern='*'):
    from django_redis import get_redis_connection
    redis = get_redis_connection('default')
    prefix = f'presence:1:tenant:{tenant_id}:{pattern}'
    keys = redis.keys(prefix)
    if keys:
        redis.delete(*keys)

15.2 Optimisation ORM Django
# Bonnes pratiques ORM

# select_related pour FK (JOIN SQL)
attendances = Attendance.objects.filter(
    clock_date=today
).select_related('employee', 'employee__department', 'agency')

# prefetch_related pour M2M
employees = Employee.objects.filter(
    status='ACTIVE'
).prefetch_related(
    'secondary_agencies',
    Prefetch('attendances', queryset=Attendance.objects.filter(clock_date=today))
)

# only() pour limiter les champs chargés
employees = Employee.objects.only(
    'id', 'first_name', 'last_name', 'matricule', 'status'
)

# Agrégations côté base de données
from django.db.models import Count, Avg, Sum, Q
stats = Attendance.objects.filter(
    clock_date__range=[start, end]
).aggregate(
    total=Count('id'),
    late_count=Count('id', filter=Q(status='LATE')),
    avg_delay=Avg('delay_minutes', filter=Q(delay_minutes__gt=0)),
    total_overtime=Sum('overtime_minutes'),
)

# Pagination obligatoire sur toutes les listes
from django.core.paginator import Paginator
paginator = Paginator(queryset, per_page=25)
page = paginator.get_page(request.GET.get('page', 1))

# iterator() pour les gros exports
for attendance in Attendance.objects.filter(...).iterator(chunk_size=500):
    writer.writerow([...])

# bulk_create pour insertions multiples
Attendance.objects.bulk_create(attendance_list, batch_size=100)

# update() pour modifications en masse
Attendance.objects.filter(
    clock_date=today, status='PENDING_VALIDATION'
).update(status='ON_TIME', validated=True)

15.3 Index de base de données
Type	Implémentation
Index composés critiques	attendances : (tenant_id, clock_date)
attendances : (tenant_id, employee_id, clock_date)
attendances : (tenant_id, status, clock_date)
employees : (tenant_id, status)
absences : (tenant_id, start_date, end_date)
Index FULLTEXT	employees : FULLTEXT(first_name, last_name, email)
audit_logs : FULLTEXT(description)
Partitionnement	PARTITION BY RANGE (YEAR(clock_date)) sur attendances et audit_logs. Améliore les requêtes historiques.
Monitoring index	SELECT * FROM sys.schema_unused_indexes;
SELECT * FROM sys.schema_redundant_indexes;
SHOW INDEX FROM attendances;
15.4 Scalabilité
Dimension	Approche
Scalabilité actuelle	Gunicorn 4 workers × 1 serveur = 500 utilisateurs simultanés. Celery 4 workers async.
Scalabilité horizontale V2	Plusieurs instances Django derrière load balancer. Sessions Redis partagé. Stockage objet S3/MinIO pour les médias.
Stateless Django	Django est stateless (état dans Redis + MySQL). Ajout d'instances transparent.
Celery scaling	Ajout de workers supplémentaires sans configuration. Répartition automatique via Redis broker.

CHAPITRE 16 — JOURNALISATION

16.1 Architecture des logs
Fichier	Description
app.log	Logs applicatifs. Niveau INFO. Format JSON. Rotation 10 Mo × 5 fichiers.
security.log	Connexions, brute force, GPS simulé, cross-tenant. Niveau WARNING. Rotation 10 Mo × 10 fichiers.
error.log	Exceptions Python 500. Niveau ERROR. Envoyé à Sentry en production.
celery.log	Tâches démarrées/terminées/échouées. Niveau INFO.
ai.log	Interactions IA : question anonymisée, provider, tokens, durée.
slow_query.log	Requêtes MySQL > 1s. Analyse hebdomadaire recommandée.
nginx/access.log	Toutes les requêtes HTTP. Format JSON étendu. Rotation quotidienne.
nginx/error.log	Erreurs Nginx : rate limiting, 502, etc.
16.2 Format JSON des logs
# Exemple log applicatif
{
  'asctime': '2025-01-15T09:23:45.123456Z',
  'name': 'apps.attendance',
  'levelname': 'INFO',
  'message': 'Attendance recorded',
  'tenant_id': '550e8400-e29b-41d4-a716-446655440000',
  'user_id': '7c9e6679-7425-40de-944b-e07fc1f90ae7',
  'clock_type': 'ARRIVEE',
  'status': 'ON_TIME',
  'duration_ms': 245
}

# Exemple log sécurité
{
  'asctime': '2025-01-15T09:23:45.123456Z',
  'name': 'apps.security',
  'levelname': 'WARNING',
  'message': 'Failed login attempt',
  'email': 'user@example.com',
  'ip_address': '192.168.1.100',
  'attempt_number': 3
}

16.3 Sentry en production
# settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=env('SENTRY_DSN', default=''),
    integrations=[DjangoIntegration(), CeleryIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
    environment='production',
)

CHAPITRE 17 — SAUVEGARDES

17.1 Script de sauvegarde automatique
#!/bin/bash
# scripts/backup.sh
set -euo pipefail

BACKUP_DIR='/backups'
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="presence_backup_${DATE}"
RETENTION_DAILY=7

source /app/.env
echo "[$(date)] Starting backup: ${BACKUP_NAME}"

# 1. Dump MySQL
mysqldump \
    --host=${MYSQL_HOST} --user=${MYSQL_USER} \
    --password=${MYSQL_PASSWORD} \
    --single-transaction --routines --triggers \
    ${MYSQL_DATABASE} | gzip > "${BACKUP_DIR}/mysql_${BACKUP_NAME}.sql.gz"

# 2. Archive médias
tar -czf "${BACKUP_DIR}/media_${BACKUP_NAME}.tar.gz" \
    --exclude='*/exports/*' /app/media/

# 3. Chiffrement AES-256
openssl enc -aes-256-cbc -salt -pbkdf2 \
    -in "${BACKUP_DIR}/mysql_${BACKUP_NAME}.sql.gz" \
    -out "${BACKUP_DIR}/mysql_${BACKUP_NAME}.sql.gz.enc" \
    -pass env:BACKUP_ENCRYPTION_KEY
rm "${BACKUP_DIR}/mysql_${BACKUP_NAME}.sql.gz"

# 4. Checksum SHA-256
sha256sum "${BACKUP_DIR}/mysql_${BACKUP_NAME}.sql.gz.enc" >> "${BACKUP_DIR}/checksums.txt"
sha256sum "${BACKUP_DIR}/media_${BACKUP_NAME}.tar.gz.enc" >> "${BACKUP_DIR}/checksums.txt"

# 5. Rotation
ls -t ${BACKUP_DIR}/mysql_*.enc | tail -n +$((RETENTION_DAILY + 1)) | xargs rm -f 2>/dev/null || true

echo "[$(date)] Backup completed: ${BACKUP_NAME}"

17.2 Planification Celery Beat
# Tâche quotidienne à 02:00 UTC
@shared_task(name='core.backup_database')
def backup_database():
    result = subprocess.run(['/scripts/backup.sh'], capture_output=True, text=True, timeout=3600)
    if result.returncode != 0:
        logger.error(f'Backup failed: {result.stderr}')
        send_superadmin_alert.delay('BACKUP_FAILED', result.stderr)
    else:
        logger.info('Backup successful')

# Cron : 0 2 * * *  -> backup quotidien
# Cron : 0 3 * * 0  -> test restauration hebdomadaire

17.3 Procédure de restauration
#!/bin/bash
# scripts/restore.sh
BACKUP_FILE=$1
source /app/.env

# Déchiffrement
openssl enc -aes-256-cbc -d -pbkdf2 \
    -in "$BACKUP_FILE" -out /tmp/restore.sql.gz \
    -pass env:BACKUP_ENCRYPTION_KEY

# Vérification checksum
CHECKSUM=$(sha256sum /tmp/restore.sql.gz | awk '{print $1}')
if ! grep -q "$CHECKSUM" /backups/checksums.txt; then
    echo 'ERREUR: Checksum invalide ! Fichier corrompu.'
    exit 1
fi

# Restauration MySQL
mysql --host=${MYSQL_HOST} --user=root --password=${MYSQL_ROOT_PASSWORD} \
    -e "DROP DATABASE IF EXISTS ${MYSQL_DATABASE}; CREATE DATABASE ${MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

gunzip -c /tmp/restore.sql.gz | mysql \
    --host=${MYSQL_HOST} --user=root --password=${MYSQL_ROOT_PASSWORD} ${MYSQL_DATABASE}

rm /tmp/restore.sql.gz
echo 'Restauration terminée avec succès.'
Politique	Détail
Sauvegarde quotidienne	02:00 UTC. MySQL dump + médias. Chiffrement AES-256. Checksum SHA-256.
Sauvegarde différentielle	Toutes les 6h via binlog MySQL (Binary Log).
Rétention	7 sauvegardes quotidiennes, 4 hebdomadaires, 3 mensuelles.
Test restauration	Dimanche 03:00 UTC sur environnement de test. Résultat loggé.
RTO (Recovery Time Objective)	< 4 heures : temps de reprise après incident majeur.
RPO (Recovery Point Objective)	< 6 heures : perte de données maximale acceptable.

CHAPITRE 18 — DÉPLOIEMENT

18.1 Environnements
Environnement	Configuration
Développement	docker-compose.yml. DEBUG=True. phpMyAdmin. Hot reload. Emails via MailHog.
Staging	docker-compose.prod.yml. DEBUG=False. Données réalistes. TLS Let's Encrypt. Miroir production.
Production	docker-compose.prod.yml. Toutes optimisations. Sauvegardes auto. Monitoring actif.
18.2 Pipeline CI/CD GitHub Actions
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: testpassword
          MYSQL_DATABASE: presence_test
          MYSQL_USER: presence_test
          MYSQL_PASSWORD: testpassword
        ports: ['3306:3306']
        options: --health-cmd='mysqladmin ping' --health-interval=10s
      redis:
        image: redis:7-alpine
        ports: ['6379:6379']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: Install dependencies
        run: pip install -r requirements/development.txt
      - name: Linting
        run: flake8 apps/ && black --check apps/ && isort --check-only apps/
      - name: Security scan
        run: bandit -r apps/ -x apps/*/tests/ -ll
      - name: Tests
        env:
          DJANGO_SETTINGS_MODULE: config.settings.development
          MYSQL_HOST: 127.0.0.1
          DJANGO_SECRET_KEY: test-only
        run: |
          python manage.py migrate --noinput
          coverage run manage.py test apps/ --parallel
          coverage report --fail-under=80

  build:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}/presence-saas:${{ github.sha }}

  deploy:
    needs: build
    environment: production
    runs-on: ubuntu-latest
    steps:
      - uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/presence-saas
            export IMAGE_TAG=${{ github.sha }}
            docker compose -f docker-compose.prod.yml pull web celery
            docker compose -f docker-compose.prod.yml up -d --no-deps web celery
            docker compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput
            docker compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput
            sleep 10 && curl -sf http://localhost/health/ || exit 1

18.3 Settings production
# config/settings/production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookies sécurisés
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Fichiers statiques WhiteNoise + Brotli
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

CHAPITRE 19 — SUPERVISION ET MONITORING

19.1 Endpoint de santé
# apps/core/views.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache

def health_check(request):
    checks = {}
    overall = 'healthy'

    # MySQL
    try:
        with connection.cursor() as cursor: cursor.execute('SELECT 1')
        checks['database'] = {'status': 'ok'}
    except Exception as e:
        checks['database'] = {'status': 'error', 'error': str(e)}
        overall = 'unhealthy'

    # Redis
    try:
        cache.set('hc', 'ok', 10)
        assert cache.get('hc') == 'ok'
        checks['redis'] = {'status': 'ok'}
    except Exception as e:
        checks['redis'] = {'status': 'error'}
        overall = 'degraded'

    # Disk
    import shutil
    disk = shutil.disk_usage('/app/media')
    pct = disk.used / disk.total * 100
    checks['disk'] = {'status': 'ok' if pct < 85 else 'warning', 'used_pct': round(pct, 1)}
    if pct >= 90: overall = 'degraded'

    return JsonResponse({'status': overall, 'checks': checks}, status=200 if overall == 'healthy' else 503)

19.2 Métriques et alertes
Outil	Rôle
Uptime Robot	Surveillance HTTP /health/ toutes les 5 minutes. Alerte e-mail + SMS si indisponible.
Sentry	Capture des exceptions Python. Alertes nouvelles erreurs. Monitoring performances.
Flower (Celery)	Interface web : queues, workers actifs, tâches en échec, temps d'exécution.
Slow Query Log MySQL	Requêtes > 1s. Analyse hebdomadaire pour optimisation.
Alerte disque	Script cron toutes les heures. Alerte Super Admin si > 80%.
19.3 Seuils d'alerte critiques
Seuil	Action
Disponibilité < 99%	Alerte immédiate Super Admin (e-mail + SMS). Ouverture incident.
Erreurs 500 > 10/min	Alerte Sentry. Vérification état conteneurs Docker.
MySQL connexions > 150/200	Alerte capacité. Investiguer connexions lentes.
Redis mémoire > 80%	Alerte capacité. Vérifier TTL et augmenter mémoire.
Celery queue > 1000 tâches	Alerte saturation. Ajouter workers.
Disque > 85%	Alerte préventive. Nettoyage exports et logs anciens.
Sauvegarde échouée	Alerte immédiate Super Admin. Relance manuelle.
Cross-tenant attempt > 0	Alerte CRITIQUE sécurité. Investigation immédiate.

CHAPITRE 20 — STRATÉGIE DE TESTS TECHNIQUES

20.1 Pyramide de tests
Niveau	Description
Tests unitaires (70%)	Fonctions et méthodes isolées. Mocks pour dépendances. Rapides < 100ms. Couverture cible > 80%.
Tests d'intégration (20%)	Interaction Django + MySQL, Django + Celery. BDD réelle de test. Workflows complets.
Tests end-to-end (10%)	Scénarios utilisateur via Selenium/Playwright. Navigateur réel. Fonctionnalités clés : pointage, login.
20.2 Tests unitaires — Geofencing
# apps/attendance/tests/test_geofencing.py
from django.test import TestCase
from apps.agencies.utils import haversine_distance, GeofencingService, GeoZone

class HaversineDistanceTest(TestCase):
    def test_same_point_is_zero(self):
        d = haversine_distance(48.8566, 2.3522, 48.8566, 2.3522)
        self.assertAlmostEqual(d, 0, places=2)

    def test_within_100m(self):
        lat2 = 48.8566 + 0.00072  # ~80m au nord
        d = haversine_distance(48.8566, 2.3522, lat2, 2.3522)
        self.assertLess(d, 100)

    def test_mocked_gps_always_rejected(self):
        from unittest.mock import MagicMock
        service = GeofencingService()
        result = service.validate_employee_position(
            employee=MagicMock(), latitude=48.8566, longitude=2.3522,
            gps_accuracy=5, is_mock=True
        )
        self.assertFalse(result['valid'])
        self.assertEqual(result['reason'], 'GPS_SIMULATED')

20.3 Tests d'isolation multi-tenant
# apps/tenants/tests/test_isolation.py
from django.test import TestCase
from django.urls import reverse
from apps.tenants.models import Organization
from apps.accounts.models import User
from apps.employees.models import Employee

class TenantIsolationTest(TestCase):
    def setUp(self):
        self.tenant_a = Organization.objects.create(
            name='Entreprise A', slug='entreprise-a', status='ACTIVE')
        self.user_a = User.objects.create_user(
            email='a@test.com', password='Pass123!', tenant=self.tenant_a, role='ADMIN')
        self.emp_a = Employee.objects.create(tenant=self.tenant_a, user=self.user_a)

        self.tenant_b = Organization.objects.create(
            name='Entreprise B', slug='entreprise-b', status='ACTIVE')
        self.user_b = User.objects.create_user(
            email='b@test.com', password='Pass123!', tenant=self.tenant_b, role='ADMIN')
        self.emp_b = Employee.objects.create(tenant=self.tenant_b, user=self.user_b)

    def test_user_a_cannot_see_tenant_b_employees(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse('employees:list'))
        employee_ids = [e.id for e in response.context['employees']]
        self.assertIn(self.emp_a.id, employee_ids)
        self.assertNotIn(self.emp_b.id, employee_ids)

    def test_cross_tenant_url_returns_404(self):
        self.client.force_login(self.user_a)
        response = self.client.get(f'/employees/{self.emp_b.id}/')
        self.assertIn(response.status_code, [403, 404])

20.4 Tests de sécurité
# apps/accounts/tests/test_security.py
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User

class AuthSecurityTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(
            email='test@test.com', password='StrongPass123!')

    def test_brute_force_lockout(self):
        for _ in range(5):
            self.client.post(reverse('accounts:login'), {
                'username': 'test@test.com', 'password': 'wrong'})
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.locked_until)

    def test_csrf_protection(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'test@test.com', 'password': 'test'})
        self.assertEqual(response.status_code, 403)

    def test_session_invalidated_on_password_change(self):
        client2 = Client()
        client2.force_login(self.user)
        self.client.force_login(self.user)
        self.client.post(reverse('accounts:change-password'), {
            'old_password': 'StrongPass123!',
            'new_password1': 'NewStrong456!', 'new_password2': 'NewStrong456!'})
        response = client2.get(reverse('dashboard:index'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next=/dashboard/")

20.5 Tests de charge Locust
# locustfile.py
from locust import HttpUser, task, between
import random

class PresenceUser(HttpUser):
    wait_time = between(1, 5)
    host = 'https://staging.mondomaine.com'

    def on_start(self):
        self.client.post('/login/', {
            'username': f'employee{random.randint(1,100)}@test.com',
            'password': 'TestPass123!',})

    @task(3)
    def view_dashboard(self):
        self.client.get('/dashboard/')

    @task(5)
    def clock_in(self):
        self.client.post('/api/v1/attendance/clock/', json={
            'type': 'ARRIVEE',
            'latitude': 48.8566 + random.uniform(-0.001, 0.001),
            'longitude': 2.3522 + random.uniform(-0.001, 0.001),
            'accuracy': 15, 'photo': 'data:image/jpeg;base64,/9j/...', 'is_mock': False})

    @task(1)
    def view_history(self):
        self.client.get('/attendance/history/')

# Exécution : locust --users=500 --spawn-rate=50 --run-time=5m
# Objectif : p95 < 2s sous 500 utilisateurs simultanés

20.6 Standards de qualité du code
Standard	Description
PEP 8 + Black	Formatage automatique. line-length=120. Vérification CI automatique.
isort	Tri imports compatible Black.
Type hints	Annotations Python 3.11+ sur toutes les fonctions publiques. Vérification mypy.
Docstrings	Google Style sur toutes les classes et méthodes publiques.
Bandit (SAST)	Détection automatique des vulnérabilités Python dans le CI.
Coverage > 80%	Rapport coverage.xml uploadé Codecov. Bloque le merge si < 80%.
Pre-commit hooks	black, isort, flake8, bandit exécutés avant chaque commit.
django-extensions	shell_plus, show_urls, graph_models pour le développement.
20.7 Makefile
# Makefile
up:             docker compose --profile dev up -d
down:           docker compose down
logs:           docker compose logs -f web celery
shell:          docker compose exec web python manage.py shell_plus
test:           docker compose exec web python manage.py test apps/ --verbosity=2
coverage:       docker compose exec web coverage run manage.py test apps/ && coverage report
lint:           docker compose exec web flake8 apps/ && black --check apps/
format:         docker compose exec web black apps/ && isort apps/
migrate:        docker compose exec web python manage.py migrate
backup:         docker compose exec web /scripts/backup.sh
security-scan:  docker compose exec web bandit -r apps/ -x apps/*/tests/ -ll
load-test:      locust --host=http://localhost:8000 --users=100 --spawn-rate=10

CONCLUSION — RÉCAPITULATIF ARCHITECTURE TECHNIQUE

Ce document constitue la référence technique complète de la plateforme SaaS de gestion de présence. Il couvre 20 dimensions architecturales pour le développement, le déploiement et la maintenance.

Composant	Technologie / Approche
Stack backend	Python 3.11+ / Django 4.2 LTS / Gunicorn 4 workers
Stack frontend	Django Templates / Bootstrap 5.3 / JavaScript ES6+ / Service Worker PWA
Base de données	MySQL 8.0 InnoDB / utf8mb4 / Partitionnement par année
Cache et queues	Redis 7 (cache + sessions + Celery broker)
Tâches async	Celery 5 — 5 queues : default, notifications, reports, ai, sync
Conteneurisation	Docker 24+ / Docker Compose v2 / 7 services en production
Reverse proxy	Nginx 1.25 — TLS, rate limiting, X-Accel-Redirect, compression Brotli
Multi-tenant	Shared Schema / TenantManager (thread local) / TenantMiddleware
Sécurité	Argon2id / RBAC / CSRF / CSP / HSTS / Rate limiting / Audit triggers MySQL
PWA	Service Worker / IndexedDB offline / Web Push VAPID / Background Sync
Géolocalisation	Haversine Python / GeofencingService / Mock detection / Zones multiples
Caméra	getUserMedia facingMode:user / Canvas capture / Pillow validation serveur
IA	Provider Pattern / 7 fournisseurs / Isolation tenant stricte / Quota / Logs
Notifications	Celery async / HTML e-mail / Web Push / In-app / Retry ×3
Rapports	ReportLab PDF / openpyxl Excel / CSV / Async / X-Accel download sécurisé
Tests	pytest-django / 80% coverage / Isolation tenant / Locust 500 users
CI/CD	GitHub Actions — lint + bandit + tests + build Docker + deploy SSH
Sauvegardes	Dump MySQL daily + AES-256 + SHA-256 / Rétention 7j/4sem/3mois
Monitoring	Sentry / /health/ endpoint / Uptime Robot / Flower Celery / Slow query log
Standards	PEP8 / Black / isort / mypy / Google docstrings / Bandit SAST / Pre-commit
PEP8 / Black / isort / mypy / Google docstrings / Bandit SAST / Pre-commit