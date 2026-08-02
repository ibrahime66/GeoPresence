CAHIER DES CHARGES
Plateforme SaaS Intelligente de Gestion de Présence

Document de spécifications fonctionnelles et techniques
Version 1.0 — Révision initiale
Champ	Valeur
Référence	CDC-PRESENCE-SAAS-V1.0
Date de rédaction	2025
Statut	Draft final — soumis pour validation
Confidentialité	Confidentiel — usage interne
Technologies	Python / Django / MySQL 8 / Bootstrap 5
Architecture	SaaS Multi-Tenant / MVC Django
Environnement	Ubuntu / Docker / Docker Compose
Versionning	Git / GitHub

GLOSSAIRE, DÉFINITIONS ET ABRÉVIATIONS

1.1 Glossaire
Terme	Définition
Tenant	Organisation cliente disposant de son propre espace isolé sur la plateforme.
Pointage	Action d'enregistrement de l'arrivée ou du départ d'un employé via l'application.
Geofencing	Technologie de délimitation d'une zone géographique virtuelle. Le pointage est refusé si l'utilisateur se trouve hors de cette zone.
PWA	Progressive Web App : application web installable sur un appareil comme une application native.
Multi-Tenant	Architecture logicielle où une seule instance de l'application sert plusieurs organisations clientes de façon complètement isolée.
Super Administrateur	Utilisateur Anthropic disposant des droits globaux sur toute la plateforme SaaS.
Administrateur	Responsable d'une organisation cliente disposant de tous les droits dans son espace.
Manager	Responsable d'équipe pouvant consulter et valider les présences des membres de son équipe.
Horaire fixe	Plage horaire identique chaque jour (ex : 08h00–17h00).
Horaire par équipe	Organisation par rotation : équipe matin, soir, nuit.
Horaire personnalisé	Plage horaire spécifique à un individu ou à un créneau donné.
Agence	Entité géographique appartenant à une organisation, possédant ses propres coordonnées GPS et horaires.
Rayon GPS	Distance en mètres définissant le périmètre autorisé autour des coordonnées d'une agence.
Mode hors ligne	Fonctionnement de l'application sans connexion Internet avec synchronisation différée.
Service Worker	Script JavaScript s'exécutant en arrière-plan dans le navigateur, permettant le fonctionnement hors ligne et les notifications push.
Justificatif	Document fourni par l'employé pour expliquer une absence ou un retard.
Retard	Arrivée au-delà de l'heure prévue, calculée automatiquement par le système.
Départ anticipé	Départ avant la fin de la plage horaire prévue.
Heures supplémentaires	Heures effectuées au-delà de la plage horaire définie.
OWASP	Open Web Application Security Project : référentiel de sécurité pour les applications web.
ASVS	Application Security Verification Standard : standard de vérification de la sécurité applicative.
KPI	Key Performance Indicator : indicateur clé de performance.
Audit Trail	Journal complet et inaltérable de toutes les actions effectuées dans le système.
IAM	Identity and Access Management : gestion des identités et des accès.
2FA	Authentification à deux facteurs.
RBAC	Role-Based Access Control : contrôle d'accès basé sur les rôles.
API REST	Interface de programmation suivant le style architectural REST.
ORM	Object-Relational Mapping : couche d'abstraction entre le code Python et la base de données MySQL.
CDN	Content Delivery Network : réseau de distribution de contenu pour optimiser les performances.
CSRF	Cross-Site Request Forgery : attaque forçant un utilisateur à effectuer des actions non désirées.
XSS	Cross-Site Scripting : injection de scripts malveillants dans une page web.
SQL Injection	Attaque consistant à insérer du code SQL malveillant dans une requête.

1.2 Abréviations
Abréviation	Signification
CDC	Cahier Des Charges
RH	Ressources Humaines
SI	Système d'Information
UX/UI	User Experience / User Interface
BDD	Base De Données
MVP	Minimum Viable Product
SLA	Service Level Agreement
NF	Non Fonctionnel
FC	Fonctionnel et Comportemental
GPS	Global Positioning System
IP	Internet Protocol
URL	Uniform Resource Locator
UUID	Universally Unique Identifier

1.3 Hypothèses
    • La plateforme sera hébergée sur un serveur Linux Ubuntu avec Docker.
    • Chaque organisation (tenant) dispose d'un sous-domaine ou d'un espace identifié.
    • Les employés disposent d'un smartphone avec GPS, caméra et accès Internet (connexion non garantie en permanence).
    • Les navigateurs supportés sont les versions récentes de Chrome, Firefox, Safari et Edge.
    • L'organisation cliente est responsable de la validité des données (horaires, employés, zones GPS).
    • Le Super Administrateur est un employé de l'entreprise éditrice de la plateforme.
    • Les fonctionnalités IA dépendent de la disponibilité de l'API du fournisseur IA configuré.

1.4 Limites du projet — Hors périmètre (V1)
    • Intégration avec des logiciels de paie tiers (prévu en V2).
    • Gestion de la paie ou des salaires.
    • Application mobile native iOS/Android (la PWA couvre ce besoin).
    • Module de vidéosurveillance.
    • Reconnaissance faciale automatique (la photo est capturée pour contrôle humain).
    • Intégration avec des systèmes de badgeage physique (RFID, NFC).
    • Module de facturation et de paiement en ligne (prévu, non développé en V1).

PRÉSENTATION DU PROJET

2.1 Contexte et vision
La gestion de la présence du personnel constitue un enjeu stratégique pour toute organisation. Les systèmes traditionnels (pointeuses physiques, feuilles de présence papier, tableurs) souffrent de limitations majeures : fraude (pointage par procuration), absence de traçabilité géographique, impossibilité de gérer des équipes dispersées sur plusieurs sites, et faible capacité d'analyse.
La présente plateforme SaaS répond à ces problématiques en offrant une solution intelligente, sécurisée, multi-site et multi-organisation, accessible depuis n'importe quel appareil connecté à Internet.
Le système s'appuie sur trois piliers fondamentaux :
    • La géolocalisation GPS pour garantir la présence physique de l'employé dans la zone autorisée.
    • La photo obligatoire prise en temps réel via la caméra pour prévenir la fraude.
    • L'intelligence artificielle pour analyser les données, détecter les anomalies et fournir des recommandations.

2.2 Types d'organisations cibles
Type d'organisation	Particularités
Entreprises	PME, grandes entreprises, multinationales avec gestion des présences des employés.
Établissements scolaires	Écoles primaires, collèges, lycées avec gestion des enseignants par créneau horaire.
Universités	Gestion des enseignants-chercheurs avec emplois du temps complexes.
Restaurants	Gestion des équipes avec horaires décalés, coupures, services multiples.
Pharmacies	Personnel en roulement avec horaires stricts et réglementation.
Cliniques et hôpitaux	Personnel médical avec horaires de nuit, gardes, astreintes.
ONG	Organisations à but non lucratif avec bénévoles et salariés.
Administrations publiques	Fonctionnaires avec règles de présence réglementaires.
Associations	Structures avec membres actifs et permanents.
Autres	Toute organisation disposant d'employés, agents ou intervenants à gérer.

2.3 Architecture Multi-Tenant
La plateforme est conçue selon une architecture Multi-Tenant stricte. Chaque organisation (tenant) possède son propre espace de données complètement isolé du reste de la plateforme.
2.3.1 Isolation des données
L'isolation est assurée à plusieurs niveaux :
    • Niveau base de données : chaque enregistrement est associé à un tenant_id. Toutes les requêtes SQL incluent systématiquement ce filtre comme contrainte obligatoire.
    • Niveau application : le middleware Django valide le tenant actif à chaque requête. Toute tentative d'accès à un autre tenant déclenche une erreur 403.
    • Niveau session : la session utilisateur est liée à un tenant unique. Il est impossible de naviguer entre deux tenants avec la même session.
    • Niveau fichiers : les fichiers uploadés (photos, logos, documents) sont stockés dans des répertoires séparés par tenant.
2.3.2 Identification du tenant
Chaque tenant est identifié par :
    • Un identifiant unique (UUID) généré à la création.
    • Un slug unique (ex : entreprise-abc) utilisé dans les URLs.
    • Un sous-domaine ou un chemin d'URL dédié.
2.3.3 Super Administrateur
Le Super Administrateur est le seul utilisateur qui opère en dehors du contexte tenant. Il dispose d'une interface dédiée lui permettant de gérer l'ensemble des organisations sans jamais accéder directement aux données opérationnelles (employés, pointages, documents) d'un tenant.

ACTEURS ET RESPONSABILITÉS

3.1 Super Administrateur
Le Super Administrateur est l'administrateur global de la plateforme SaaS. Il n'appartient à aucun tenant et n'accède jamais aux données opérationnelles des organisations.

3.1.1 Droits et responsabilités
    • Créer une nouvelle organisation (tenant) avec toutes ses informations initiales.
    • Modifier les informations d'une organisation existante.
    • Suspendre temporairement une organisation (accès bloqué pour tous les utilisateurs du tenant).
    • Réactiver une organisation suspendue.
    • Supprimer définitivement une organisation après confirmation explicite et sauvegarde obligatoire des données.
    • Gérer les abonnements et les plans tarifaires (module prévu, non développé en V1, interface en place).
    • Consulter les statistiques globales de la plateforme (nombre d'organisations, d'utilisateurs, de pointages, etc.).
    • Consulter les journaux d'audit globaux de la plateforme.
    • Gérer les paramètres globaux du système (langue par défaut, fuseau horaire par défaut, politiques de sécurité globales).
    • Gérer les modèles et fournisseurs IA disponibles pour les tenants.
    • Gérer les sauvegardes globales de la plateforme.
    • Accéder aux journaux système et aux alertes techniques.
3.1.2 Restrictions
    • Il ne peut pas créer, modifier ou supprimer des employés appartenant à un tenant.
    • Il ne peut pas consulter les pointages, absences ou congés des employés d'un tenant.
    • Il ne peut pas accéder aux documents des employés.
    • Toutes ses actions sont enregistrées dans le journal d'audit global.

3.2 Administrateur d'Organisation
L'Administrateur d'Organisation est le responsable de son propre tenant. Il dispose de tous les droits à l'intérieur de son organisation, sans pouvoir accéder à d'autres organisations.

3.2.1 Gestion de l'organisation
    • Personnaliser le logo de l'organisation.
    • Personnaliser les couleurs de l'interface (couleur primaire, secondaire).
    • Modifier les informations légales et de contact de l'organisation.
    • Configurer le fuseau horaire, la langue et les formats date/heure.
    • Configurer les paramètres GPS (rayon par défaut, tolérance).
    • Configurer les paramètres de pointage (tolérance retard, seuil heures sup., etc.).
    • Configurer les paramètres IA de l'organisation.
    • Configurer les notifications de l'organisation.
3.2.2 Gestion des structures
    • Créer, modifier, activer et désactiver des agences.
    • Créer, modifier et désactiver des départements.
    • Créer, modifier et désactiver des postes.
    • Créer des comptes managers et superviseurs.
    • Affecter des managers à des équipes ou des départements.
3.2.3 Gestion des ressources humaines
    • Créer, modifier, activer, suspendre et archiver des comptes employés.
    • Affecter les employés à des agences, départements et postes.
    • Gérer les horaires de travail (création, modification, affectation).
    • Gérer les plannings et emplois du temps.
    • Gérer les congés (création des types, validation des demandes).
    • Gérer les jours fériés de l'organisation.
    • Valider ou rejeter les justificatifs d'absence.
3.2.4 Consultation et reporting
    • Consulter en temps réel les présences de tous les employés.
    • Consulter l'historique complet des pointages.
    • Consulter les statistiques détaillées par employé, département, agence.
    • Exporter les rapports en PDF, Excel et CSV.
    • Importer des données (employés, horaires) via fichiers CSV/Excel.
    • Consulter les journaux d'audit de son organisation.
3.2.5 Gestion des annonces
    • Créer et publier des annonces internes.
    • Cibler les annonces par agence, département ou groupe d'employés.
    • Programmer la publication et l'expiration des annonces.

3.3 Manager
Le Manager gère uniquement les équipes qui lui sont affectées. Ses droits sont strictement limités à son périmètre.

3.3.1 Droits du Manager
    • Consulter les présences en temps réel de son équipe.
    • Consulter l'historique des pointages de son équipe.
    • Consulter les absences et retards de son équipe.
    • Approuver ou rejeter les demandes de congé de son équipe (si l'Administrateur lui a délégué ce droit).
    • Valider les justificatifs d'absence de son équipe.
    • Consulter les statistiques de son équipe.
    • Recevoir des alertes (absence, retard, anomalie) concernant son équipe.
    • Envoyer des notifications à son équipe.
3.3.2 Restrictions du Manager
    • Il ne peut pas créer ni modifier des comptes employés.
    • Il ne peut pas accéder aux données des employés hors de son équipe.
    • Il ne peut pas modifier les paramètres de l'organisation.
    • Il ne peut pas exporter des données globales.

3.4 Superviseur
Le Superviseur est un rôle intermédiaire entre le Manager et l'Administrateur. Ses droits sont configurables par l'Administrateur selon les besoins de l'organisation.

3.4.1 Droits configurables du Superviseur
    • Consulter les présences de plusieurs équipes ou d'un département entier.
    • Consulter les statistiques d'un département.
    • Valider les justificatifs et demandes de congé d'un département.
    • Générer des rapports pour son périmètre.
    • Recevoir des alertes pour son périmètre.

3.5 Employé
L'Employé est l'utilisateur final de l'application. Il interagit principalement via l'interface de pointage et son tableau de bord personnel.

3.5.1 Droits de l'Employé
    • Se connecter à son compte sécurisé.
    • Modifier certaines informations personnelles (photo de profil, numéro de téléphone, langue d'affichage).
    • Effectuer un pointage d'arrivée dans les conditions définies.
    • Effectuer un pointage de départ dans les conditions définies.
    • Consulter son historique complet de pointages.
    • Consulter ses statistiques personnelles (taux de présence, retards cumulés, etc.).
    • Consulter ses absences et justifications.
    • Déposer une demande de congé.
    • Déposer un justificatif d'absence.
    • Consulter le statut de ses demandes.
    • Consulter les annonces de son organisation.
    • Interagir avec l'assistant IA selon les permissions accordées par l'Administrateur.
3.5.2 Restrictions de l'Employé
    • Il ne peut pas modifier ses horaires de travail.
    • Il ne peut pas accéder aux données des autres employés.
    • Il ne peut pas modifier ses présences a posteriori sans validation.
    • Il ne peut pas utiliser une photo de galerie pour le pointage.

TECHNOLOGIES ET ARCHITECTURE TECHNIQUE

4.1 Stack technologique
Composant	Technologie
Backend	Python 3.11+ avec le framework Django (LTS)
Frontend	Django Templates, HTML5, CSS3, Bootstrap 5.3, JavaScript ES6+
Base de données	MySQL 8.0 avec moteur InnoDB
ORM	Django ORM (abstraction complète de MySQL)
Cache	Redis (sessions, cache applicatif, files de tâches)
File d'attente	Celery + Redis (traitement asynchrone, notifications, exports)
Serveur web	Nginx (reverse proxy) + Gunicorn (WSGI)
Environnement	Ubuntu 22.04 LTS
Conteneurisation	Docker 24+ et Docker Compose
Versionning	Git avec GitHub
CI/CD	GitHub Actions (recommandé)
Stockage fichiers	Stockage local avec possibilité d'extension vers S3/MinIO

4.2 Architecture MVC Django
L'application suit strictement le patron architectural MVT (Model-View-Template) de Django, équivalent au MVC :
    • Model : définition des entités de données, des relations et des contraintes métier via l'ORM Django.
    • View : logique applicative et traitement des requêtes HTTP. Les vues sont organisées en Class-Based Views (CBV) pour favoriser la réutilisabilité.
    • Template : rendu HTML via le moteur de templates Django avec héritage de templates.
La structure du projet Django est organisée en applications (apps) Django indépendantes, chacune responsable d'un domaine fonctionnel précis. Cette modularité facilite la maintenance et l'évolution.
4.3 Architecture Multi-Tenant
4.3.1 Approche retenue : Shared Database, Shared Schema
L'architecture multi-tenant retenue est du type 'base de données partagée, schéma partagé'. Toutes les organisations partagent la même base de données MySQL et les mêmes tables, avec une colonne tenant_id (ou organisation_id) présente sur toutes les tables métier.
4.3.2 Justification du choix
    • Maintenance simplifiée : une seule base de données à administrer et sauvegarder.
    • Coût d'infrastructure réduit par rapport à une base de données par tenant.
    • Migrations de schéma appliquées une seule fois pour tous les tenants.
    • Isolation assurée par le middleware applicatif Django et les contraintes de requêtes.
4.3.3 Middleware Tenant
Un middleware Django personnalisé intercepte chaque requête HTTP et :
    1. Identifie le tenant actif à partir de l'URL, du sous-domaine ou de la session.
    2. Injecte le tenant dans le contexte de la requête (request.tenant).
    3. Configure un manager Django personnalisé qui filtre automatiquement toutes les requêtes ORM avec le tenant actif.
    4. Rejette toute requête dont le tenant est introuvable ou suspendu.
4.4 Progressive Web App (PWA)
L'application est conçue dès le départ pour fonctionner comme une PWA complète. Les fichiers requis sont :
    • manifest.json : définition de l'icône, nom, couleurs, orientation et mode d'affichage (standalone).
    • service-worker.js : gestion du cache, du mode hors ligne, des notifications push.
    • HTTPS obligatoire : les PWA nécessitent une connexion sécurisée.
4.5 Responsive Design
L'interface est conçue en mobile-first avec Bootstrap 5. Les points de rupture (breakpoints) suivants sont utilisés :
Breakpoint	Usage
xs	< 576px — Smartphones en mode portrait
sm	576px – 767px — Smartphones en mode paysage
md	768px – 991px — Tablettes
lg	992px – 1199px — Petits écrans desktop
xl	≥ 1200px — Grands écrans desktop

MODULE AUTHENTIFICATION

5.1 Description générale
Le module d'authentification est le point d'entrée de toute la plateforme. Il gère la connexion, la déconnexion, la gestion des sessions, la réinitialisation des mots de passe et la sécurisation des accès. Ce module est critique car il constitue la première ligne de défense contre les accès non autorisés.
5.2 Connexion
5.2.1 Description détaillée
La page de connexion est accessible à l'URL /login/ (ou /[tenant-slug]/login/ selon la configuration). Elle affiche un formulaire simple demandant l'identifiant (adresse e-mail) et le mot de passe.
5.2.2 Préconditions
    • L'utilisateur dispose d'un compte actif dans le système.
    • L'organisation de l'utilisateur est active (non suspendue).
    • L'utilisateur n'a pas dépassé le nombre maximum de tentatives échouées.
5.2.3 Déroulement normal
    5. L'utilisateur accède à la page de connexion.
    6. Il saisit son adresse e-mail et son mot de passe.
    7. Il clique sur le bouton 'Se connecter'.
    8. Le système vérifie l'existence du compte associé à l'e-mail.
    9. Le système vérifie que le compte est actif.
    10. Le système vérifie que l'organisation est active.
    11. Le système vérifie le mot de passe avec l'algorithme de hachage bcrypt/Argon2.
    12. Le système crée une session sécurisée.
    13. Le système enregistre l'événement de connexion dans le journal d'audit.
    14. Le système redirige l'utilisateur vers son tableau de bord selon son rôle.
5.2.4 Scénarios alternatifs
    • E-mail inconnu : message générique 'Identifiants incorrects' (ne pas révéler si l'e-mail existe).
    • Mot de passe incorrect : incrémentation du compteur de tentatives, message générique.
    • Compte inactif ou suspendu : message 'Votre compte est suspendu. Contactez votre administrateur.'
    • Organisation suspendue : message 'Votre organisation est temporairement suspendue.'
    • Première connexion : redirection vers la page de changement de mot de passe obligatoire.
    • Session déjà active : l'utilisateur est redirigé directement vers son tableau de bord.
5.2.5 Règles métier
    • L'identifiant de connexion est l'adresse e-mail. Les noms d'utilisateur textuels ne sont pas supportés.
    • La comparaison de l'e-mail est insensible à la casse.
    • Le mot de passe est sensible à la casse.
    • Après 5 tentatives échouées consécutives, le compte est temporairement verrouillé.
    • La durée de verrouillage est configurable par l'Administrateur (défaut : 15 minutes).
    • Un e-mail de notification est envoyé à l'utilisateur en cas de verrouillage.
    • Le CAPTCHA s'affiche automatiquement après 3 tentatives échouées.
    • Toutes les tentatives (réussies ou non) sont enregistrées dans le journal d'audit.

5.3 Déconnexion
5.3.1 Description
La déconnexion peut être initiée par l'utilisateur ou déclenchée automatiquement par le système.
5.3.2 Déconnexion manuelle
    15. L'utilisateur clique sur 'Se déconnecter' dans le menu.
    16. Le système invalide la session côté serveur.
    17. Le système supprime le cookie de session.
    18. Le système enregistre l'événement dans le journal.
    19. L'utilisateur est redirigé vers la page de connexion.
5.3.3 Déconnexion automatique
    • Après inactivité : déconnexion automatique après N minutes d'inactivité (N configurable, défaut 30 min).
    • Expiration de session : déconnexion après la durée maximale de session (défaut : 8 heures).
    • Déconnexion de toutes les sessions : l'utilisateur ou l'Administrateur peut invalider toutes les sessions actives d'un compte.

5.4 Réinitialisation du mot de passe
5.4.1 Déroulement
    20. L'utilisateur clique sur 'Mot de passe oublié'.
    21. Il saisit son adresse e-mail.
    22. Le système vérifie si l'e-mail existe (sans le révéler explicitement).
    23. Le système génère un token unique à usage unique avec expiration (30 minutes).
    24. Le système envoie un e-mail contenant le lien de réinitialisation sécurisé.
    25. L'utilisateur clique sur le lien dans l'e-mail.
    26. Le système vérifie la validité du token (non expiré, non utilisé).
    27. L'utilisateur saisit et confirme son nouveau mot de passe.
    28. Le système vérifie la conformité du mot de passe aux règles de complexité.
    29. Le système vérifie que le nouveau mot de passe n'est pas identique aux N derniers mots de passe.
    30. Le système met à jour le mot de passe hashé.
    31. Le système invalide tous les tokens de réinitialisation existants pour ce compte.
    32. Le système invalide toutes les sessions actives du compte.
    33. Le système enregistre l'événement dans le journal.
5.4.2 Règles de sécurité
    • Le token de réinitialisation est un UUID v4 à usage unique.
    • Le token expire après 30 minutes (configurable).
    • Un seul token valide peut exister à la fois par compte.
    • L'e-mail de réinitialisation ne révèle jamais si l'e-mail existe dans le système.
    • Le lien de réinitialisation est en HTTPS uniquement.

5.5 Première connexion
Lors de la création d'un compte par l'Administrateur, un mot de passe temporaire aléatoire est généré automatiquement et envoyé à l'utilisateur par e-mail. Lors de la première connexion, l'utilisateur est obligatoirement redirigé vers une page de changement de mot de passe. Il ne peut accéder à aucune autre fonctionnalité tant qu'il n'a pas défini un nouveau mot de passe personnel conforme aux règles de complexité.
5.6 Gestion des sessions
5.6.1 Caractéristiques des sessions
    • Stockage : sessions stockées côté serveur dans Redis (pas dans les cookies).
    • Identifiant : cookie httpOnly, Secure, SameSite=Strict avec valeur aléatoire.
    • Durée : configurable par l'Administrateur (défaut : 8 heures pour les employés, 2 heures pour les Administrateurs).
    • Inactivité : expiration après N minutes d'inactivité (défaut : 30 min).
5.6.2 Sessions actives
Chaque utilisateur peut consulter la liste de ses sessions actives depuis son profil. Pour chaque session, le système affiche :
    • Appareil (type et système d'exploitation détectés via l'user-agent).
    • Navigateur.
    • Adresse IP.
    • Date et heure de connexion.
    • Dernière activité.
    • Localisation approximative (basée sur IP, si disponible).
L'utilisateur peut révoquer n'importe quelle session distante. L'Administrateur peut révoquer toutes les sessions d'un utilisateur.

MODULE GESTION DES ORGANISATIONS

6.1 Description générale
Ce module permet au Super Administrateur de créer et gérer les organisations clientes (tenants). Chaque organisation est un espace totalement isolé avec ses propres données, paramètres et utilisateurs.
6.2 Création d'une organisation
6.2.1 Informations requises
Champ	Description
Nom légal	Dénomination sociale officielle de l'organisation. Obligatoire.
Nom commercial	Nom d'affichage dans l'application. Obligatoire.
Slug	Identifiant URL unique (lettres minuscules, chiffres, tirets). Généré automatiquement, modifiable.
Type d'organisation	Entreprise, École, Université, Restaurant, Pharmacie, Clinique, ONG, Administration, Association, Autre.
Secteur d'activité	Secteur économique (liste prédéfinie + champ libre).
Pays	Pays d'implantation principale.
Ville	Ville du siège principal.
Adresse	Adresse complète du siège.
Code postal	Code postal.
Téléphone	Numéro de téléphone principal.
E-mail	E-mail de contact principal.
Site web	URL du site web (optionnel).
Nombre d'employés	Fourchette indicative (< 10, 10–50, 50–200, 200–500, > 500).
Fuseau horaire	Fuseau horaire de référence (liste complète IANA).
Langue par défaut	Langue d'interface (Français, Anglais, Arabe).
Format date	DD/MM/YYYY ou MM/DD/YYYY ou YYYY-MM-DD.
Format heure	12h ou 24h.
Logo	Fichier image (PNG/JPG, max 2 Mo, dimensions min. 200x200px).
Couleur primaire	Code hexadécimal couleur principale de la charte graphique.
Couleur secondaire	Code hexadécimal couleur secondaire.
Nom Administrateur	Nom complet du premier Administrateur de l'organisation.
E-mail Administrateur	E-mail du premier Administrateur (recevra les accès par e-mail).
Téléphone Administrateur	Numéro de téléphone du premier Administrateur.

6.2.2 Règles de validation
    • Le nom légal ne peut pas être vide et doit contenir au moins 2 caractères.
    • Le slug doit être unique sur l'ensemble de la plateforme.
    • L'e-mail de l'Administrateur doit être valide et unique sur la plateforme.
    • Le logo doit respecter les formats PNG ou JPG uniquement.
    • La couleur hexadécimale doit être un code valide (#RRGGBB).
    • Le fuseau horaire doit appartenir à la liste IANA officielle.
6.2.3 Actions post-création
    • Création automatique de l'espace tenant dans la base de données.
    • Création du compte Administrateur principal avec mot de passe temporaire.
    • Envoi d'un e-mail de bienvenue à l'Administrateur avec ses accès.
    • Création des paramètres par défaut de l'organisation.
    • Enregistrement dans le journal d'audit.

6.3 États d'une organisation
État	Comportement du système
Active	L'organisation fonctionne normalement. Tous les utilisateurs peuvent se connecter.
Suspendue	Accès bloqué pour tous les utilisateurs du tenant. Le Super Admin peut réactiver.
Expirée	Abonnement expiré (module V2). Accès limité en lecture seule.
Supprimée	Organisation archivée et désactivée définitivement.

6.4 Paramètres de l'organisation
6.4.1 Paramètres généraux
    • Logo (redimensionné automatiquement à 300x300px pour l'affichage).
    • Couleurs de l'interface (primaire, secondaire, couleur d'accentuation).
    • Langue d'interface par défaut.
    • Fuseau horaire.
    • Format date et heure.
    • Informations légales (numéro SIRET/RC, numéro TVA, etc.).
6.4.2 Paramètres de pointage
    • Tolérance de retard : nombre de minutes de grâce avant de comptabiliser un retard (défaut : 5 min).
    • Tolérance de départ anticipé : nombre de minutes acceptées avant l'heure de fin (défaut : 5 min).
    • Seuil heures supplémentaires : nombre de minutes au-delà desquelles les heures sont comptabilisées en heures sup.
    • Pointage hors ligne autorisé : Oui/Non.
    • Délai maximum de synchronisation hors ligne : durée maximale acceptable (défaut : 48h).
    • Obligation de photo : Oui/Non (Oui par défaut, non désactivable en V1).
    • Rayon GPS par défaut : en mètres, appliqué si l'agence n'a pas son propre rayon.
6.4.3 Paramètres de sécurité
    • Durée de session (en heures).
    • Durée d'inactivité avant déconnexion (en minutes).
    • Nombre de tentatives avant blocage (défaut : 5).
    • Durée de blocage (en minutes, défaut : 15).
    • Longueur minimale du mot de passe (défaut : 8).
    • Expiration du mot de passe (en jours, défaut : 90).
    • Historique des mots de passe (nombre de mots de passe mémorisés, défaut : 5).

MODULE GESTION DES AGENCES

7.1 Description générale
Une organisation peut disposer d'une ou plusieurs agences (sites géographiques). Chaque agence représente un lieu physique où les employés exercent leur activité. L'agence est l'unité de base du geofencing : c'est à partir de ses coordonnées GPS que le système détermine si un employé est autorisé à pointer.
7.2 Modèle de données d'une agence
Champ	Description
Nom	Nom de l'agence (ex : Siège Social, Agence Paris Nord, Agence Casablanca).
Code	Code court unique au sein de l'organisation (ex : SG, APN, ACB).
Type	Siège, Agence, Filiale, Entrepôt, Chantier, etc.
Adresse	Adresse complète.
Ville	Ville.
Pays	Pays.
Téléphone	Numéro de téléphone de l'agence.
E-mail	E-mail de contact de l'agence.
Responsable	Employé désigné comme responsable de l'agence.
Latitude	Coordonnée GPS — latitude (décimale, 6 décimales min).
Longitude	Coordonnée GPS — longitude (décimale, 6 décimales min).
Rayon GPS	Rayon du geofencing en mètres (min : 50m, max : 5000m, défaut : 200m).
Zones supplémentaires	Liste d'autres coordonnées GPS + rayon autorisés pour cette agence.
Horaires	Horaires de fonctionnement de l'agence (distinct des horaires individuels).
Statut	Active / Inactive.
Pointage hors ligne	Autorisation du pointage hors ligne spécifique à cette agence.
Photo de l'agence	Photo du lieu pour identification visuelle.
Notes	Notes internes.

7.3 Règles métier des agences
    • Chaque organisation doit disposer d'au moins une agence.
    • Une agence désactivée n'accepte plus aucun pointage.
    • Les employés affectés à une agence désactivée doivent être réaffectés avant la désactivation.
    • Les coordonnées GPS doivent être obtenues via un outil de géolocalisation (carte intégrée recommandée dans l'interface d'administration).
    • Le rayon GPS minimum est de 50 mètres pour tenir compte de la précision des GPS de smartphones.
    • Une agence peut disposer de zones supplémentaires (ex : parking, annexe) en plus de sa zone principale.
    • La suppression d'une agence est impossible si elle contient des pointages historiques. Elle doit être archivée.
7.4 Détermination automatique des coordonnées GPS
L'interface d'administration intègre une carte interactive (basée sur OpenStreetMap/Leaflet ou Google Maps selon la configuration) permettant à l'Administrateur de :
    • Rechercher une adresse et obtenir automatiquement les coordonnées GPS.
    • Placer un marqueur sur la carte pour définir le centre de la zone.
    • Visualiser le cercle de geofencing en temps réel lors de l'ajustement du rayon.
    • Ajuster manuellement les coordonnées si nécessaire.

MODULE GÉOREPÉRAGE (GEOFENCING)

8.1 Description et fonctionnement
Le géorepérage est une fonctionnalité centrale de la plateforme. Il permet de définir des zones géographiques virtuelles à l'intérieur desquelles les pointages sont autorisés. Tout pointage tenté depuis l'extérieur de ces zones est automatiquement refusé.
8.2 Algorithme de calcul de distance
La distance entre la position de l'employé et le centre de la zone autorisée est calculée en utilisant la formule de Haversine, qui tient compte de la courbure de la Terre et offre une précision suffisante pour des distances de l'ordre de quelques centaines de mètres.
Formule Haversine : d = 2R × arcsin(√(sin²((φ2−φ1)/2) + cos(φ1) × cos(φ2) × sin²((λ2−λ1)/2))) où R = 6371 km, φ = latitude en radians, λ = longitude en radians.

8.3 Vérification de la zone autorisée
    34. Le navigateur demande la permission de géolocalisation à l'utilisateur.
    35. Si la permission est refusée, le pointage est immédiatement bloqué avec message explicatif.
    36. Le navigateur obtient les coordonnées GPS actuelles de l'utilisateur (précision demandée : haute précision enableHighAccuracy = true).
    37. Le système calcule la distance entre la position de l'employé et chaque zone autorisée de son agence.
    38. Si la distance est inférieure ou égale au rayon de la zone, le pointage est autorisé.
    39. Si l'employé est affecté à plusieurs agences, le système vérifie toutes les zones de toutes ses agences.
    40. Si aucune zone ne correspond, le pointage est refusé avec message indiquant que l'utilisateur n'est pas dans la zone autorisée.
8.4 Précision GPS et marges de tolérance
Les GPS de smartphones ont une précision variable (de quelques mètres à une centaine de mètres en zone urbaine). Pour tenir compte de cette imprécision, le système applique une marge de tolérance configurable :
    • La précision GPS fournie par le navigateur (accuracy en mètres) est enregistrée avec le pointage.
    • Une marge de tolérance globale configurable (défaut : 30 mètres) est ajoutée au rayon de la zone.
    • Le rayon effectif = rayon configuré + marge de tolérance.
    • La précision GPS et la marge de tolérance appliquée sont enregistrées dans les logs du pointage.
8.5 Zones multiples
Une agence peut définir plusieurs zones autorisées pour couvrir des configurations complexes :
    • Zone principale : entrée du bâtiment / lieu de travail principal.
    • Zones secondaires : parkings, annexes, espaces extérieurs.
    • Le pointage est autorisé dès qu'il se trouve dans l'une des zones définies.
8.6 Cas particuliers liés au GPS
Cas	Comportement du système
GPS désactivé	Pointage immédiatement refusé. Message : 'Activez votre GPS pour pointer.' Lien vers les paramètres si possible.
Permission refusée	Pointage immédiatement refusé. Message explicatif avec instructions pour accorder la permission.
Précision insuffisante (>100m)	Avertissement affiché. Le pointage est enregistré avec flag 'précision faible' pour contrôle ultérieur.
Hors zone	Pointage refusé. La distance calculée et la distance autorisée sont affichées à l'employé.
GPS simulé/falsifié	Le système détecte les GPS simulés via l'attribut isMock de l'API de géolocalisation. Le pointage est refusé et une alerte est générée pour l'Administrateur.
Zone inondée / chantier	L'Administrateur peut ajouter temporairement une zone supplémentaire ou augmenter le rayon.
Travail sur plusieurs sites	L'employé est affecté à plusieurs agences. Toutes les zones sont vérifiées.
Travail à domicile	Une agence 'Télétravail' peut être créée avec les coordonnées du domicile de l'employé (déclaration sur l'honneur).

MODULE POINTAGE — CŒUR DU SYSTÈME

9.1 Description générale
Le module de pointage est le cœur fonctionnel de la plateforme. Il permet à chaque employé d'enregistrer son arrivée et son départ avec une traçabilité complète : photo en temps réel, géolocalisation GPS, horodatage précis et informations techniques de l'appareil.
Le pointage est conçu pour être à la fois simple pour l'utilisateur (deux clics maximum) et rigoureux sur le plan de la sécurité et de l'authenticité.
9.2 Flux de vérifications pré-pointage
Avant d'autoriser le pointage, le système effectue une série de vérifications dans l'ordre suivant. Si l'une d'elles échoue, le pointage est refusé et l'employé reçoit un message explicite :
N°	Vérification	Message en cas d'échec
Vérif. 1	Utilisateur authentifié	Session valide présente. Sinon : redirection vers login.
Vérif. 2	Compte utilisateur actif	Statut = Actif. Sinon : message 'Compte suspendu'.
Vérif. 3	Organisation active	Tenant non suspendu. Sinon : message 'Organisation suspendue'.
Vérif. 4	Employé actif	Statut employé = Actif. Sinon : message 'Compte employé inactif'.
Vérif. 5	GPS activé	navigator.geolocation disponible et activé. Sinon : message + lien paramètres.
Vérif. 6	Permission localisation	Permission accordée par l'utilisateur. Sinon : instructions d'activation.
Vérif. 7	Permission caméra	Accès caméra accordé. Sinon : instructions d'activation.
Vérif. 8	Zone GPS autorisée	Distance ≤ rayon effectif. Sinon : affichage distance et zone requise.
Vérif. 9	Horaire valide	Pointage dans la fenêtre temporelle autorisée. Sinon : message horaire.
Vérif. 10	Pas de doublon	Pas de pointage identique dans les N dernières minutes (configurable).

9.3 Processus de pointage étape par étape
9.3.1 Étape 1 — Déclenchement
L'employé accède à la page de pointage depuis son tableau de bord. Un bouton distinct est affiché selon le contexte : 'Pointer mon arrivée' ou 'Pointer mon départ'. Le bouton approprié est affiché automatiquement selon le dernier pointage enregistré.
9.3.2 Étape 2 — Géolocalisation
Dès que l'employé clique sur le bouton, le système :
    41. Demande la permission de géolocalisation si elle n'est pas encore accordée.
    42. Acquiert les coordonnées GPS avec enableHighAccuracy: true.
    43. Affiche un indicateur de chargement pendant l'acquisition (timeout : 15 secondes).
    44. Vérifie que l'employé est dans la zone autorisée.
9.3.3 Étape 3 — Activation de la caméra
Si la vérification GPS est réussie, le système active automatiquement la caméra frontale. Un aperçu en temps réel est affiché à l'écran. La galerie photo est strictement interdite : seule la caméra en direct est utilisée (constraint : { video: { facingMode: 'user' } }).
9.3.4 Étape 4 — Capture de la photo
L'employé voit son visage en temps réel. Il clique sur 'Prendre la photo' ou la photo est capturée automatiquement après un compte à rebours de 3 secondes (configurable). La photo est capturée en JPEG, qualité 0.85, résolution maximum 640x480px. La photo n'est jamais sauvegardée dans la galerie du téléphone.
9.3.5 Étape 5 — Confirmation et envoi
L'employé voit un aperçu de la photo capturée. Il peut recommencer la capture s'il le souhaite. Il clique sur 'Confirmer le pointage'. Les données sont envoyées au serveur via HTTPS en POST (format multipart/form-data).
9.3.6 Étape 6 — Enregistrement
Le serveur reçoit et traite les données :
    45. Re-validation côté serveur de toutes les vérifications (sécurité défense en profondeur).
    46. Calcul du statut (À l'heure, Retard, Départ anticipé, Heures supplémentaires).
    47. Enregistrement en base de données.
    48. Envoi des notifications si nécessaire (retard détecté, etc.).
    49. Retour de confirmation JSON à l'interface.
9.3.7 Étape 7 — Confirmation à l'employé
L'interface affiche un message de confirmation avec l'heure enregistrée. En cas d'erreur serveur, le pointage est mis en file d'attente hors ligne si le mode offline est activé.

9.4 Données enregistrées par pointage
Champ	Description
id	Identifiant unique UUID du pointage.
tenant_id	Organisation concernée.
employe_id	Employé ayant effectué le pointage.
agence_id	Agence de référence du pointage.
type_pointage	ARRIVEE ou DEPART.
date_pointage	Date du pointage (YYYY-MM-DD).
heure_pointage	Heure exacte du pointage côté serveur (HH:MM:SS.ms).
heure_client	Heure fournie par le navigateur client (peut différer du serveur).
latitude	Latitude GPS au moment du pointage (6 décimales).
longitude	Longitude GPS au moment du pointage (6 décimales).
precision_gps	Précision GPS en mètres fournie par le navigateur.
adresse_approx	Adresse obtenue par géocodage inverse (facultatif, asynchrone).
photo	Chemin vers la photo capturée (stockage sécurisé).
adresse_ip	Adresse IP du client.
user_agent	User-agent complet du navigateur.
appareil	Appareil détecté (Mobile, Tablette, Desktop).
navigateur	Navigateur détecté (Chrome, Firefox, etc.).
os	Système d'exploitation détecté.
heure_prevue	Heure planifiée selon l'horaire affecté.
retard_minutes	Nombre de minutes de retard (null si aucun retard).
depart_anticipe_min	Nombre de minutes de départ anticipé (null si aucun).
heures_supp_min	Nombre de minutes d'heures supplémentaires (null si aucune).
statut	A_LHEURE, RETARD, DEPART_ANTICIPE, HORS_HORAIRE, EN_ATTENTE_VALIDATION.
mode	EN_LIGNE ou HORS_LIGNE.
sync_at	Date/heure de synchronisation (si pointage hors ligne).
valide	Booléen : le pointage a-t-il été validé ?
valide_par	Utilisateur ayant validé (Manager ou Admin).
observations	Notes libres saisies par l'employé ou ajoutées par le responsable.
created_at	Horodatage de création en base de données.
updated_at	Horodatage de dernière modification.

9.5 Types de statut de pointage
Statut	Description
A_LHEURE	L'employé a pointé dans la tolérance autorisée autour de l'heure prévue.
RETARD	L'employé a pointé après l'heure prévue + tolérance. Le nombre de minutes de retard est calculé.
DEPART_ANTICIPE	L'employé a pointé son départ avant l'heure de fin prévue − tolérance.
HEURES_SUP	L'employé a pointé son départ après l'heure de fin prévue + seuil.
HORS_HORAIRE	Le pointage a été effectué en dehors de toute plage horaire définie.
EN_ATTENTE_VALIDATION	Pointage hors ligne ou exceptionnel nécessitant une validation manuelle.
VALIDE_MANUELLEMENT	Pointage modifié ou validé manuellement par un Administrateur ou Manager.
REJETE	Pointage refusé ou annulé par un Administrateur.

9.6 Règles métier du pointage
    • Un employé ne peut effectuer qu'un seul pointage d'arrivée et un seul pointage de départ par plage horaire, sauf exception configurée par l'organisation (ex : pause repas).
    • Le pointage d'arrivée doit toujours précéder le pointage de départ sur la même journée.
    • Si un employé tente de pointer deux arrivées consécutives, le système affiche une alerte et demande confirmation.
    • Le calcul du retard est basé sur l'heure serveur, pas sur l'heure client.
    • Un retard est comptabilisé uniquement si le dépassement dépasse la tolérance configurée.
    • La photo est obligatoire. Aucun pointage ne peut être enregistré sans photo.
    • La photo doit provenir de la caméra en direct. Toute photo de galerie est détectée et rejetée.
    • La position GPS est vérifiée côté serveur pour les pointages en ligne.
    • Pour les pointages hors ligne, la vérification GPS est effectuée côté client et re-vérifiée à la synchronisation.
    • Tout pointage modifié manuellement est marqué comme VALIDE_MANUELLEMENT et l'action est enregistrée dans le journal d'audit.

9.7 Pointage hors connexion (Mode Offline)
9.7.1 Principes
L'application doit fonctionner même lorsque la connexion Internet est indisponible. Le Service Worker gère la mise en cache et la synchronisation différée.
9.7.2 Fonctionnement hors ligne
    50. L'employé ouvre l'application sans connexion Internet.
    51. Le Service Worker sert l'interface depuis le cache.
    52. L'employé effectue le pointage normalement (GPS et caméra fonctionnent sans Internet).
    53. Le pointage est stocké localement dans IndexedDB avec toutes les données (photo en base64, GPS, heure réelle).
    54. Un indicateur visuel informe l'employé que le pointage est enregistré hors ligne.
    55. Dès que la connexion est rétablie, le Service Worker synchronise automatiquement tous les pointages en attente.
    56. Le serveur re-valide chaque pointage synchronisé.
    57. L'employé reçoit une confirmation de synchronisation.
9.7.3 Règles de validation à la synchronisation
    • Le délai entre l'heure du pointage et la synchronisation ne doit pas dépasser la durée maximale configurée (défaut : 48h).
    • La vérification GPS est re-calculée côté serveur à partir des coordonnées stockées.
    • Si la vérification échoue à la synchronisation (position hors zone), le pointage est marqué EN_ATTENTE_VALIDATION pour contrôle manuel.
    • Si le délai est dépassé, le pointage est marqué EN_ATTENTE_VALIDATION.
9.7.4 Sécurité du mode hors ligne
    • Les données stockées dans IndexedDB sont chiffrées avec une clé dérivée de la session utilisateur.
    • Les données sont effacées de IndexedDB après synchronisation réussie.
    • En cas de tentative de falsification de l'heure (horloge modifiée manuellement), le serveur détecte l'incohérence et marque le pointage pour validation.

MODULE GESTION DES HORAIRES

10.1 Description générale
La gestion des horaires est un module fondamental qui détermine quand un employé est censé être présent et donc quand son pointage est autorisé. Le système supporte plusieurs types d'horaires pour répondre aux besoins variés des organisations clientes.
10.2 Types d'horaires
10.2.1 Horaires fixes
Un horaire fixe définit une plage de travail identique chaque jour ouvrable. Ce type est le plus courant dans les entreprises classiques.
Exemple : 08h00 → 17h00, du lundi au vendredi. L'employé doit pointer son arrivée avant ou à 08h00 (+ tolérance) et son départ après ou à 17h00 (- tolérance).

Paramètres d'un horaire fixe :
Paramètre	Description
Nom	Nom de l'horaire (ex : Horaire Standard, Horaire Décalé).
Heure de début	Heure de début de travail (HH:MM).
Heure de fin	Heure de fin de travail (HH:MM).
Jours actifs	Sélection des jours de la semaine (Lun, Mar, Mer, Jeu, Ven, Sam, Dim).
Pause déjeuner	Heure de début et fin de pause (optionnel). Si définie, le départ pause et le retour pause peuvent être pointés.
Fenêtre de pointage arrivée	Plage pendant laquelle le pointage d'arrivée est accepté (ex : 30 min avant → 2h après heure de début).
Fenêtre de pointage départ	Plage pendant laquelle le pointage de départ est accepté (ex : 30 min avant → 3h après heure de fin).
Tolérance retard	Minutes de grâce avant de comptabiliser un retard (peut surcharger le paramètre global).
Tolérance départ anticipé	Minutes avant la fin autorisées sans comptabiliser un départ anticipé.
10.2.2 Horaires par équipe (rotation)
Les horaires par équipe permettent de gérer les organisations fonctionnant en rotation (usines, hôpitaux, restaurants, etc.). Plusieurs équipes se succèdent pour couvrir 24h/24.
Exemple : Équipe Matin 06h00→14h00 | Équipe Après-midi 14h00→22h00 | Équipe Nuit 22h00→06h00

Règles spécifiques aux horaires par équipe :
    • Les équipes de nuit chevauchent deux jours calendaires. Le pointage de départ à 06h00 du mardi est associé à la plage du lundi soir.
    • Le système calcule automatiquement le décalage de jour pour les pointages en équipe de nuit.
    • La rotation des équipes est planifiée à l'avance dans le planning (voir module Emplois du temps).
    • Un employé ne peut être affecté qu'à une seule équipe par plage de rotation.
    • Les heures supplémentaires en équipe de nuit bénéficient du coefficient applicable selon la législation (paramétrable).
10.2.3 Horaires personnalisés (individuels)
Un horaire personnalisé est défini pour un employé spécifique. Il prend le dessus sur l'horaire par défaut de son poste ou département.
Cas d'usage :
    • Employé à temps partiel avec des horaires spécifiques.
    • Employé en contrat aidé avec horaires réduits.
    • Cadre avec plages horaires flexibles.
    • Employé en aménagement thérapeutique.
10.2.4 Horaires enseignants
Spécifique aux organisations de type Établissement scolaire et Université. Un enseignant intervient sur des créneaux précis qui varient selon les jours de la semaine.
Exemple : Lundi 12h00→14h00 | Mardi 08h00→10h00 | Jeudi 15h00→17h00. L'enseignant est absent les autres jours — ce n'est pas une absence à justifier.

Règles spécifiques aux horaires enseignants :
    • L'emploi du temps d'un enseignant est défini par semestre ou trimestre.
    • Chaque créneau est lié à une matière, une salle et un groupe d'étudiants (informations stockées pour référence, non gérées par ce module).
    • Le pointage n'est autorisé que pendant les créneaux planifiés (± fenêtre de pointage).
    • Un créneau annulé (maladie, substitution) doit être marqué comme absent ou remplacé.
    • Un enseignant peut avoir plusieurs créneaux le même jour (ex : 08h00→10h00 et 14h00→16h00).
    • Chaque créneau nécessite un pointage d'arrivée et un pointage de départ distincts.
10.3 Affectation des horaires
Un horaire peut être affecté à plusieurs niveaux de la hiérarchie organisationnelle, avec un système de priorité :
Priorité	Niveau	Description
Niveau 1 (plus fort)	Employé individuel	Horaire personnalisé affecté directement à l'employé.
Niveau 2	Poste	Horaire par défaut du poste (ex : Caissier = 08h00-16h00).
Niveau 3	Département	Horaire par défaut du département (ex : Service Commercial = 09h00-18h00).
Niveau 4 (plus faible)	Agence	Horaire par défaut de l'agence.

10.4 Gestion des changements d'horaire
Un employé peut changer d'horaire temporairement ou définitivement. Le système gère l'historique complet des horaires de chaque employé.
    • Chaque affectation d'horaire a une date de début et une date de fin optionnelle.
    • À chaque pointage, le système détermine l'horaire applicable à la date courante.
    • Les changements d'horaire futurs peuvent être planifiés à l'avance.
    • L'historique des horaires est conservé indéfiniment pour la cohérence des rapports.

MODULE GESTION DES EMPLOYÉS

11.1 Description générale
Le module de gestion des employés permet à l'Administrateur de créer, configurer et gérer les comptes de tous les membres de l'organisation. Chaque employé dispose d'un profil complet contenant ses informations personnelles, professionnelles et ses paramètres de pointage.
11.2 Modèle de données employé
11.2.1 Informations personnelles
Champ	Description
Matricule	Identifiant interne unique au sein de l'organisation (généré automatiquement ou saisi manuellement).
Prénom	Prénom de l'employé. Obligatoire.
Nom	Nom de famille. Obligatoire.
Nom d'usage	Nom d'usage différent du nom légal (optionnel).
Date de naissance	Date de naissance (pour calcul ancienneté et congés).
Genre	Masculin, Féminin, Non renseigné.
Nationalité	Pays de nationalité.
Numéro identité	Numéro de carte d'identité ou passeport (chiffré en base).
Photo de profil	Photo officielle de l'employé (max 2 Mo, PNG/JPG).
E-mail professionnel	Adresse e-mail principale de connexion.
E-mail personnel	Adresse e-mail secondaire pour les notifications hors réseau.
Téléphone pro	Numéro de téléphone professionnel.
Téléphone perso	Numéro de téléphone personnel.
Adresse domicile	Adresse complète du domicile.
Contact d'urgence	Nom, prénom et téléphone du contact en cas d'urgence.
11.2.2 Informations professionnelles
Champ	Description
Poste	Poste occupé (référence vers la table des postes).
Département	Département d'appartenance.
Agence	Agence principale d'affectation.
Agences secondaires	Autres agences où l'employé peut pointer.
Type de contrat	CDI, CDD, Intérim, Stage, Bénévole, Consultant, etc.
Date d'entrée	Date de prise de poste.
Date de fin contrat	Date de fin de contrat (CDD, Stage).
Manager direct	Référence vers le manager responsable.
Horaire	Horaire de travail affecté.
Droit aux congés	Nombre de jours de congés annuels.
Solde congés	Nombre de jours restants (calculé automatiquement).
Statut	Actif, Suspendu, En congé, Archivé.

11.3 Création d'un employé
11.3.1 Préconditions
    • L'Administrateur est connecté et son organisation est active.
    • Au minimum un poste, un département et une agence existent dans l'organisation.
11.3.2 Déroulement
    58. L'Administrateur accède au formulaire de création d'employé.
    59. Il renseigne les informations obligatoires (prénom, nom, e-mail, poste, agence).
    60. Il configure les paramètres d'accès (rôle, horaire, permissions IA).
    61. Le système génère automatiquement un matricule si non fourni.
    62. Le système crée le compte utilisateur avec un mot de passe temporaire.
    63. Le système envoie un e-mail de bienvenue à l'employé avec ses accès.
    64. L'employé est affiché dans la liste avec le statut 'Actif'.
11.3.3 Règles de validation
    • L'e-mail doit être unique au sein de la plateforme entière (pas seulement au sein du tenant).
    • Le matricule doit être unique au sein de l'organisation.
    • La date d'entrée ne peut pas être dans le futur de plus de 30 jours.
    • Si une date de fin de contrat est renseignée, elle doit être postérieure à la date d'entrée.
11.4 États d'un employé
État	Comportement
Actif	L'employé peut se connecter et pointer normalement.
Suspendu	L'employé ne peut pas se connecter. Son historique est conservé.
En congé	L'employé est en congé approuvé. Ses absences ne sont pas comptabilisées.
Archivé	L'employé a quitté l'organisation. Accès désactivé, données conservées.

11.5 Import en masse
L'Administrateur peut importer une liste d'employés via un fichier CSV ou Excel. Le système fournit un modèle de fichier téléchargeable avec toutes les colonnes requises et leur format attendu. Le processus d'import inclut :
    65. Téléversement du fichier (max 10 Mo, formats acceptés : .csv, .xlsx, .xls).
    66. Validation ligne par ligne avec rapport d'erreurs détaillé.
    67. Aperçu des données avant l'import définitif.
    68. Import avec rapport final (lignes importées, lignes en erreur, lignes ignorées).
    69. Les lignes en erreur peuvent être corrigées et réimportées.

MODULE GESTION DES ABSENCES, RETARDS ET CONGÉS

12.1 Gestion des absences
12.1.1 Détection automatique des absences
Une absence est détectée automatiquement par le système lorsqu'un employé n'a pas effectué de pointage d'arrivée à l'issue de la fenêtre de pointage autorisée. Un job automatique (tâche Celery planifiée) s'exécute quotidiennement pour détecter les absences non justifiées.
Logique de détection :
    70. À la fin de la fenêtre de pointage d'arrivée, le système vérifie tous les employés devant être présents ce jour.
    71. Pour chaque employé sans pointage, le système crée automatiquement un enregistrement d'absence.
    72. L'Administrateur et le Manager reçoivent une notification.
    73. L'employé reçoit une notification l'informant de son absence enregistrée.
12.1.2 Justification d'une absence
Un employé peut justifier une absence depuis son espace personnel :
    • Il sélectionne la date de l'absence.
    • Il sélectionne le motif (liste configurable par l'Administrateur).
    • Il joint un ou plusieurs justificatifs (PDF, JPG, PNG, max 5 Mo par fichier).
    • Il ajoute un commentaire explicatif.
    • Il soumet la demande de justification.
L'Administrateur ou le Manager :
    • Reçoit une notification de soumission.
    • Consulte la demande avec les justificatifs.
    • Approuve ou rejette la demande avec un commentaire.
    • L'employé reçoit une notification du résultat.
12.1.3 Types de motifs d'absence (configurables)
    • Maladie (avec ou sans certificat médical).
    • Accident du travail.
    • Congé maternité / paternité.
    • Décès d'un proche.
    • Mariage.
    • Déménagement.
    • Convocation administrative.
    • Formation professionnelle.
    • Absence injustifiée.
    • Autres (champ libre).

12.2 Gestion des retards
12.2.1 Calcul automatique des retards
Un retard est calculé automatiquement lors de chaque pointage d'arrivée. La formule est :
Retard (minutes) = Heure pointage − (Heure prévue + Tolérance). Si le résultat est ≤ 0, aucun retard n'est enregistré.

Le système cumule les retards et fournit des statistiques :
    • Nombre total de retards sur la période.
    • Durée totale cumulée des retards.
    • Retard moyen par occurrence.
    • Évolution des retards sur les 12 derniers mois.
12.2.2 Alertes retards
    • Alerte immédiate au Manager dès la détection d'un retard supérieur à un seuil configurable.
    • Alerte récurrente si l'employé dépasse N retards en M jours (seuils configurables).

12.3 Gestion des congés
12.3.1 Types de congés
L'Administrateur configure les types de congés de son organisation :
Type	Description
Congé annuel payé	Nombre de jours défini annuellement (droit légal + convention collective).
RTT	Réduction du Temps de Travail (spécifique France).
Congé sans solde	Congé accordé sans maintien de salaire.
Congé maladie	Arrêt maladie avec justificatif médical.
Congé maternité/paternité	Congé légal lié à la naissance ou adoption.
Congé exceptionnel	Décès, mariage, déménagement, etc.
Formation	Période de formation professionnelle.
Personnalisé	Types de congés spécifiques à l'organisation.
12.3.2 Processus de demande de congé
    74. L'employé accède au formulaire de demande de congé.
    75. Il sélectionne le type de congé, la date de début et la date de fin.
    76. Le système calcule automatiquement le nombre de jours ouvrables de congé.
    77. Le système vérifie le solde de congés disponible.
    78. Le système vérifie l'absence de conflits (jours fériés, congés déjà posés).
    79. L'employé soumet sa demande avec un commentaire optionnel.
    80. Le Manager et/ou l'Administrateur reçoivent une notification.
    81. Le Manager approuve ou rejette la demande.
    82. L'employé est notifié du résultat.
    83. Si approuvé, le solde de congés est débité.
12.3.3 Règles métier des congés
    • La demande de congé doit être soumise au moins N jours à l'avance (N configurable, défaut : 3 jours).
    • Le solde de congés ne peut pas devenir négatif (sauf exception configurée : congés par anticipation).
    • Les congés chevauchant des jours fériés ne décomptent pas les jours fériés.
    • La modification d'une demande approuvée nécessite une nouvelle validation.
    • L'annulation d'un congé approuvé restitue le solde correspondant.
    • Les congés non pris à la fin de l'année peuvent être reportés, monétisés ou perdus selon la configuration.
12.4 Jours fériés
L'Administrateur configure les jours fériés de son organisation :
    • Importation automatique des jours fériés nationaux selon le pays de l'organisation.
    • Ajout de jours fériés locaux ou spécifiques à l'organisation.
    • Configuration des jours fériés récurrents (annuels) et ponctuels.
    • Les jours fériés sont exclus du calcul des absences et des retards.
    • Les jours fériés sont exclus du calcul des jours de congés.

SÉCURITÉ DE LA PLATEFORME

13.1 Principes fondamentaux de sécurité
La sécurité de la plateforme est conçue selon les référentiels OWASP ASVS (Application Security Verification Standard) et OWASP Top 10. Les principes directeurs sont :
    • Principe du moindre privilège : chaque utilisateur n'accède qu'aux ressources strictement nécessaires à son rôle.
    • Défense en profondeur : la sécurité est assurée à plusieurs niveaux (réseau, serveur, application, base de données).
    • Sécurité par conception : la sécurité est intégrée dès la conception, pas ajoutée a posteriori.
    • Échec sécurisé : en cas d'erreur, le système refuse l'accès par défaut.
    • Zero Trust : aucune requête n'est considérée comme fiable par défaut, même provenant du réseau interne.
13.2 Sécurité des mots de passe
13.2.1 Règles de complexité
Règle	Détail
Longueur minimale	8 caractères (configurable par l'Administrateur jusqu'à 20).
Majuscule obligatoire	Au moins une lettre majuscule (A-Z).
Minuscule obligatoire	Au moins une lettre minuscule (a-z).
Chiffre obligatoire	Au moins un chiffre (0-9).
Caractère spécial	Au moins un caractère spécial (@, #, $, !, etc.).
Interdictions	Ne peut pas contenir le prénom, le nom ou l'e-mail de l'utilisateur.
Historique	Le nouveau mot de passe ne peut pas être identique aux N derniers (N configurable, défaut : 5).
Expiration	Le mot de passe expire après N jours (configurable, défaut : 90 jours).
Avertissement	Notification 7 jours avant expiration.
13.2.2 Hachage des mots de passe
Les mots de passe sont hachés avec l'algorithme Argon2id (recommandé par OWASP) via la bibliothèque Django argon2-cffi. Les paramètres de hachage sont : time_cost = 2, memory_cost = 65536 KB, parallelism = 2.

13.3 Protection contre les attaques
13.3.1 Brute Force et Credential Stuffing
    • Blocage du compte après 5 tentatives échouées (configurable).
    • Blocage progressif : 15 min, 30 min, 1h, 4h, 24h selon la récurrence.
    • CAPTCHA après 3 tentatives échouées.
    • Limitation de débit (rate limiting) : max 10 tentatives par minute par IP.
    • Notification par e-mail à l'utilisateur lors d'un blocage.
    • Notification à l'Administrateur en cas de blocage répété.
13.3.2 Injection SQL
    • Utilisation exclusive de l'ORM Django pour toutes les requêtes (paramètrisation automatique).
    • Interdiction des requêtes SQL brutes (raw SQL) sauf cas exceptionnels documentés et revus.
    • Validation de toutes les entrées utilisateur avant traitement.
    • Analyse de sécurité (SAST) dans le pipeline CI/CD.
13.3.3 Cross-Site Scripting (XSS)
    • Échappement automatique de toutes les variables dans les templates Django.
    • Content Security Policy (CSP) stricte : interdiction d'exécuter des scripts inline non approuvés.
    • Validation et assainissement de tous les champs de saisie.
    • Bibliothèque bleach pour l'assainissement des champs HTML riches.
13.3.4 CSRF (Cross-Site Request Forgery)
    • Middleware CSRF Django activé sur toutes les requêtes POST, PUT, DELETE.
    • Token CSRF unique par session, inclus dans tous les formulaires.
    • Vérification du token CSRF côté serveur à chaque requête modifiante.
    • SameSite=Strict sur les cookies de session.
13.3.5 Clickjacking
    • En-tête HTTP X-Frame-Options: DENY sur toutes les réponses.
    • Directive frame-ancestors 'none' dans la CSP.
13.3.6 Session Hijacking
    • Cookies de session httpOnly et Secure.
    • Régénération du Session ID après chaque connexion.
    • Invalidation des sessions lors d'un changement de mot de passe.
    • Détection de changement d'adresse IP en cours de session (alerte ou déconnexion selon configuration).
13.3.7 Téléversement de fichiers
    • Validation du type MIME côté serveur (pas uniquement l'extension).
    • Limitation de la taille des fichiers (configurable par type).
    • Stockage des fichiers uploadés hors de la racine web (non accessibles directement).
    • Scan antivirus des fichiers uploadés (intégration ClamAV recommandée).
    • Renommage automatique des fichiers avec UUID pour éviter les conflits et attaques.

13.4 CAPTCHA
Un CAPTCHA intelligent est intégré pour protéger les formulaires sensibles :
    • Conditions d'apparition : après 3 tentatives de connexion échouées, sur le formulaire de réinitialisation de mot de passe, sur tout formulaire public.
    • Solution retenue : hCaptcha (alternative à Google reCAPTCHA respectueuse de la vie privée) ou Google reCAPTCHA v3.
    • Le CAPTCHA est activable/désactivable par l'Administrateur.
    • Les comptes de test peuvent être exemptés du CAPTCHA via une liste blanche configurable.

13.5 En-têtes de sécurité HTTP
En-tête	Valeur et objectif
Strict-Transport-Security	max-age=31536000; includeSubDomains; preload — Force HTTPS.
X-Content-Type-Options	nosniff — Empêche le MIME sniffing.
X-Frame-Options	DENY — Empêche l'inclusion dans un iframe.
Content-Security-Policy	Politique stricte définissant les sources autorisées pour scripts, styles, images.
Referrer-Policy	strict-origin-when-cross-origin — Contrôle les informations de référent.
Permissions-Policy	Restriction des API navigateur (caméra, géolocalisation uniquement pour l'app).
Cache-Control	no-store sur les pages authentifiées pour éviter la mise en cache de données sensibles.

13.6 Chiffrement et transport
    • HTTPS obligatoire (TLS 1.2 minimum, TLS 1.3 recommandé) sur l'ensemble des communications.
    • Certificats SSL/TLS renouvelés automatiquement via Let's Encrypt.
    • Données sensibles chiffrées en base de données (numéros d'identité, données personnelles sensibles).
    • Clés de chiffrement gérées via les variables d'environnement Docker Secrets.
    • Les sauvegardes sont chiffrées avant stockage.

MODULE JOURNAL D'AUDIT ET TRAÇABILITÉ

14.1 Principes
Tout événement significatif survenant dans la plateforme est enregistré dans un journal d'audit immuable. Ce journal constitue la trace légale et technique de toutes les actions effectuées par tous les acteurs du système.
Le journal d'audit ne peut pas être modifié ni supprimé par aucun utilisateur, y compris le Super Administrateur. Les entrées sont en écriture seule.

14.2 Événements auditables
14.2.1 Authentification
    • Connexion réussie.
    • Tentative de connexion échouée (avec raison).
    • Déconnexion (manuelle ou automatique).
    • Blocage du compte.
    • Déblocage du compte.
    • Réinitialisation de mot de passe demandée.
    • Réinitialisation de mot de passe effectuée.
    • Changement de mot de passe.
    • Révocation de session.
14.2.2 Gestion des utilisateurs
    • Création d'un utilisateur.
    • Modification des informations d'un utilisateur.
    • Activation / désactivation d'un utilisateur.
    • Suppression d'un utilisateur.
    • Modification des rôles et permissions.
14.2.3 Pointages
    • Pointage effectué (arrivée ou départ).
    • Pointage refusé (avec raison).
    • Pointage modifié manuellement (avec valeurs avant/après).
    • Pointage synchronisé (hors ligne).
    • Pointage validé ou rejeté.
14.2.4 Données et paramètres
    • Création / modification / suppression d'une agence.
    • Création / modification / suppression d'un horaire.
    • Modification des paramètres de l'organisation.
    • Import de données.
    • Export de données.
    • Accès à un rapport.
    • Utilisation de l'assistant IA.
14.2.5 Documents
    • Upload d'un document.
    • Consultation d'un document.
    • Suppression d'un document.

14.3 Structure d'un événement d'audit
Champ	Description
id	Identifiant unique UUID de l'événement.
tenant_id	Organisation concernée (null pour les événements globaux).
user_id	Utilisateur ayant déclenché l'action.
user_email	E-mail de l'utilisateur au moment de l'action (historisation).
user_role	Rôle de l'utilisateur au moment de l'action.
categorie	Authentification, Utilisateur, Pointage, Paramètres, Document, etc.
action	Code de l'action (LOGIN_SUCCESS, CLOCK_IN, USER_CREATE, etc.).
description	Description lisible de l'action.
objet_type	Type de l'objet concerné (User, Pointage, Agence, etc.).
objet_id	Identifiant de l'objet concerné.
valeurs_avant	JSON des valeurs avant modification (pour les actions de modification).
valeurs_apres	JSON des valeurs après modification.
adresse_ip	Adresse IP du client.
user_agent	User-agent complet.
appareil	Type d'appareil détecté.
navigateur	Navigateur détecté.
latitude	Latitude GPS si disponible (pour les pointages).
longitude	Longitude GPS si disponible (pour les pointages).
resultat	SUCCESS, FAILURE, WARNING.
details_erreur	Message d'erreur en cas d'échec.
timestamp	Horodatage précis UTC (YYYY-MM-DD HH:MM:SS.ffffff).

MODULE INTELLIGENCE ARTIFICIELLE

15.1 Description générale
La plateforme intègre un module d'intelligence artificielle permettant d'analyser les données de présence, de détecter des anomalies, de générer des rapports intelligents et de répondre aux questions des utilisateurs via un assistant conversationnel.
15.2 Architecture IA
Le module IA est conçu pour être agnostique au fournisseur. Le Super Administrateur configure le ou les fournisseurs IA disponibles sur la plateforme. Chaque organisation peut choisir son fournisseur parmi ceux disponibles.
15.2.1 Fournisseurs IA supportés
    • OpenAI (GPT-4, GPT-3.5 Turbo).
    • Anthropic (Claude).
    • Mistral AI.
    • Ollama (modèles locaux — pour les organisations souhaitant garder les données en interne).
    • Autres fournisseurs compatibles API REST (extensible).
15.2.2 Configuration par organisation
    • Sélection du fournisseur IA parmi ceux activés par le Super Admin.
    • Clé API propre à l'organisation (chiffrée en base).
    • Modèle sélectionné (ex : gpt-4o, claude-3-opus, mistral-large).
    • Température et autres paramètres du modèle.
    • Langue de l'assistant.
15.3 Fonctionnalités IA
15.3.1 Génération de rapports intelligents
    • Résumé quotidien automatique : envoi chaque matin d'un résumé des absences, retards et anomalies de la veille.
    • Résumé hebdomadaire : analyse de la semaine écoulée avec tendances.
    • Résumé mensuel : rapport mensuel complet avec graphiques et recommandations.
15.3.2 Détection d'anomalies
    • Détection des patterns de retards répétitifs.
    • Détection des absences non justifiées récurrentes.
    • Détection des pointages suspects (hors zone, heure inhabituelle).
    • Détection des employés à risque d'absentéisme.
    • Génération automatique d'alertes pour les anomalies détectées.
15.3.3 Assistant conversationnel
Chaque rôle dispose d'un accès configuré à l'assistant IA :
Rôle	Périmètre des questions autorisées
Super Admin	Questions sur les statistiques globales de la plateforme, anomalies techniques.
Administrateur	Questions sur les présences, absences, statistiques de son organisation. Génération de rapports personnalisés.
Manager	Questions sur son équipe : présences, absences, performances.
Employé	Questions sur ses propres données : solde de congés, historique de présences. Accès configurable par l'Admin.
15.3.4 Prévisions et recommandations
    • Prévision du taux d'absentéisme sur les prochaines semaines (basé sur l'historique).
    • Recommandations de planification (ex : anticiper les renforts lors des pics historiques d'absences).
    • Recommandations RH (ex : identifier les employés nécessitant un entretien).
15.4 Sécurité et limites du module IA
    • L'assistant IA n'a accès qu'aux données du tenant actif. Il est techniquement impossible de croiser les données entre tenants.
    • Toutes les requêtes IA sont enregistrées dans le journal (qui a demandé quoi, quand).
    • Les réponses de l'IA sont journalisées pour audit.
    • L'historique des conversations IA est conservé N jours (N configurable).
    • Des limites de requêtes sont configurables (quota mensuel par organisation).
    • L'Administrateur peut désactiver l'accès IA pour certains rôles ou employés.
    • Le contexte envoyé à l'IA est strictement limité aux données nécessaires à la réponse.
    • Aucune donnée personnelle nominative n'est envoyée sans consentement explicite configuré.

TABLEAUX DE BORD

16.1 Tableau de bord — Super Administrateur
Le tableau de bord du Super Administrateur offre une vue globale de toute la plateforme SaaS :
    • Nombre total d'organisations actives / suspendues / expirées.
    • Nombre total d'utilisateurs sur la plateforme.
    • Volume de pointages sur les 30 derniers jours (graphique en courbe).
    • Organisations créées ce mois-ci.
    • Organisations dont l'abonnement expire prochainement.
    • Alertes système (erreurs, performances, sauvegardes).
    • Journal des dernières actions d'audit global.
    • Statistiques d'utilisation de l'IA par organisation.
    • Carte mondiale (si organisations dans plusieurs pays) ou régionale.

16.2 Tableau de bord — Administrateur
Le tableau de bord de l'Administrateur est le centre de pilotage de son organisation :
16.2.1 Widgets KPI en temps réel
    • Nombre d'employés présents actuellement (mis à jour en temps réel).
    • Nombre d'absents du jour.
    • Nombre de retardataires du jour.
    • Taux de présence du jour (%) avec comparaison J-1 et J-7.
    • Nombre de demandes de congé en attente.
    • Nombre de justificatifs en attente de validation.
16.2.2 Graphiques
    • Évolution du taux de présence sur les 30 derniers jours (courbe).
    • Répartition des absences par motif ce mois (camembert).
    • Top 10 des employés avec le plus de retards (barres).
    • Comparaison présence par agence (barres groupées).
    • Répartition présence par département (barres empilées).
16.2.3 Carte en temps réel
    • Carte interactive affichant les agences avec un indicateur de taux de présence.
    • Clic sur une agence pour voir les détails.
16.2.4 Activités récentes
    • Feed en temps réel des derniers pointages (arrivées et départs).
    • Alertes récentes (absences, retards excessifs, anomalies).

16.3 Tableau de bord — Manager
    • Liste de ses employés avec statut de présence en temps réel.
    • Alertes : absences et retards de son équipe aujourd'hui.
    • Demandes en attente (congés, justificatifs).
    • Graphique de présence de son équipe sur les 7 derniers jours.
    • Planning hebdomadaire de son équipe.

16.4 Tableau de bord — Employé
    • Bouton de pointage (arrivée ou départ selon contexte).
    • Statut du jour (Présent, Absent, En congé).
    • Dernier pointage enregistré.
    • Solde de congés restant.
    • Résumé du mois en cours (jours présents, jours absents, retards).
    • Mes demandes en cours (congés, justificatifs).
    • Annonces de l'organisation.
    • Historique de mes 10 derniers pointages.

MODULE NOTIFICATIONS

17.1 Canaux de notification
Canal	Description
E-mail	Via SMTP (SendGrid, Mailgun, ou serveur SMTP propre). Pour les notifications importantes et les rapports.
Notification in-app	Cloche dans l'interface avec badge de compteur. Pour les actions nécessitant une réponse.
Notification push (PWA)	Via le Service Worker. Pour les alertes en temps réel même application fermée.
SMS (optionnel)	Via Twilio ou autre provider. Configurable par l'Admin. Pour les alertes critiques.

17.2 Scénarios de notification
Événement	Destinataire(s)	Canal(aux)
Connexion réussie	Utilisateur	E-mail si nouvelle IP
Blocage de compte	Utilisateur + Admin	E-mail
Tentative suspecte	Admin	E-mail + In-app
Absence détectée	Employé + Manager + Admin	E-mail + Push + In-app
Retard enregistré	Employé + Manager	Push + In-app
Demande de congé soumise	Manager + Admin	E-mail + In-app
Congé approuvé	Employé	E-mail + Push
Congé refusé	Employé	E-mail + Push
Congé annulé	Employé + Manager	E-mail + In-app
Pointage hors zone	Admin + Manager	E-mail + In-app
Synchronisation offline	Employé	Push
Justificatif soumis	Manager + Admin	In-app
Justificatif approuvé/rejeté	Employé	E-mail + Push
Annonce publiée	Destinataires	Push + In-app
Mot de passe expirant	Utilisateur	E-mail (J-7, J-3, J-1)
Rapport hebdomadaire	Admin	E-mail
Rapport mensuel	Admin + Managers	E-mail
Sauvegarde réussie	Super Admin	E-mail
Sauvegarde échouée	Super Admin	E-mail + SMS

17.3 Personnalisation des notifications
Chaque utilisateur peut personnaliser ses préférences de notification :
    • Activer / désactiver chaque type de notification.
    • Choisir le canal pour chaque type (e-mail, push, in-app).
    • Définir des plages horaires de non-dérangement (ex : ne pas envoyer de push entre 22h et 7h).
L'Administrateur peut définir des règles globales qui prennent le dessus sur les préférences individuelles pour les notifications critiques (ex : blocage de compte, absence non justifiée).

PERFORMANCES, EXPORTS ET SAUVEGARDES

18.1 Exigences de performance
Indicateur	Objectif
Temps de chargement page	< 2 secondes pour 95% des requêtes en conditions normales.
Temps de réponse API	< 500ms pour les requêtes simples (GET liste, GET détail).
Temps de pointage	< 3 secondes de l'appui sur le bouton à la confirmation.
Capacité simultanée	Support de 500 utilisateurs simultanés par instance (horizontalement scalable).
Disponibilité	99.5% de disponibilité mensuelle (SLA de base).
Chargement des images	Compression automatique, format WebP si supporté.
18.2 Optimisations techniques
18.2.1 Base de données
    • Index sur toutes les colonnes de recherche fréquente (tenant_id, employe_id, date_pointage, statut).
    • Index composites pour les requêtes courantes (tenant_id + date_pointage, tenant_id + employe_id + date).
    • Pagination obligatoire sur toutes les listes (défaut : 25 éléments par page, configurable).
    • Utilisation de select_related() et prefetch_related() pour éviter les requêtes N+1.
    • Analyse et optimisation régulière des requêtes lentes via EXPLAIN ANALYZE.
18.2.2 Cache
    • Cache Redis pour les données peu volatiles (listes de postes, horaires, jours fériés).
    • Cache de session dans Redis.
    • Cache des requêtes de statistiques (TTL : 15 minutes).
    • Cache des pages statiques via Nginx.
18.2.3 Traitement asynchrone
    • Tâches longues déportées vers Celery (exports, envoi d'e-mails, synchronisation offline, génération de rapports IA).
    • File d'attente Redis pour Celery.
    • Interface de monitoring Celery Flower.

18.3 Exports
Le système permet l'export des données dans plusieurs formats :
Format	Usage
PDF	Rapports de présence, fiches individuelles, résumés mensuels.
Excel (.xlsx)	Données brutes des pointages, listes d'employés, statistiques.
CSV	Export universel compatible avec les systèmes tiers.
JSON	Export technique pour intégration API.
Tous les exports sont générés de façon asynchrone via Celery. L'utilisateur reçoit une notification (in-app + e-mail) lorsque le fichier est prêt. Les fichiers d'export sont conservés 7 jours puis supprimés automatiquement.
18.4 Sauvegardes
18.4.1 Sauvegardes automatiques
    • Sauvegarde complète de la base de données MySQL : quotidienne à 02h00 UTC.
    • Sauvegarde différentielle : toutes les 6 heures.
    • Sauvegarde des fichiers uploadés (photos, documents) : quotidienne.
    • Rétention : 7 sauvegardes quotidiennes, 4 sauvegardes hebdomadaires, 3 sauvegardes mensuelles.
18.4.2 Sauvegardes manuelles
    • Le Super Administrateur peut déclencher une sauvegarde manuelle à tout moment.
    • Chaque sauvegarde manuelle est nommée avec horodatage et commentaire optionnel.
18.4.3 Stockage et sécurité
    • Les sauvegardes sont chiffrées avec AES-256 avant stockage.
    • Stockage sur au moins deux emplacements distincts (local + distant).
    • Vérification d'intégrité (checksum SHA-256) après chaque sauvegarde.
18.4.4 Restauration
    • La restauration est effectuée par le Super Administrateur depuis l'interface d'administration.
    • Un test de restauration automatique est effectué hebdomadairement sur un environnement de test.
    • Les résultats des tests de restauration sont journalisés et signalés au Super Admin.

EXIGENCES FONCTIONNELLES

19.1 Liste exhaustive des exigences fonctionnelles
ID	Description	Priorité
EF-001	L'utilisateur doit pouvoir se connecter avec son adresse e-mail et son mot de passe.	CRITIQUE
EF-002	Le système doit bloquer un compte après 5 tentatives de connexion échouées.	CRITIQUE
EF-003	L'utilisateur doit pouvoir réinitialiser son mot de passe via un lien sécurisé envoyé par e-mail.	HAUTE
EF-004	Chaque employé doit pouvoir effectuer un pointage d'arrivée depuis l'interface web.	CRITIQUE
EF-005	Chaque employé doit pouvoir effectuer un pointage de départ depuis l'interface web.	CRITIQUE
EF-006	Le système doit vérifier que l'employé est dans la zone GPS autorisée avant d'autoriser le pointage.	CRITIQUE
EF-007	Le pointage doit obligatoirement inclure une photo prise en temps réel par la caméra.	CRITIQUE
EF-008	Le pointage doit être refusé si l'employé est hors de la zone GPS autorisée.	CRITIQUE
EF-009	Le système doit fonctionner en mode hors ligne et synchroniser les pointages dès la reconnexion.	HAUTE
EF-010	L'Administrateur doit pouvoir créer, modifier, suspendre et supprimer des comptes employés.	CRITIQUE
EF-011	L'Administrateur doit pouvoir créer et gérer des agences avec coordonnées GPS.	CRITIQUE
EF-012	L'Administrateur doit pouvoir définir plusieurs types d'horaires de travail.	CRITIQUE
EF-013	Le système doit détecter automatiquement les absences non justifiées.	HAUTE
EF-014	L'employé doit pouvoir soumettre une demande de justification d'absence.	HAUTE
EF-015	L'employé doit pouvoir soumettre une demande de congé.	HAUTE
EF-016	Le Manager doit pouvoir approuver ou rejeter les demandes de congé de son équipe.	HAUTE
EF-017	Le système doit calculer automatiquement les retards et départs anticipés.	CRITIQUE
EF-018	L'Administrateur doit pouvoir exporter les données en PDF, Excel et CSV.	HAUTE
EF-019	Le Super Administrateur doit pouvoir créer et gérer les organisations.	CRITIQUE
EF-020	Le Super Administrateur doit pouvoir suspendre et réactiver une organisation.	CRITIQUE
EF-021	Toutes les actions doivent être enregistrées dans le journal d'audit.	CRITIQUE
EF-022	Le système doit envoyer des notifications par e-mail et push pour les événements importants.	HAUTE
EF-023	L'application doit être installable comme PWA sur smartphone, tablette et ordinateur.	HAUTE
EF-024	L'assistant IA doit répondre aux questions sur les données de présence.	MOYENNE
EF-025	Le système doit générer des rapports automatiques (quotidien, hebdomadaire, mensuel).	MOYENNE
EF-026	L'Administrateur doit pouvoir importer une liste d'employés via un fichier CSV/Excel.	HAUTE
EF-027	Le système doit afficher des tableaux de bord avec KPI en temps réel.	HAUTE
EF-028	L'Administrateur doit pouvoir personnaliser le logo et les couleurs de son organisation.	MOYENNE
EF-029	Le système doit gérer les jours fériés et les exclure des calculs d'absence.	HAUTE
EF-030	Le système doit supporter les horaires d'équipe incluant les équipes de nuit.	HAUTE

EXIGENCES NON FONCTIONNELLES

20.1 Sécurité
    • ENF-SEC-001 : Toutes les communications doivent être chiffrées en TLS 1.2 minimum.
    • ENF-SEC-002 : Les mots de passe doivent être hachés avec Argon2id.
    • ENF-SEC-003 : La plateforme doit résister aux attaques du Top 10 OWASP.
    • ENF-SEC-004 : Un audit de sécurité (pentest) doit être réalisé avant la mise en production.
20.2 Disponibilité
    • ENF-DIS-001 : La plateforme doit être disponible 99.5% du temps (hors maintenance planifiée).
    • ENF-DIS-002 : Les maintenances planifiées doivent être annoncées 48h à l'avance.
    • ENF-DIS-003 : Le temps de reprise après incident (RTO) doit être inférieur à 4 heures.
    • ENF-DIS-004 : Le point de reprise maximum (RPO) doit être inférieur à 6 heures.
20.3 Performances
    • ENF-PERF-001 : 95% des pages doivent se charger en moins de 2 secondes.
    • ENF-PERF-002 : Le processus de pointage doit être complété en moins de 5 secondes.
    • ENF-PERF-003 : Le système doit supporter 500 utilisateurs simultanés sans dégradation.
20.4 Maintenabilité
    • ENF-MAINT-001 : Le code doit suivre les conventions PEP8 (Python) et être documenté.
    • ENF-MAINT-002 : La couverture de tests unitaires doit être supérieure à 80%.
    • ENF-MAINT-003 : Un pipeline CI/CD doit être en place pour automatiser les tests et déploiements.
    • ENF-MAINT-004 : La documentation technique doit être maintenue à jour.
20.5 Extensibilité
    • ENF-EXT-001 : L'architecture doit permettre l'ajout de nouveaux modules sans refonte.
    • ENF-EXT-002 : Les nouvelles fonctionnalités doivent être activables par feature flag.
    • ENF-EXT-003 : L'API interne doit être documentée avec OpenAPI/Swagger.
20.6 Accessibilité
    • ENF-ACC-001 : L'interface doit respecter le niveau AA des WCAG 2.1.
    • ENF-ACC-002 : Les contrastes de couleurs doivent respecter un ratio minimum de 4.5:1.
    • ENF-ACC-003 : L'application doit être navigable entièrement au clavier.
    • ENF-ACC-004 : Les images doivent avoir des attributs alt descriptifs.
    • ENF-ACC-005 : L'application doit être compatible avec les lecteurs d'écran NVDA et VoiceOver.

RÈGLES MÉTIER CONSOLIDÉES

21.1 Règles organisationnelles
    • RM-ORG-001 : Un employé appartient à une et une seule organisation.
    • RM-ORG-002 : Une organisation possède au moins une agence.
    • RM-ORG-003 : Une agence appartient à une et une seule organisation.
    • RM-ORG-004 : Aucune donnée ne peut transiter entre deux organisations.
    • RM-ORG-005 : La suspension d'une organisation entraîne le blocage immédiat de tous ses utilisateurs.
21.2 Règles de pointage
    • RM-POINT-001 : Un pointage nécessite obligatoirement une photo prise en direct par la caméra.
    • RM-POINT-002 : Une photo de galerie est strictement interdite et détectée automatiquement.
    • RM-POINT-003 : La position GPS de l'employé doit être dans la zone autorisée de son agence.
    • RM-POINT-004 : Un employé ne peut effectuer qu'un pointage d'arrivée et un pointage de départ par plage horaire.
    • RM-POINT-005 : Le pointage d'arrivée doit précéder le pointage de départ.
    • RM-POINT-006 : L'heure de référence pour les calculs est l'heure du serveur, pas celle du client.
    • RM-POINT-007 : Un pointage ne peut être modifié que par un Manager ou Administrateur, avec traçabilité complète.
    • RM-POINT-008 : Un pointage hors connexion est valide si synchronisé dans le délai configuré.
    • RM-POINT-009 : Un GPS simulé/falsifié entraîne le refus du pointage et une alerte à l'Administrateur.
21.3 Règles d'horaires
    • RM-HOR-001 : Un employé doit toujours avoir un horaire actif affecté.
    • RM-HOR-002 : L'horaire individuel prévaut sur l'horaire du poste, qui prévaut sur celui du département.
    • RM-HOR-003 : Un pointage effectué hors de la fenêtre de pointage est marqué HORS_HORAIRE.
    • RM-HOR-004 : Les équipes de nuit chevauchant minuit sont rattachées à la journée de début.
    • RM-HOR-005 : Un enseignant n'est absent que pour les créneaux planifiés, pas les jours sans cours.
21.4 Règles de congés
    • RM-CONGE-001 : Un congé ne peut être posé que si le solde est suffisant (sauf exception).
    • RM-CONGE-002 : Les jours fériés ne sont pas décomptés des congés.
    • RM-CONGE-003 : Toute modification d'un congé approuvé requiert une nouvelle validation.
    • RM-CONGE-004 : L'annulation d'un congé approuvé restitue automatiquement le solde.
21.5 Règles de sécurité
    • RM-SEC-001 : Tout accès non autorisé à une ressource renvoie HTTP 403 sans révéler l'existence de la ressource.
    • RM-SEC-002 : Les erreurs système ne révèlent jamais de détails techniques à l'utilisateur final.
    • RM-SEC-003 : Toute action administrative est enregistrée dans le journal d'audit.
    • RM-SEC-004 : Le journal d'audit est en écriture seule, aucune modification ni suppression n'est possible.

CAS PARTICULIERS

22.1 Cas liés au GPS
Cas	Comportement du système
GPS désactivé	Afficher instructions pour activer. Refuser le pointage. Logger la tentative.
Permission GPS refusée	Afficher instructions pour accorder la permission. Refuser le pointage.
GPS peu précis (>100m)	Enregistrer pointage avec flag 'Faible précision'. Alerter l'Admin.
GPS simulé/falsifié	Refuser. Alerter Admin. Enregistrer dans l'audit comme tentative suspecte.
Hors zone autorisée	Refuser. Afficher la distance et la zone requise. Logger.
Travail sur plusieurs sites	Vérifier toutes les zones de toutes les agences affectées.
Télétravail	Créer une agence 'Télétravail' avec coordonnées du domicile.
22.2 Cas liés à la connectivité
Cas	Comportement du système
Internet indisponible	Mode offline activé. Pointage stocké localement. Synchro automatique à la reconnexion.
Connexion instable	Retry automatique 3 fois avec backoff exponentiel avant bascule offline.
Synchro > délai max	Pointage marqué EN_ATTENTE_VALIDATION pour contrôle manuel.
Falsification heure offline	Détection par comparaison heure client vs heure synchro. Alerte Admin.
22.3 Cas liés aux employés
Cas	Comportement du système
Employé suspendu	Connexion refusée. Message 'Compte suspendu'. Aucun pointage possible.
Employé en congé	Pointage autorisé si l'employé se présente quand même. Le système enregistre.
Pointage oublié (arrivée)	Absence automatiquement enregistrée après la fenêtre. Justificatif possible.
Départ oublié	Départ non enregistré. Alerte envoyée à l'employé et au Manager.
Changement d'horaire	L'horaire effectif est déterminé à la date du pointage selon l'historique.
Changement de téléphone	L'utilisateur se reconnecte normalement. Aucun lien fort au device.
22.4 Cas liés à l'organisation
Cas	Comportement du système
Organisation suspendue	Tous les utilisateurs du tenant perdent l'accès immédiatement.
Horaires de nuit (J-1/J)	Pointage rattaché au début de la plage (date J-1). Calcul automatique.
Jour férié non configuré	Traité comme jour ouvrable normal. Recommandation : configurer les jours fériés.
Agence désactivée	Aucun nouveau pointage accepté pour cette agence. Alerter l'Admin.

APPLICATION PWA ET RESPONSIVE DESIGN

23.1 Progressive Web App (PWA)
23.1.1 Manifest.json
Le fichier manifest.json définit les métadonnées de l'application PWA :
    • name : Nom complet de l'application.
    • short_name : Nom court affiché sous l'icône.
    • description : Description de l'application.
    • start_url : URL de démarrage (/dashboard/).
    • display : standalone (l'application s'affiche sans barre de navigation du navigateur).
    • background_color : Couleur de fond de l'écran de chargement.
    • theme_color : Couleur de la barre de statut.
    • icons : Icônes en différentes tailles (72x72, 96x96, 128x128, 144x144, 152x152, 192x192, 384x384, 512x512).
    • orientation : portrait-primary.
    • scope : / — L'application gère tout le domaine.
23.1.2 Installation sur Android
    84. L'utilisateur visite l'application dans Chrome Android.
    85. Après 2 visites (ou immédiatement si bouton affiché), Chrome affiche une bannière d'installation.
    86. L'utilisateur accepte l'installation.
    87. L'application est ajoutée à l'écran d'accueil avec son icône et son nom.
    88. Au lancement, l'application s'ouvre en mode standalone (sans barre d'adresse).
23.1.3 Installation sur iPhone / iPad (Safari)
    89. L'utilisateur ouvre l'application dans Safari.
    90. Il tape l'icône de partage (bas de l'écran).
    91. Il sélectionne 'Sur l'écran d'accueil'.
    92. Il confirme le nom et tape 'Ajouter'.
Note : iOS ne supporte pas les notifications push via PWA (limitation Apple). Les notifications sont limitées aux notifications in-app et e-mail sur iOS.
23.1.4 Notifications push
    • Demande de permission affichée lors de la première visite (après interaction utilisateur obligatoire).
    • Stockage du token push en base de données associé à l'utilisateur et à l'appareil.
    • Envoi des notifications push via l'API Web Push (VAPID).
    • Gestion des tokens expirés (nettoyage automatique).

23.2 Responsive Design — Exigences détaillées
23.2.1 Smartphone
    • Navigation : menu hamburger avec drawer latéral ou bottom navigation bar.
    • Bouton de pointage : taille minimale 44x44px (recommandation Apple / Google Material Design).
    • Formulaires : champs agrandis, labels clairs, clavier adaptatif (numérique pour les téléphones).
    • Tableaux : transformation en cartes empilées sur mobile (pas de défilement horizontal).
    • Graphiques : simplifiés sur mobile, version complète sur desktop.
    • Photos : chargement optimisé, format WebP prioritaire.
23.2.2 Tablette
    • Navigation : sidebar fixe ou collapsible selon l'orientation.
    • Disposition en grille (2 colonnes pour les listes).
    • Tableaux affichés normalement (largeur suffisante).
23.2.3 Desktop
    • Sidebar de navigation fixe à gauche.
    • Contenu principal sur la droite avec max-width configuré.
    • Tableaux complets avec toutes les colonnes.
    • Graphiques en pleine largeur.
23.2.4 Compatibilité navigateurs
Navigateur	Support
Chrome	≥ 90 — Support complet.
Firefox	≥ 88 — Support complet.
Safari	≥ 14 — Support complet (limitations PWA iOS).
Edge	≥ 90 — Support complet (base Chromium).
Samsung Internet	≥ 14 — Support complet.
IE 11	Non supporté.

CONTRAINTES, RISQUES ET RECOMMANDATIONS

24.1 Contraintes techniques
    • Le projet est développé exclusivement avec Python/Django. Aucun autre framework backend n'est autorisé.
    • Le frontend utilise Django Templates, Bootstrap 5 et JavaScript vanilla. Aucun framework JS (React, Vue) n'est utilisé en V1.
    • La base de données est MySQL 8 exclusivement. PostgreSQL n'est pas supporté en V1.
    • L'environnement de production utilise Docker et Docker Compose obligatoirement.
    • Le code source est versionné sur GitHub avec une stratégie de branches définie (main, develop, feature/*, hotfix/*).
24.2 Contraintes organisationnelles
    • La plateforme doit être multi-langue dès le départ (Français, Anglais, Arabe au minimum).
    • L'interface doit supporter les langues RTL (Arabe).
    • Les formats de date et heure doivent être configurables par organisation.
24.3 Contraintes réglementaires
    • Le système doit être conforme au RGPD (Règlement Général sur la Protection des Données).
    • Les données personnelles doivent pouvoir être exportées sur demande (droit à la portabilité).
    • Les données personnelles doivent pouvoir être supprimées sur demande (droit à l'oubli), dans le respect des obligations légales de conservation.
    • La durée de conservation des données de pointage doit être configurable par organisation (minimum légal selon le pays).
    • Un registre des traitements de données doit être maintenu.
24.4 Risques identifiés
Risque	Niveau et mitigation
Fraude GPS	ÉLEVÉ — Un employé peut tenter de falsifier sa position GPS. Mitigation : détection des GPS simulés, photo obligatoire, audit des anomalies de position.
Fraude photo	ÉLEVÉ — Tentative d'utiliser une photo de galerie. Mitigation : contrainte caméra exclusive, vérification côté serveur.
Perte de connexion	MOYEN — Pointages non enregistrés en cas de panne réseau. Mitigation : mode offline avec IndexedDB.
Vol de session	MOYEN — Interception du token de session. Mitigation : HTTPS, httpOnly, SameSite cookies, expiration.
Surcharge base de données	MOYEN — Volume de pointages important. Mitigation : index, cache, pagination, archivage périodique.
Perte de données	BAS — En cas de panne serveur. Mitigation : sauvegardes automatiques, réplication.
Non-adoption utilisateurs	MOYEN — Résistance au changement. Mitigation : UX simplifiée, formation, documentation.

24.5 Recommandations
    • Mettre en place un environnement de développement, de staging et de production strictement séparés.
    • Réaliser un audit de sécurité (pentest) avant la première mise en production.
    • Mettre en place un monitoring applicatif (Sentry pour les erreurs, Grafana + Prometheus pour les métriques).
    • Configurer des alertes automatiques pour les métriques critiques (CPU > 80%, mémoire > 80%, temps de réponse > 3s).
    • Documenter toutes les décisions architecturales dans un ADR (Architecture Decision Record).
    • Mettre en place une politique de rotation des clés API et des secrets Docker.
    • Prévoir une formation des Administrateurs de chaque organisation avant la mise en service.
    • Planifier des revues de code systématiques pour les fonctionnalités critiques (pointage, sécurité).

PÉRIMÈTRE FONCTIONNEL, DÉPENDANCES ET SYNTHÈSE

25.1 Périmètre fonctionnel V1
Les fonctionnalités suivantes sont incluses dans le périmètre de la version 1 :
    • Authentification complète (connexion, déconnexion, réinitialisation, gestion sessions).
    • Multi-tenant avec isolation stricte des données.
    • Gestion des organisations, agences, départements, postes.
    • Gestion complète des employés, enseignants, managers, superviseurs.
    • Geofencing GPS avec zones multiples.
    • Pointage avec photo obligatoire (arrivée et départ).
    • Mode hors ligne avec synchronisation automatique.
    • Gestion des horaires (fixes, par équipe, personnalisés, enseignants).
    • Gestion des absences, retards et congés.
    • Journal d'audit complet et immuable.
    • Tableaux de bord par rôle avec KPI en temps réel.
    • Exports PDF, Excel, CSV.
    • Notifications (e-mail, in-app, push).
    • Assistant IA configurable.
    • Sauvegardes automatiques et manuelles.
    • PWA (installation, offline, notifications push).
    • Interface responsive (mobile, tablette, desktop).
25.2 Hors périmètre V1 (prévu V2+)
    • Module de facturation et abonnements en ligne.
    • Intégration avec logiciels de paie.
    • Reconnaissance faciale automatique.
    • Application mobile native iOS/Android.
    • Intégration badgeuse physique (RFID/NFC).
    • Module de gestion des performances RH.
    • Module e-learning.
25.3 Dépendances externes
Dépendance	Détail
Fournisseur SMTP	Envoi d'e-mails (SendGrid, Mailgun, ou SMTP propre).
Fournisseur IA	OpenAI, Anthropic, Mistral ou autre (configurable).
Fournisseur cartographique	OpenStreetMap / Leaflet.js (open source) ou Google Maps (payant).
Service CAPTCHA	hCaptcha ou Google reCAPTCHA.
Service SMS (optionnel)	Twilio ou équivalent.
Infrastructure serveur	VPS ou cloud (AWS, OVH, Hetzner, etc.) avec Ubuntu 22.04.
Registre Docker	Docker Hub ou registre privé pour les images.


— Fin du Cahier des Charges —
Document confidentiel — Version 1.0
