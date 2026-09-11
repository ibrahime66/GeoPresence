# Audit sécurité & cohérence — GeoPresence

Scan complet du code (`apps/`, `config/`, `templates/`, `static/`) + vérifications sur la prod (`geopresence.site`).
Date de l'audit : 2026-09-10.

Légende : 🔴 critique · 🟠 élevé · 🟡 moyen · 🔵 durcissement · ⚪ incohérence (non-sécurité)

---

## Suivi de résolution

On corrige du plus critique au plus faible. Une PR (ou un lot de PR) par bloc.

| # | Sévérité | Titre | Statut | PR | Déployé |
|---|----------|-------|--------|----|---------|
| 1 | 🔴 | IP client réelle jamais lue (`REMOTE_ADDR` = `127.0.0.1`) | ✅ corrigé | #7 | ⏳ |
| 2 | 🔴 | `/admin/` contourne verrouillage + rate-limit + CAPTCHA | ⬜ à faire | — | — |
| 3 | 🔴 | `gps_accuracy` non borné → géofencing contournable | ⬜ à faire | — | — |
| 4 | 🔴 | `mode=OFFLINE` piloté par le client sur l'endpoint en ligne | ⬜ à faire | — | — |
| 5 | 🟡 | CAPTCHA désactivé en prod | ⬜ à faire | — | — |
| 6 | 🟡 | Pas de rate-limit sur la demande de reset mot de passe | ⬜ à faire | — | — |
| 7 | 🟡 | Énumération de comptes par timing au login | ⬜ à faire | — | — |
| 8 | 🟡 | XSS stocké potentiel : `agency_zones_json\|safe` | ⬜ à faire | — | — |
| 9 | 🟡 | CSP `script-src 'unsafe-inline'` | ⬜ à faire | — | — |
| 10 | 🟡 | DoS verrouillage de compte ciblé | ⬜ à faire | — | — |
| 11 | 🔵 | `CSRF_TRUSTED_ORIGINS` non défini | ⬜ à faire | — | — |
| 12 | 🔵 | `BackupDownloadView` sans confinement de chemin | ⬜ à faire | — | — |
| 13 | 🔵 | Org DELETED réactivable par POST direct | ⬜ à faire | — | — |
| 14 | 🔵 | Matricule employé : race condition `count()+1` | ⬜ à faire | — | — |
| 15 | 🔵 | Admin Django monté en prod (surface) | ⬜ à faire | — | — |
| 16 | 🔵 | `seed_demo.py` mot de passe en dur | ⬜ à faire | — | — |
| 17 | ⚪ | Index `(tenant, created_at)` manquant sur plusieurs tables | ⬜ à faire | — | — |
| 18 | ⚪ | Données de prod à nettoyer (orgs + comptes en double) | ⬜ à faire | — | — |
| 19 | ⚪ | Pas d'autorisation niveau objet (filtres `tenant=` manuels) | ⬜ à faire | — | — |
| 20 | ⚪ | `TenantModel` : manager par défaut non filtré (admin) | ⬜ à faire | — | — |
| 21 | ⚪ | Dashboard admin : ~115 requêtes SQL / chargement | ⬜ à faire | — | — |
| 22 | ⚪ | `attendance_history` mobile : logo au milieu de page | ⬜ à faire | — | — |
| 23 | ⚪ | Commentaire geofencing ↔ code divergent (flag inexistant) | ⬜ à faire | — | — |

---

## 🔴 1 — L'IP réelle du client n'est jamais lue (tout est `127.0.0.1` en prod)

`request.META["REMOTE_ADDR"]` est utilisé partout, or derrière Nginx c'est toujours l'IP du proxy (`127.0.0.1`). Nginx transmet bien `X-Real-IP` / `X-Forwarded-For` mais **aucun code ne les lit**, et il n'y a pas de middleware qui promeut le XFF.

- `apps/security/ratelimit.py:15` `get_client_ip` → `REMOTE_ADDR`
- `apps/audit/services.py:52` `ip_address=request.META.get("REMOTE_ADDR")`
- `apps/attendance/views.py:120` (IP du pointage)
- `apps/accounts/sessions.py:55` (IP de la session)

**Vérifié en prod** : 100 % des lignes `AuditLog` et `UserSession` ont `ip_address = '127.0.0.1'`.

**Impact :**
- Le rate-limiting de connexion (`login_ip`, 10/min) est un **seul compteur global** : 10 tentatives/minute pour *tout le site*. Un attaquant sature le seau et bloque les connexions légitimes ; le throttling par attaquant n'existe pas.
- Le journal d'audit (CDC §14/§17) est **inexploitable en investigation** — aucune IP réelle.
- L'écran « Sessions actives » (CDC §5.6.2) affiche `127.0.0.1` pour tous les appareils : impossible de repérer une session suspecte.
- La trace forensique d'un pointage (CDC §9) est vide.

**Correctif :** middleware de confiance proxy (ne lire `X-Forwarded-For[0]` que parce qu'on sait qu'on est derrière un unique Nginx local) qui réécrit `REMOTE_ADDR`, OU passer par `django-ipware`. Placer avant tous les middlewares custom.

---

## 🔴 2 — L'admin Django (`/admin/`) contourne verrouillage + rate-limit + CAPTCHA

Le durcissement anti-brute-force (verrouillage progressif, rate-limit, CAPTCHA) vit **uniquement** dans `apps/accounts/views.py::LoginView`. La connexion de l'admin Django (`/admin/login/`) passe par `django.contrib.auth` + `ModelBackend`, qui ne vérifie que `is_active` — **jamais `locked_until`**.

**Vérifié en prod :** `https://geopresence.site/admin/` → 302 vers le formulaire de login, exposé publiquement.

**Impact :** un attaquant peut brute-forcer le mot de passe du **Super Administrateur** sur `/admin/login/` sans aucune limite (pas de lockout, pas de rate-limit, pas de CAPTCHA). Le Super Admin est le seul `is_staff=True` → jackpot complet (accès à toutes les organisations via l'admin).

**Correctif (au choix) :**
- désactiver l'admin Django en prod si personne ne s'en sert (`admin.site` non monté dans `config/urls.py` en production) ;
- sinon restreindre `location /admin/` par IP dans Nginx (`allow <IP bureau>; deny all;`) ;
- a minima : `AdminAuthenticationForm` custom qui applique le même lockout que `LoginView`.

---

## 🔴 3 — `gps_accuracy` non borné → contournement total du géofencing

`apps/agencies/geofencing.py:31-34` : si `gps_accuracy > tolerance`, on ajoute **toute** la valeur au rayon effectif.

```python
if gps_accuracy and gps_accuracy > tolerance_meters:
    tolerance += float(gps_accuracy) - tolerance_meters
```

`gps_accuracy` vient du client (`ClockForm.gps_accuracy = DecimalField(max_digits=8, decimal_places=2)` → jusqu'à **999 999.99**). Aucun plafond, aucun rejet, aucun flag.

**Impact :** un employé qui POST `gps_accuracy=999999` sur `/api/pointage/` obtient un rayon effectif ≈ 1 000 km → **il pointe depuis n'importe où**, avec le statut `ON_TIME` (même pas `PENDING_VALIDATION`). Le commentaire du code affirme « l'anomalie est enregistrée séparément (flag "précision faible") » — **ce flag n'existe nulle part**.

**Correctif :** plafonner `gps_accuracy` (ex. 100 m) ; au-delà → soit rejet (`ClockRejected`), soit acceptation forcée en `PENDING_VALIDATION` + champ `Attendance.low_gps_precision=True` réellement écrit et visible dans les écrans de validation.

---

## 🔴 4 — `mode=OFFLINE` est piloté par le client sur l'endpoint en ligne

`apps/attendance/forms.py` expose `mode = ChoiceField(choices=Attendance.Mode.choices, required=False)` et `apps/attendance/views.py:123` le passe tel quel à `clock(...)`. Il n'y a **qu'un seul** endpoint de pointage (`/api/pointage/`).

Dans `services.clock()`, un pointage `OFFLINE` **hors zone GPS** n'est pas rejeté : il est enregistré `PENDING_VALIDATION` rattaché à `employee.primary_agency`.

**Impact :** un employé POST `mode=OFFLINE` + `client_time` récent + une position hors zone → le pointage est accepté (en attente) au lieu d'être refusé. Un admin qui valide les pointages en attente en lot peut entériner une fraude. Le CDC §9.3.6 exige une re-validation serveur *complète* ; ici le fait « je suis hors ligne » est cru sur parole.

**Correctif :** forcer `mode=ONLINE` sur `/api/pointage/` (ignorer le champ du formulaire) ; ne créer un vrai endpoint `/api/pointage/sync/` distinct que le jour où le mode hors ligne est réellement implémenté, avec ses propres contrôles.

---

## 🟡 5 — CAPTCHA désactivé en production

`HCAPTCHA_SITE_KEY` / `HCAPTCHA_SECRET_KEY` vides en prod → `captcha.is_enabled()` renvoie `False` → l'étape CAPTCHA (CDC §13.4, après 3 échecs + sur le reset de mot de passe) est neutralisée partout. Seules défenses restantes : lockout + rate-limit (ce dernier cassé, cf. #1).

**Correctif :** créer un compte hCaptcha, renseigner les deux clés dans `.env` prod.

---

## 🟡 6 — Aucun rate-limit sur la demande de réinitialisation de mot de passe

`apps/accounts/views.py::PasswordResetRequestView` n'appelle **pas** `ratelimit.hit(...)` (contrairement à `LoginView`). Seule barrière : le CAPTCHA — désactivé en prod (#5).

**Impact :** un attaquant spamme des e-mails de réinitialisation vers n'importe quel compte (harcèlement e-mail, saturation du journal d'audit, épuisement du quota SMTP Gmail).

**Correctif :** `ratelimit.hit("pwreset_ip", ip, limit=5, window_seconds=3600)` + éventuellement un seau par e-mail.

---

## 🟡 7 — Énumération de comptes par mesure de temps sur le login

`LoginView.form_valid` : quand l'e-mail n'existe pas, on ne calcule **pas** de hash. Quand il existe, `user.check_password()` (Argon2id, volontairement lent) tourne. La différence de temps de réponse permet de distinguer « e-mail connu » de « e-mail inconnu ».

**Correctif :** exécuter un `check_password` factice contre un hash bidon quand `user is None` (constant-time).

---

## 🟡 8 — XSS stocké potentiel : `agency_zones_json|safe` dans un `<script>`

`templates/attendance/clock.html:88` : `"zones": {{ agency_zones_json|default:"[]"|safe }}`. La valeur est du `json.dumps(...)` — **qui n'échappe pas `</script>`**. Un label de zone ou un nom d'agence contenant `</script><script>…` s'exécute.

**Impact :** limité (seuls les Admins définissent zones/agences, sur leur propre org → surtout self-XSS), mais reste une vraie sortie non échappée dans un contexte script.

**Correctif :** remplacer par `{{ agency_zones|json_script:"agency-zones" }}` et lire via `JSON.parse(document.getElementById('agency-zones').textContent)` (comme déjà fait pour les graphiques du dashboard).

---

## 🟡 9 — CSP avec `script-src 'unsafe-inline'`

`apps/security/middleware.py` : `script-src 'self' 'unsafe-inline' …`. Toute injection `<script>` ou `onerror=` s'exécute → la CSP n'offre quasi aucune protection XSS. C'est dû à l'usage massif de `<script>` inline et de `onclick=` dans les templates (y compris ceux ajoutés récemment).

**Correctif (moyen terme) :** système de nonce CSP + sortir le JS inline dans des fichiers.

---

## 🟡 10 — DoS par verrouillage de compte ciblé

5 mauvais mots de passe → verrouillage progressif 15 / 30 / 60 / 240 / **1440** min. Avec ~25 tentatives, un attaquant garde une victime bloquée 24 h, et peut recommencer. Combiné à #1 (rate-limit global, pas par IP), c'est faisable en continu depuis une seule machine.

C'est un compromis inhérent aux politiques de lockout imposées par le CDC §13.3, mais à connaître. Atténuation : lockout basé sur (IP + compte) plutôt que compte seul, une fois #1 corrigé.

---

## 🔵 11 — `CSRF_TRUSTED_ORIGINS` non défini

Fonctionne aujourd'hui (Django dérive l'origine depuis `Host` + scheme, et tout est same-origin), mais fragile si un jour un sous-domaine / un domaine alternatif est ajouté. À poser explicitement : `CSRF_TRUSTED_ORIGINS = ["https://geopresence.site", "https://www.geopresence.site"]`.

## 🔵 12 — `BackupDownloadView` sans confinement de chemin

`apps/backups/views.py` : `Path(settings.BACKUP_DIR) / backup.filename` sans `.resolve()` ni vérification `is_relative_to(BACKUP_DIR)`. `filename` est généré par le système (pas d'entrée utilisateur) → risque théorique seulement, mais un `path.resolve()` + garde coûte 2 lignes. Réservé au Super Admin de toute façon.

## 🔵 13 — Organisation « supprimée » réactivable par POST direct

`OrganizationDeleteView` met `status=DELETED` (soft delete, correct pour la conservation légale). Mais l'UI cache seulement le menu ; `POST /superadmin/organisations/<pk>/reactiver/` remet `status=ACTIVE` même sur une org DELETED, ce qui contredit le docstring « totalement et définitivement inaccessible ». Ajouter un garde `if org.status == DELETED: 404` dans `OrganizationReactivateView`.

## 🔵 14 — Génération du matricule employé : race condition

`apps/employees/models.py::_generate_matricule` = `objects.all_tenants().filter(tenant=…).count() + 1`. Deux créations simultanées → même matricule → `IntegrityError` non gérée (500). Utiliser une séquence atomique ou un retry.

## 🔵 15 — Admin Django monté en prod pour un seul utilisateur potentiel

Voir #2. Même si le brute-force est corrigé, l'admin Django expose *toutes* les données de *toutes* les organisations (les `ModelAdmin` ne surchargent pas tous `get_queryset`, et de toute façon le Super Admin est censé tout voir). Surface à réduire.

## 🔵 16 — `apps/core/management/commands/seed_demo.py` : mot de passe en dur `Demo1234!`

Non exécuté en prod (aucun compte demo trouvé), mais la commande existe. S'assurer qu'elle refuse de tourner si `DEBUG=False`.

---

## ⚪ Incohérences (hors sécurité)

**17 — Index `(tenant, created_at)` manquant sur plusieurs tables.**
`TenantModel.Meta.indexes` définit `%(app_label)s_%(class)s_tc_idx`, mais Django **n'hérite pas** les `indexes` d'une `Meta` abstraite quand la sous-classe redéfinit `class Meta:` sans hériter. Concernés : `ScheduleSlot`, `EmployeeScheduleAssignment`, `SlotException`, et tout modèle avec un `class Meta:` propre. Ces tables n'ont pas l'index `(tenant, created_at)` (impact perf, pas sécurité).

**18 — Données de prod à nettoyer.**
Deux organisations `Revyon Tech` / `Revyon tech` actives + une DELETED. Comptes de test en double : `ibrahimebarry520@glail.com` (typo « glail », inactif) vs `…@gmail.com`, `salimdiaby3028` vs `salimoudiaby3028`.

**19 — `RoleRequiredMixin` ne fait pas d'autorisation au niveau objet.**
La sécurité inter-tenant repose *entièrement* sur le fait que chaque vue filtre ses querysets par `tenant`. C'est fait correctement partout où j'ai regardé, mais un seul `all_tenants().filter(pk=…)` sans `tenant=` = fuite inter-organisation. Le pattern `X.objects.all_tenants().filter(tenant=request.tenant)` est répété ~50 fois ; un `X.objects.filter(...)` (manager déjà scopé au tenant courant) serait plus sûr par défaut. À défaut : un test d'intégration « aucune vue ne renvoie de données d'un autre tenant ».

**20 — `TenantModel` : le manager par défaut est le manager NON filtré.**
`default_manager_name = "all_objects"`. Nécessaire pour les relations inverses/cascades, mais conséquence : `Model.objects` (le manager *filtré*) n'est pas le défaut. L'admin Django et toute relation inverse voient *tout*. Chaque `ModelAdmin` doit penser à surcharger `get_queryset` — plusieurs ne le font pas (cf. #15).

**21 — Tableau de bord Admin : ~115 requêtes SQL par chargement.**
Boucle de 30 jours sur `_presence_rate` dans `_admin_context` (`apps/core/views.py`). Rendu ~200-470 ms serveur, mais optimisable (une seule requête agrégée par `GROUP BY clock_date`).

**22 — `attendance_history` mobile : logo GeoPresence qui apparaît en milieu de page.**
Artefact de la barre de nav `position: fixed` capturée par le rendu — cosmétique, à vérifier.

**23 — Le commentaire de `_find_matching_agency` / geofencing parle d'un « flag précision faible » inexistant** (cf. #3) — le code et sa doc divergent.

---

## Ce qui est solide (pour mémoire)

- Isolation multi-tenant : `TenantManager` fail-secure (`.none()` si pas de tenant), `clean()` qui revalide les FK inter-tenant sur `Employee`, `SlotException`, etc.
- Formulaires : tous les `ModelChoiceField` sont scopés au tenant (`.all_tenants().filter(tenant=…)`).
- Mots de passe : Argon2id, 11 validateurs, historique, expiration, changement forcé.
- Auth : verrouillage progressif, messages génériques, `next` validé contre l'open-redirect, logout POST-only, révocation de sessions.
- IA : contexte strictement dérivé de `user` (agrégats tenant), sortie rendue échappée (`textContent` / `{{ }}`), quota par organisation. Pas de fuite inter-tenant même avec un jailbreak du prompt.
- Pointage : re-validation serveur, GPS simulé rejeté sans condition, séquence arrivée/départ contrôlée, heure serveur = source de vérité.
- Sauvegardes : AES-256, checksum vérifié avant restauration, mot de passe MySQL via env (pas argv).
- En-têtes : HSTS, CSP, Permissions-Policy, `Cache-Control: no-store` sur les pages authentifiées, cookies `Secure` + `HttpOnly` + `SameSite=Strict`.
- Secrets hors git, `.env` en `600`, `DEBUG=False` en prod, `ALLOWED_HOSTS` correct.
