ANALYSE MÉTIER
Plateforme SaaS Intelligente de Gestion de Présence

Business Analysis — Référence complète pour conception, développement et tests
Version 1.0 — Document confidentiel
Champ	Valeur
Référence	AM-PRESENCE-SAAS-V1.0
Type de document	Analyse Métier (Business Analysis)
Date	2025
Statut	Approuvé pour développement
Auteur	Business Analyst Senior / Consultant SI
Projet	Plateforme SaaS de Gestion de Présence Multi-Tenant
Technologies	Python / Django / MySQL 8 / Bootstrap 5 / Docker
Audience	Comité de direction, Architectes, Développeurs, UX/UI, Testeurs

TABLE DES MATIÈRES

Chapitre	Contenu
Chapitre 1	Présentation Métier — Contexte, Objectifs, Enjeux, Problèmes, Bénéfices
Chapitre 2	Analyse des Parties Prenantes — Acteurs, Rôles, Responsabilités, Attentes
Chapitre 3	Analyse des Besoins — Fonctionnels, Métier, Organisationnels, Techniques, Réglementaires, Sécurité, Accessibilité, Performance
Chapitre 4	Analyse des Processus Métier — Création organisation, Pointage, GPS, Photo, Absences, Congés, IA, Exports...
Chapitre 5	Cartographie des Processus — Principaux, Secondaires, Support, Administration, Sécurité, IA
Chapitre 6	Analyse des Règles Métier — Identifiant, Description, Justification, Impact, Exceptions
Chapitre 7	Analyse des Contraintes Métier — Horaires, GPS, Organisationnelles, Légales, Sécurité, IA
Chapitre 8	Analyse des Données Métier — Entités, Cycle de vie, Propriétaire, Confidentialité
Chapitre 9	Analyse des Flux Métier — Échanges inter-acteurs, Informations, Déclencheurs
Chapitre 10	Analyse des Risques Métier — Organisationnels, Techniques, Fraude, Sécurité, GPS, IA
Chapitre 11	Analyse de la Valeur Métier — Bénéfices par acteur
Chapitre 12	Indicateurs Métier (KPI) — Définition, Calcul, Fréquence, Responsable
Chapitre 13	Glossaire Métier — Termes, Définitions, Abréviations

CHAPITRE 1 — PRÉSENTATION MÉTIER

1.1 Description du métier
La gestion de la présence du personnel est une fonction vitale de toute organisation employant des ressources humaines. Elle consiste à enregistrer, contrôler, analyser et rapporter les entrées et sorties du personnel sur les lieux de travail, à comparer ces données avec les horaires planifiés, à détecter les anomalies (absences, retards, départs anticipés, heures supplémentaires) et à fournir les éléments nécessaires aux décisions managériales et aux obligations légales.
Traditionnellement assurée par des pointeuses physiques, des feuilles de présence papier ou des tableurs, cette fonction est aujourd'hui confrontée à des exigences croissantes : dispersion géographique des équipes, multiplication des types de contrats, besoin de traçabilité en temps réel, prévention de la fraude, conformité réglementaire et analyse prédictive des comportements d'absence.
La plateforme SaaS de gestion de présence adresse l'ensemble de ces problématiques en proposant une solution numérique intelligente, géolocalisée, sécurisée et accessible depuis n'importe quel appareil connecté. Elle s'adresse à un spectre très large d'organisations : entreprises privées, établissements scolaires, universités, pharmacies, restaurants, cliniques et hôpitaux, organisations non gouvernementales, administrations publiques et associations.
La plateforme est conçue selon un modèle SaaS (Software as a Service) multi-tenant : une seule instance logicielle sert simultanément des centaines d'organisations clientes, chacune disposant de son propre espace de données parfaitement isolé des autres. Ce modèle garantit l'économie d'échelle pour l'éditeur et la sécurité des données pour les clients.
1.2 Contexte du projet
Le projet s'inscrit dans un contexte de transformation numérique accélérée des organisations. Les organisations de toutes tailles et de tous secteurs cherchent à remplacer leurs outils de gestion de présence obsolètes par des solutions modernes, mobiles et intelligentes. Plusieurs tendances de fond motivent ce projet :
    • Télétravail et mobilité : La pandémie de COVID-19 a profondément transformé les modes de travail. Les organisations gèrent désormais des équipes hybrides (présentiel + télétravail), des travailleurs itinérants et des équipes multi-sites. Les outils traditionnels ne permettent pas de gérer ces configurations.
    • Conformité réglementaire : Les législations du travail de nombreux pays imposent un enregistrement précis du temps de travail. Le non-respect de ces obligations expose les organisations à des sanctions légales et financières.
    • Fraude au pointage : Le 'buddy punching' (pointage par procuration) est une pratique frauduleuse coûteuse estimée à des milliards de dollars de pertes annuelles à l'échelle mondiale. Les solutions basées sur la simple saisie d'un code PIN ou d'une carte magnétique ne permettent pas de l'éliminer.
    • Analyse des données RH : Les organisations cherchent à transformer leurs données de présence en informations exploitables pour améliorer la gestion des ressources humaines, réduire l'absentéisme et optimiser la planification.
    • Exigences de traçabilité : Dans certains secteurs (santé, éducation, administrations publiques), la traçabilité des présences est une obligation légale ou réglementaire impliquant un audit trail complet et inaltérable.
1.3 Objectifs du projet
1.3.1 Objectifs primaires
    • OBJ-P01 — Éliminer la fraude au pointage : Rendre techniquement impossible le pointage par procuration grâce à la combinaison obligatoire de la géolocalisation GPS (l'employé est physiquement présent sur le lieu de travail) et de la photo en temps réel (l'employé est bien la personne qui pointe).
    • OBJ-P02 — Automatiser la gestion des présences : Remplacer les processus manuels (feuilles de présence, tableurs) par un système entièrement automatisé qui détecte, calcule et enregistre les présences, absences, retards et heures supplémentaires sans intervention humaine.
    • OBJ-P03 — Assurer une traçabilité complète et inaltérable : Enregistrer chaque événement (pointage, modification, validation, connexion) dans un journal d'audit immuable permettant toute vérification ultérieure.
    • OBJ-P04 — Permettre le pointage depuis n'importe quel appareil connecté : Rendre le pointage possible depuis un smartphone, une tablette ou un ordinateur, avec ou sans connexion Internet (mode hors ligne).
    • OBJ-P05 — Fournir une visibilité en temps réel : Permettre aux managers et administrateurs de voir instantanément qui est présent, absent ou en retard, depuis n'importe quel endroit.
1.3.2 Objectifs secondaires
    • OBJ-S01 — Centraliser la gestion RH de base : Intégrer dans un seul outil la gestion des absences, des congés, des justificatifs et des horaires, réduisant les outils fragmentés.
    • OBJ-S02 — Analyser et prédire les comportements d'absence : Utiliser l'intelligence artificielle pour détecter les patterns d'absentéisme, générer des alertes précoces et fournir des recommandations managériales.
    • OBJ-S03 — Servir des organisations de tous types et toutes tailles : Offrir une solution adaptée aussi bien à une école de 20 enseignants qu'à une entreprise de 500 employés, sans développement spécifique.
    • OBJ-S04 — Générer des rapports automatiques : Produire quotidiennement, hebdomadairement et mensuellement des rapports de présence prêts à l'emploi pour les RH et la direction.
    • OBJ-S05 — Respecter les réglementations de protection des données : Concevoir le système en conformité avec le RGPD et les législations locales applicables sur la vie privée.
1.4 Enjeux stratégiques
1.4.1 Enjeux pour l'éditeur de la plateforme
    • Enjeu commercial : Pénétrer un marché des logiciels RH en forte croissance avec un produit différenciant (géolocalisation + photo + IA + multi-secteur).
    • Enjeu technique : Concevoir une architecture suffisamment robuste pour supporter des centaines de tenants simultanément sans compromis sur les performances ni sur la sécurité.
    • Enjeu réglementaire : Assurer la conformité du produit aux différentes législations applicables dans les pays cibles (RGPD en Europe, lois locales dans les autres zones).
    • Enjeu de scalabilité : Bâtir une architecture qui peut croître (plus de tenants, plus d'employés, plus de fonctionnalités) sans refonte majeure.
1.4.2 Enjeux pour les organisations clientes
    • Enjeu financier : Réduire les coûts liés à l'absentéisme, à la fraude au pointage et à la gestion manuelle des présences (heures de traitement RH).
    • Enjeu légal : Respecter les obligations de suivi du temps de travail et disposer des preuves nécessaires en cas de litige social ou d'inspection du travail.
    • Enjeu managérial : Donner aux managers les outils pour prendre des décisions basées sur des données fiables et en temps réel.
    • Enjeu RH : Améliorer le bien-être des employés en assurant une gestion équitable et transparente des présences et des congés.
1.5 Problèmes actuels des organisations
1.5.1 Problèmes liés aux processus
Problème	Description et impact
Pointage par procuration (buddy punching)	Un employé demande à un collègue de pointer à sa place. Ce phénomène représente selon les études entre 1 et 5% de la masse salariale totale perdue en présences fictives.
Feuilles de présence papier	Les feuilles papier sont modifiables a posteriori, perdables, non agrégées automatiquement et nécessitent une saisie manuelle dans les systèmes RH ou de paie.
Tableurs non sécurisés	Les fichiers Excel circulent par e-mail, sont modifiables sans traçabilité et ne permettent aucune vérification en temps réel.
Absence de géolocalisation	Aucun outil traditionnel ne permet de vérifier que l'employé est physiquement présent sur son lieu de travail déclaré.
Calculs manuels et sources d'erreurs	Le calcul des heures supplémentaires, des retards cumulés et des soldes de congés est souvent effectué manuellement, source d'erreurs et de contestations.
Délais de traitement	Les responsables RH traitent les feuilles de présence avec plusieurs jours de retard, rendant toute réaction immédiate impossible.
Absence de vision consolidée multi-sites	Les organisations avec plusieurs sites gèrent des systèmes fragmentés par site, sans vue globale consolidée.
Manipulation des horloges	Des employés malintentionnés peuvent avancer l'heure de leur pointage en manipulant l'heure de leur téléphone.
1.5.2 Problèmes liés aux outils actuels
Outil	Limitations
Pointeuses physiques	Coût d'acquisition et de maintenance élevé. Espace physique requis. Fragilité. Impossibilité d'utiliser en télétravail ou sur site externe. Données non exportables facilement.
Badgeuses RFID/NFC	Le badge peut être confié à un autre employé (proxy). Nécessite une infrastructure physique par site. Coût d'installation important.
Applications mobiles de pointage simples	Pas de vérification GPS sérieuse. Pas de photo. Facilement contournables. Pas de gestion multi-tenant.
Logiciels RH complets	Très coûteux. Complexes à implémenter. Sur-dimensionnés pour les petites structures. La gestion de présence n'est souvent qu'un module parmi des dizaines d'autres.
Feuilles de calcul collaborative (Google Sheets)	Aucune sécurité. Pas de workflow. Pas d'automatisation. Pas d'audit trail.
1.6 Bénéfices attendus
1.6.1 Bénéfices opérationnels
    • Réduction de la fraude de 100% : La combinaison GPS + photo temps réel rend techniquement impossible le pointage par procuration ou à distance.
    • Gain de temps RH estimé à 80% : L'automatisation complète des calculs (retards, absences, heures sup., soldes de congés) élimine les tâches de saisie et de calcul manuels.
    • Réduction des erreurs de paie : Des données de présence précises et automatiques réduisent les erreurs de calcul de salaire liées aux absences et heures supplémentaires.
    • Disponibilité 24h/24 depuis n'importe où : L'accès web + PWA permet aux managers de consulter les présences depuis leur domicile, en déplacement ou depuis un autre site.
1.6.2 Bénéfices managériaux
    • Décision en temps réel : Les managers disposent d'un tableau de bord en temps réel pour prendre des décisions immédiates face aux absences non prévues.
    • Analyse prédictive : Le module IA prédit les pics d'absentéisme et permet d'anticiper les besoins en personnel supplémentaire.
    • Rapports automatiques : Des rapports hebdomadaires et mensuels sont générés automatiquement, sans travail de production.
1.6.3 Bénéfices légaux et réglementaires
    • Conformité du temps de travail : Des données précises et horodatées permettent de justifier le respect des durées légales de travail.
    • Protection en cas de litige : L'audit trail complet et inaltérable constitue une preuve légale en cas de contestation par un employé ou une inspection.
    • Conformité RGPD : La plateforme est conçue dès le départ pour respecter les obligations de protection des données personnelles.

CHAPITRE 2 — ANALYSE DES PARTIES PRENANTES

Ce chapitre identifie et analyse toutes les parties prenantes de la plateforme. Une partie prenante est tout individu, groupe ou organisation qui a un intérêt dans le projet, qui est impacté par ses résultats, ou qui peut influencer son développement et son utilisation.
2.1 Super Administrateur (Éditeur SaaS)
Le Super Administrateur est l'opérateur global de la plateforme. Il appartient à l'équipe de l'entreprise qui édite et exploite la plateforme SaaS. Il n'est rattaché à aucun tenant/organisation cliente.

2.1.1 Profil et responsabilités
Attribut	Détail
Profil type	Administrateur système ou ingénieur DevOps de l'entreprise éditrice du logiciel.
Responsabilités principales	Créer et gérer les organisations clientes (tenants). Surveiller l'état général de la plateforme. Gérer les abonnements et la facturation (V2). Assurer la disponibilité et les performances du système. Gérer les sauvegardes globales. Configurer les modèles IA disponibles.
Objectifs	Garantir la disponibilité et la performance de la plateforme pour tous les tenants. Onboarder rapidement de nouveaux clients. Résoudre les incidents techniques. Surveiller l'utilisation et la croissance de la plateforme.
Attentes vis-à-vis du système	Interface d'administration puissante avec vue globale. Journaux système complets. Alertes automatiques en cas d'incident. Outils de diagnostic rapide. Gestion simplifiée des tenants.
Contraintes	Ne peut jamais accéder aux données opérationnelles des tenants (employés, pointages, documents). Toutes ses actions sont auditées. Responsable légalement de la sécurité des données hébergées.
Interactions système	Crée et configure les tenants. Accède aux journaux globaux. Gère les sauvegardes. Configure les fournisseurs IA. Surveille les performances.
2.2 Administrateur d'Organisation
L'Administrateur d'Organisation est le responsable technique et fonctionnel du déploiement de la plateforme au sein de son organisation cliente. Il est désigné par la direction de l'organisation et dispose de tous les droits dans son espace.

2.2.1 Profil et responsabilités
Attribut	Détail
Profil type	Directeur RH, Responsable informatique, DG d'une petite structure, ou tout responsable désigné par la direction.
Responsabilités principales	Configurer l'organisation (agences, départements, postes). Créer et gérer les comptes utilisateurs. Configurer les horaires de travail. Valider les absences et justificatifs. Générer les rapports. Gérer les annonces internes. Configurer les paramètres IA.
Objectifs	Déployer la plateforme efficacement pour son organisation. Avoir une vision complète et en temps réel de la présence. Réduire la charge administrative liée à la gestion des présences. Produire des rapports précis pour la direction et les RH.
Attentes vis-à-vis du système	Interface complète et ergonomique. Tableaux de bord riches. Exports dans plusieurs formats. Notifications configurables. Personnalisation aux couleurs de l'organisation.
Contraintes	Limité aux données de son organisation. Ne peut pas accéder aux données d'une autre organisation. Responsable de la bonne utilisation du système par ses employés.
Interactions système	Configure tous les paramètres. Crée employés/managers. Consulte toutes les présences. Valide congés/justificatifs. Génère rapports. Publie annonces.
2.2.2 Sous-profils d'Administrateur
Sous-profil	Caractéristiques
Directeur RH (grande structure)	Accent sur les rapports, les statistiques RH et la conformité légale. Utilise principalement les fonctions d'analyse et d'export.
Responsable informatique	S'occupe principalement de la configuration technique (paramètres GPS, horaires, intégrations). Moins impliqué dans la validation RH.
Directeur / Gérant (PME)	Cumule les rôles. Gère tout seul la plateforme pour une équipe de 5 à 50 personnes. A besoin de la solution la plus simple possible.
Secrétaire de direction	Délégué par le directeur pour les tâches quotidiennes (validation congés, gestion des absences). Droits limités à certaines fonctions.
2.3 Manager
Le Manager gère une équipe opérationnelle. Son périmètre d'action est strictement limité aux employés qui lui sont rattachés. Il est le premier relais entre les employés et l'administration.

Attribut	Détail
Profil type	Chef d'équipe, responsable de service, chef de rayon, chef de département, coordinateur.
Responsabilités principales	Surveiller les présences de son équipe en temps réel. Valider les justificatifs d'absence. Approuver les demandes de congé (si délégué). Signaler les anomalies à l'Administrateur. Transmettre les informations à son équipe via les annonces.
Objectifs	Avoir une vue claire et immédiate sur la disponibilité de son équipe. Gérer efficacement les absences imprévues. Maintenir la productivité opérationnelle de son équipe.
Attentes	Interface simple et rapide. Alertes en temps réel sur les absences et retards. Accès depuis mobile. Historique facilement consultable.
Contraintes	Accès limité à son équipe uniquement. Ne peut pas modifier les horaires ou créer des comptes. Ne peut pas accéder aux données salariales.
Interactions	Reçoit des alertes. Valide ou rejette des demandes. Consulte les présences. Communique avec son équipe via annonces.
2.4 Superviseur
Le Superviseur est un rôle intermédiaire entre le Manager et l'Administrateur. Ses droits sont configurables par l'Administrateur. Il peut superviser plusieurs équipes ou un département entier.

Attribut	Détail
Profil type	Directeur de département, responsable de site, coordinateur régional.
Responsabilités	Superviser plusieurs équipes ou départements. Valider les demandes des managers. Générer des rapports de département. Recevoir des alertes agrégées pour son périmètre.
Objectifs	Vision agrégée sur plusieurs équipes. Pilotage du département ou du site. Coordination entre plusieurs managers.
Contraintes	Périmètre défini par l'Administrateur. Droits configurables.
2.5 Employé standard
L'Employé est l'utilisateur final le plus nombreux. Son interaction avec la plateforme est principalement limitée au pointage, à la consultation de ses données personnelles et aux demandes (congés, justificatifs).

Attribut	Détail
Profil type	Tout membre du personnel quel que soit son niveau hiérarchique ou son type de contrat.
Responsabilités	Pointer son arrivée et son départ aux heures planifiées. Justifier ses absences dans les délais requis. Déposer ses demandes de congé suffisamment à l'avance. Consulter et signaler toute anomalie dans ses données.
Objectifs	Pointage rapide et simple. Vision claire de ses soldes de congés. Suivi de ses demandes. Accès à ses historiques.
Attentes	Interface mobile simple. Pointage en moins de 10 secondes. Retour visuel immédiat après pointage. Notifications claires.
Contraintes	Ne peut pointer que depuis la zone GPS autorisée. Ne peut pas modifier ses pointages a posteriori. Ne peut pas voir les données des autres employés. Obligation de la photo en temps réel.
Anxiétés	Peur que la photo soit utilisée à mauvais escient. Peur d'être bloqué si le GPS ne fonctionne pas. Peur d'un retard comptabilisé par erreur.
2.6 Enseignant
L'Enseignant est une variante spécifique de l'employé, avec des particularités propres à son métier : horaires discontinus définis par emploi du temps, créneaux de cours variables selon les jours, absences uniquement pour les créneaux planifiés.

Attribut	Détail
Profil type	Enseignant du primaire, secondaire, universitaire, formateur, instructeur.
Spécificités	Horaires basés sur un emploi du temps (créneaux précis, non continus). Absent les jours sans cours sans que ce soit une absence à justifier. Peut avoir plusieurs créneaux le même jour. Pointe arrivée et départ par créneau.
Responsabilités	Pointer pour chaque créneau de cours. Signaler les cours annulés. Justifier les absences sur les créneaux planifiés.
Attentes	Voir clairement ses créneaux du jour. Pointage par créneau différencié. Ne pas recevoir d'alertes d'absence pour les jours sans cours.
2.7 Responsable RH
Dans les grandes organisations, le Responsable RH peut exister comme rôle distinct de l'Administrateur. Il n'a généralement pas accès aux paramètres techniques mais dispose de droits étendus sur les données RH.

Attribut	Détail
Profil type	Chargé de ressources humaines, gestionnaire de paie, DRH adjoint.
Responsabilités	Valider les absences et justificatifs. Gérer les soldes de congés. Produire les rapports pour la paie. Archiver les documents RH. Gérer les dossiers disciplinaires liés aux absences répétées.
Attentes	Exports précis et formatés pour la paie. Historiques complets et filtrables. Alertes sur les absences répétées. Gestion des documents justificatifs.
2.8 Directeur / Direction Générale
La Direction Générale est une partie prenante consommatrice de rapports et de tableaux de bord. Elle n'interagit pas directement avec l'opérationnel de la plateforme mais est le destinataire principal des synthèses managériales.

Attribut	Détail
Attentes	Tableaux de bord exécutifs. KPI clés en temps réel. Rapports de synthèse mensuels automatiques. Vision des tendances d'absentéisme. ROI de la solution.
Interactions	Consultation des tableaux de bord de haut niveau. Réception des rapports automatiques par e-mail. Décisions basées sur les indicateurs fournis par la plateforme.
2.9 Auditeur / Inspecteur
L'Auditeur peut être interne (auditeur interne de l'organisation) ou externe (inspection du travail, commissaire aux comptes, organisme de certification). Il a besoin d'accéder aux données historiques pour vérifier la conformité.

Attribut	Détail
Attentes	Journal d'audit complet et inaltérable. Exports des présences sur des périodes définies. Preuves de la conformité des horaires de travail. Traçabilité des modifications.
Mode d'accès	Accès en lecture seule sur demande de l'Administrateur. Export des données pour la période auditée.
2.10 Service Informatique de l'Organisation
Dans les organisations disposant d'un service informatique interne, celui-ci peut jouer un rôle dans le déploiement (configuration réseau, SSO) et le support de niveau 1 pour les utilisateurs de son organisation.

Attribut	Détail
Responsabilités	Support de premier niveau pour les utilisateurs (problèmes de connexion, GPS, caméra). Liaison avec l'éditeur pour les problèmes techniques. Configuration des postes pour l'accès à la plateforme.
Attentes	Documentation technique claire. API documentée. Logs d'erreurs accessibles.
2.11 Matrice des interactions entre parties prenantes
Source	Cible	Nature de l'interaction	Canal
Super Admin	Administrateur	Crée le compte, configure le tenant, suspend si nécessaire.	Plateforme SaaS
Administrateur	Manager	Crée le compte, définit le périmètre, reçoit les alertes escaladées.	Interface admin
Administrateur	Employé	Crée le compte, gère les horaires, valide les congés/absences.	Interface admin
Manager	Employé	Reçoit alertes, valide demandes, consulte présences.	Interface manager
Employé	Système	Pointe, demande congés, soumet justificatifs.	Interface employé / PWA
Administrateur	Système IA	Configure l'IA, consulte les rapports, interagit avec l'assistant.	Interface admin + IA
Manager	Système IA	Reçoit recommandations, consulte rapports équipe.	Interface manager
Système	Employé	Notifie les confirmations, absences détectées, congés validés.	E-mail + Push + In-app
Système	Manager	Notifie absences, retards, demandes en attente.	E-mail + Push + In-app
Auditeur	Système	Consultation lecture seule des journaux et exports.	Interface admin (accès restreint)

CHAPITRE 3 — ANALYSE DES BESOINS

Ce chapitre identifie et documente de façon exhaustive tous les besoins identifiés pour la plateforme, classés par catégorie. Chaque besoin est décrit avec son contexte, sa justification et son importance relative.
3.1 Besoins fonctionnels
3.1.1 Besoins liés à l'authentification et à la sécurité d'accès
Identifiant	Description	Priorité
BF-AUTH-01	Les utilisateurs doivent pouvoir s'authentifier par e-mail et mot de passe. L'authentification doit être sécurisée contre le brute force avec blocage automatique après N tentatives. La session doit expirer après inactivité. L'identifiant est l'adresse e-mail, insensible à la casse.	CRITIQUE
BF-AUTH-02	Le système doit permettre la réinitialisation sécurisée du mot de passe par lien e-mail. Le lien doit expirer après 30 minutes. Un seul lien valide peut exister à la fois. Toute réinitialisation invalide toutes les sessions actives.	CRITIQUE
BF-AUTH-03	La première connexion doit forcer le changement du mot de passe temporaire. L'utilisateur ne peut accéder à aucune autre fonctionnalité tant que ce changement n'est pas effectué.	CRITIQUE
BF-AUTH-04	Le système doit offrir une gestion des sessions multi-appareils. L'utilisateur voit toutes ses sessions actives et peut en révoquer à distance.	HAUTE
BF-AUTH-05	Les mots de passe doivent respecter des règles de complexité configurables par l'Administrateur. Les mots de passe doivent expirer selon une durée configurable. L'historique des N derniers mots de passe doit être mémorisé.	HAUTE
3.1.2 Besoins liés au pointage
Identifiant	Description	Priorité
BF-POINT-01	L'employé doit pouvoir pointer son arrivée depuis un smartphone, tablette ou ordinateur via une interface web responsive / PWA. Le pointage doit être possible en moins de 10 secondes depuis l'ouverture de l'interface.	CRITIQUE
BF-POINT-02	Le système doit vérifier la position GPS de l'employé avant d'autoriser le pointage. Si l'employé est hors de la zone autorisée (rayon configurable par agence), le pointage doit être refusé avec message explicatif.	CRITIQUE
BF-POINT-03	Le pointage doit obligatoirement inclure une photo prise en temps réel par la caméra frontale. L'utilisation de la galerie photo doit être techniquement impossible. La photo doit être capturée automatiquement sans étape supplémentaire pour l'utilisateur.	CRITIQUE
BF-POINT-04	Le système doit fonctionner en mode hors ligne. Si l'Internet est indisponible, le pointage doit être enregistré localement et synchronisé automatiquement dès la reconnexion.	HAUTE
BF-POINT-05	Le système doit calculer automatiquement le statut de chaque pointage : à l'heure, retard, départ anticipé, heures supplémentaires, hors horaire.	CRITIQUE
BF-POINT-06	L'Administrateur et le Manager doivent pouvoir corriger un pointage erroné. Toute correction doit être tracée dans l'audit trail avec les valeurs avant et après.	HAUTE
BF-POINT-07	Le système doit détecter et rejeter les tentatives de falsification GPS (GPS simulé, mock location).	CRITIQUE
BF-POINT-08	Les enseignants doivent pouvoir pointer par créneau de cours. Chaque créneau génère un pointage d'arrivée et un pointage de départ distincts.	HAUTE
3.1.3 Besoins liés à la gestion des organisations et agences
Identifiant	Description	Priorité
BF-ORG-01	Le Super Administrateur doit pouvoir créer une nouvelle organisation avec toutes ses informations (nom, type, pays, fuseau horaire, langue, logo, couleurs, Administrateur initial).	CRITIQUE
BF-ORG-02	L'Administrateur doit pouvoir créer et gérer des agences avec coordonnées GPS, rayon de geofencing, horaires et responsable.	CRITIQUE
BF-ORG-03	L'Administrateur doit pouvoir créer des départements, des postes et des équipes au sein de son organisation.	HAUTE
BF-ORG-04	L'Administrateur doit pouvoir personnaliser l'apparence de son espace (logo, couleurs primaire et secondaire).	MOYENNE
BF-ORG-05	Le Super Administrateur doit pouvoir suspendre et réactiver une organisation. La suspension doit être instantanée et bloquer tous les accès au tenant.	CRITIQUE
3.1.4 Besoins liés à la gestion des employés
Identifiant	Description	Priorité
BF-EMP-01	L'Administrateur doit pouvoir créer des comptes employés avec toutes leurs informations (personnelles, professionnelles, contrat). La création déclenche l'envoi automatique des accès par e-mail.	CRITIQUE
BF-EMP-02	L'Administrateur doit pouvoir importer une liste d'employés via CSV/Excel avec rapport d'erreurs ligne par ligne.	HAUTE
BF-EMP-03	L'Administrateur doit pouvoir affecter les employés à des agences, départements, postes et horaires.	CRITIQUE
BF-EMP-04	Les employés doivent pouvoir consulter et mettre à jour leurs informations personnelles non critiques (photo, téléphone, langue).	HAUTE
BF-EMP-05	L'Administrateur doit pouvoir suspendre, archiver ou supprimer des comptes employés. L'historique des données doit être conservé.	HAUTE
3.1.5 Besoins liés aux horaires
Identifiant	Description	Priorité
BF-HOR-01	Le système doit supporter plusieurs types d'horaires : fixe (même plage chaque jour), par équipe (rotation), personnalisé (individuel), enseignant (emploi du temps par créneau).	CRITIQUE
BF-HOR-02	Le système doit gérer les horaires de nuit chevauchant minuit en rattachant correctement les pointages à la bonne plage.	HAUTE
BF-HOR-03	Les horaires doivent être affectables à plusieurs niveaux (individu, poste, département, agence) avec un ordre de priorité défini.	CRITIQUE
BF-HOR-04	Les changements d'horaire doivent être historisés. Le système doit utiliser l'horaire correct à chaque date de pointage.	HAUTE
3.1.6 Besoins liés aux absences, retards et congés
Identifiant	Description	Priorité
BF-ABS-01	Le système doit détecter automatiquement les absences non justifiées à l'expiration de la fenêtre de pointage.	CRITIQUE
BF-ABS-02	Les employés doivent pouvoir soumettre des justificatifs d'absence avec pièces jointes. Le responsable valide ou rejette avec commentaire.	HAUTE
BF-ABS-03	Les employés doivent pouvoir soumettre des demandes de congé. Le responsable valide ou rejette. Le solde est automatiquement géré.	HAUTE
BF-ABS-04	Le système doit gérer les jours fériés et les exclure des calculs d'absence et de congé.	HAUTE
BF-ABS-05	Le système doit calculer automatiquement les retards, les départs anticipés et les heures supplémentaires.	CRITIQUE
3.1.7 Besoins liés aux rapports et exports
Identifiant	Description	Priorité
BF-RAP-01	Le système doit générer des rapports de présence par employé, département, agence et période.	HAUTE
BF-RAP-02	Les rapports doivent être exportables en PDF, Excel (.xlsx) et CSV.	HAUTE
BF-RAP-03	Des rapports automatiques (quotidien, hebdomadaire, mensuel) doivent être générés et envoyés par e-mail.	HAUTE
BF-RAP-04	Les tableaux de bord doivent afficher les KPI en temps réel avec graphiques interactifs.	HAUTE
3.2 Besoins métier
Identifiant	Description	Priorité
BM-01	L'organisation doit pouvoir prouver à tout moment la présence effective de ses employés sur leur lieu de travail (photo + GPS + horodatage).	CRITIQUE
BM-02	La direction doit disposer d'un tableau de bord exécutif avec les KPI de présence en temps réel pour piloter ses équipes.	HAUTE
BM-03	Les RH doivent pouvoir produire les données de présence nécessaires au calcul de la paie sans intervention manuelle supplémentaire.	HAUTE
BM-04	Les managers doivent être alertés immédiatement en cas d'absence ou de retard significatif pour prendre des mesures opérationnelles.	HAUTE
BM-05	L'organisation doit pouvoir gérer des équipes dispersées sur plusieurs sites depuis une seule interface centralisée.	HAUTE
BM-06	L'organisation doit pouvoir adapter la plateforme à ses spécificités sectorielles (horaires enseignants, rotations hôpitaux, services restaurants, etc.).	HAUTE
BM-07	L'organisation doit disposer d'un historique complet des présences sur plusieurs années pour répondre aux obligations légales.	HAUTE
BM-08	Les données de présence doivent être fiables et incontestables pour être utilisées en cas de litige social.	CRITIQUE
3.3 Besoins organisationnels
Identifiant	Description	Priorité
BO-01	La plateforme doit pouvoir être déployée dans n'importe quelle organisation sans développement spécifique. La configuration doit couvrir tous les paramètres métier.	CRITIQUE
BO-02	La plateforme doit s'adapter à la structure hiérarchique de chaque organisation (agences, départements, équipes, postes).	HAUTE
BO-03	La plateforme doit supporter plusieurs langues et plusieurs fuseaux horaires pour les organisations internationales.	HAUTE
BO-04	La plateforme doit pouvoir être personnalisée visuellement aux couleurs et au logo de chaque organisation.	MOYENNE
BO-05	Les rôles et permissions doivent être flexibles et configurables par l'Administrateur pour s'adapter aux particularités organisationnelles.	HAUTE
BO-06	La plateforme doit permettre une montée en charge progressive (de 5 à 5000 employés) sans changement d'outil.	HAUTE
3.4 Besoins techniques
Identifiant	Description	Priorité
BT-01	La plateforme doit être développée avec Python/Django (backend), Bootstrap 5 / JavaScript (frontend), MySQL 8 (base de données), Docker (conteneurisation).	CRITIQUE
BT-02	L'architecture doit être multi-tenant avec isolation stricte des données par organisation.	CRITIQUE
BT-03	La plateforme doit fonctionner comme une PWA (Progressive Web App) installable sur smartphone, tablette et desktop.	HAUTE
BT-04	Le code doit être versionné sur GitHub avec un pipeline CI/CD pour les tests et déploiements.	HAUTE
BT-05	Le système doit utiliser Redis pour le cache et Celery pour les tâches asynchrones (exports, notifications, synchronisation).	HAUTE
BT-06	Toutes les communications doivent être chiffrées en TLS 1.2 minimum.	CRITIQUE
BT-07	L'application doit charger en moins de 2 secondes pour 95% des requêtes.	HAUTE
BT-08	Le système doit supporter 500 utilisateurs simultanés sans dégradation des performances.	HAUTE
3.5 Besoins réglementaires
Identifiant	Description	Priorité
BR-01	La plateforme doit être conforme au RGPD. Les données personnelles doivent être collectées avec consentement, protégées, portables et supprimables sur demande.	CRITIQUE
BR-02	Les durées de conservation des données doivent être configurables et respecter les obligations légales locales.	HAUTE
BR-03	Les données de présence doivent être suffisamment précises pour justifier le respect des durées légales de travail (durée maximale journalière, repos hebdomadaire, etc.).	HAUTE
BR-04	Un registre des traitements de données doit être maintenu conformément au RGPD.	HAUTE
BR-05	L'organisation doit pouvoir exporter toutes les données d'un employé sur demande (droit à la portabilité RGPD).	HAUTE
BR-06	L'organisation doit pouvoir supprimer toutes les données personnelles d'un employé sur demande (droit à l'oubli RGPD), dans le respect des obligations de conservation.	HAUTE
3.6 Besoins de sécurité
Identifiant	Description	Priorité
BS-01	La plateforme doit résister aux attaques du Top 10 OWASP : injection SQL, XSS, CSRF, clickjacking, brute force, session hijacking, etc.	CRITIQUE
BS-02	Les mots de passe doivent être hachés avec Argon2id.	CRITIQUE
BS-03	Le module de géolocalisation doit détecter et rejeter les GPS simulés.	CRITIQUE
BS-04	Toutes les actions sensibles doivent être enregistrées dans un journal d'audit inaltérable.	CRITIQUE
BS-05	Les fichiers uploadés doivent être validés, stockés hors de la racine web et scannés (antivirus recommandé).	HAUTE
BS-06	Les cookies de session doivent être httpOnly, Secure et SameSite=Strict.	CRITIQUE
BS-07	Les en-têtes HTTP de sécurité doivent être configurés (CSP, HSTS, X-Frame-Options, X-Content-Type-Options).	HAUTE
BS-08	Un audit de sécurité (pentest) doit être réalisé avant la mise en production.	HAUTE
3.7 Besoins d'accessibilité
Identifiant	Description	Priorité
BAC-01	L'interface doit respecter le niveau AA des WCAG 2.1 pour être accessible aux personnes en situation de handicap.	HAUTE
BAC-02	Les contrastes de couleurs doivent respecter un ratio minimum de 4.5:1.	HAUTE
BAC-03	L'application doit être navigable au clavier (tabulation, touches directionnelles).	HAUTE
BAC-04	Les images et icônes fonctionnelles doivent avoir des attributs alt descriptifs.	HAUTE
BAC-05	L'interface doit être compatible avec les lecteurs d'écran (NVDA sur Windows, VoiceOver sur iOS/macOS).	MOYENNE
BAC-06	L'interface doit supporter l'affichage RTL (de droite à gauche) pour la langue arabe.	HAUTE
BAC-07	Le bouton de pointage doit avoir une taille minimale de 44x44 pixels pour être accessible sur tactile.	HAUTE
3.8 Besoins de performance
Identifiant	Description	Priorité
BP-01	95% des pages doivent se charger en moins de 2 secondes sur une connexion 4G standard.	HAUTE
BP-02	Le processus complet de pointage (du clic au bouton à la confirmation d'enregistrement) doit être réalisé en moins de 5 secondes.	HAUTE
BP-03	L'acquisition GPS doit être réalisée en moins de 10 secondes (timeout paramétrable).	HAUTE
BP-04	Le système doit supporter 500 utilisateurs simultanés sans dégradation mesurable des performances.	HAUTE
BP-05	Les exports (PDF, Excel) de rapports mensuels doivent être générés en moins de 30 secondes (asynchrone acceptable).	MOYENNE
BP-06	La base de données doit répondre en moins de 100ms pour 95% des requêtes avec des index appropriés.	HAUTE
BP-07	L'application PWA doit fonctionner en mode hors ligne sans dégradation de l'interface (hors fonctionnalités réseau).	HAUTE
BP-08	La disponibilité de la plateforme doit être d'au moins 99.5% par mois hors maintenance planifiée.	HAUTE

CHAPITRE 4 — ANALYSE DES PROCESSUS MÉTIER

Ce chapitre décrit de façon exhaustive chaque processus métier de la plateforme. Pour chaque processus, nous décrivons les objectifs, les acteurs impliqués, les préconditions, le déroulement étape par étape, les décisions, les validations, les exceptions et le résultat final. Ces descriptions serviront de base directe à la conception des diagrammes BPMN, des cas d'utilisation UML et des spécifications de développement.
4.1 Processus d'onboarding d'une nouvelle organisation
PM-01 — Création et activation d'une nouvelle organisation cliente
Identifiant	PM-01
Objectif	Créer un nouveau tenant opérationnel avec son Administrateur initial en moins de 15 minutes.
Déclencheur	Une nouvelle organisation signe un abonnement avec l'éditeur SaaS. Le Super Administrateur reçoit la confirmation et initie le processus.
Acteurs	Super Administrateur (initiateur)
Administrateur d'organisation (destinataire des accès)
Système (exécutant automatique)
Préconditions	Le Super Administrateur est authentifié.
L'e-mail de l'Administrateur initial de l'organisation est disponible et valide.
Le nom de l'organisation est unique dans le système.
Étape 1 — Saisie des informations	Le Super Admin remplit le formulaire de création : nom légal, nom commercial, type d'organisation, secteur, pays, ville, adresse, téléphone, e-mail, fuseau horaire, langue, format date/heure.
Étape 2 — Configuration visuelle	Le Super Admin ou l'Administrateur initial configure le logo (PNG/JPG, max 2 Mo) et les couleurs (primaire et secondaire en hexadécimal).
Étape 3 — Définition de l'Administrateur initial	Saisie du nom, prénom, e-mail et téléphone du premier Administrateur. L'e-mail doit être unique sur toute la plateforme.
Étape 4 — Validation et création	Le système génère un UUID tenant unique, crée l'espace de données isolé, génère un slug URL unique, crée le compte Administrateur avec un mot de passe temporaire aléatoire sécurisé.
Étape 5 — Notification	Un e-mail de bienvenue est envoyé à l'Administrateur initial contenant : URL de connexion, identifiant (e-mail), mot de passe temporaire, lien vers la documentation d'onboarding.
Étape 6 — Première connexion Administrateur	L'Administrateur se connecte avec les accès temporaires et est redirigé vers la page de changement de mot de passe obligatoire. Après changement, il accède au wizard de configuration initiale.
Décisions clés	Si l'e-mail existe déjà : blocage avec message d'erreur, proposition de modification.
Si le slug existe déjà : suggestion automatique de slug alternatif.
Si le logo ne respecte pas les dimensions : avertissement et redimensionnement automatique.
Exceptions	E-mail invalide : validation côté client et serveur.
Problème d'envoi e-mail : le Super Admin peut re-déclencher manuellement l'envoi.
Timeout de création : retry automatique x3 avec journalisation.
Postconditions	L'organisation existe dans le système avec statut 'Active'.
L'Administrateur dispose d'accès fonctionnels.
L'espace de données est vierge et prêt à être configuré.
L'événement est enregistré dans le journal d'audit global.
Résultat final	Organisation opérationnelle en moins de 5 minutes, Administrateur notifié et pouvant se connecter immédiatement.

PM-02 — Configuration initiale de l'organisation par l'Administrateur
Identifiant	PM-02
Objectif	Configurer complètement l'organisation pour la rendre opérationnelle.
Déclencheur	Première connexion de l'Administrateur après réception de ses accès.
Acteurs	Administrateur (initiateur et exécutant)
Système (assistant et validateur)
Préconditions	L'organisation existe dans le système.
L'Administrateur a effectué son premier changement de mot de passe.
Étape 1 — Configuration générale	L'Administrateur confirme et complète les informations de l'organisation (informations légales, coordonnées, fuseau horaire, langue, formats).
Étape 2 — Configuration des paramètres de pointage	Définition de la tolérance de retard (défaut : 5 min), tolérance de départ anticipé, seuil heures supplémentaires, autorisation du mode hors ligne, rayon GPS par défaut, durée de session, délai d'inactivité.
Étape 3 — Création des agences	L'Administrateur crée au minimum une agence avec : nom, adresse, coordonnées GPS (obtenues via carte interactive), rayon de geofencing.
Étape 4 — Création des départements	Création des structures organisationnelles (départements, services).
Étape 5 — Création des postes	Définition des postes de travail disponibles.
Étape 6 — Création des horaires	Définition des horaires de travail : horaires fixes par jour, rotations par équipe, horaires personnalisés.
Étape 7 — Création des comptes utilisateurs	Création des comptes managers, superviseurs et employés avec affectation aux agences, départements, postes et horaires.
Étape 8 — Configuration IA	Sélection du fournisseur IA (si activé par Super Admin), saisie de la clé API, test de connexion.
Étape 9 — Configuration des notifications	Paramétrage des notifications (absences, retards, congés) par canal (e-mail, push, SMS).
Décisions clés	Si aucune agence créée : blocage des fonctionnalités nécessitant une agence.
Si aucun horaire créé : avertissement, les employés sans horaire ne peuvent pas pointer.
Postconditions	L'organisation est entièrement configurée.
Les employés peuvent se connecter et pointer.
Le tableau de bord de l'Administrateur affiche les données en temps réel.
Résultat final	Organisation pleinement opérationnelle.

4.2 Processus de pointage
PM-03 — Pointage d'arrivée d'un employé
Identifiant	PM-03
Objectif	Enregistrer de façon sécurisée et incontestable l'arrivée d'un employé sur son lieu de travail.
Déclencheur	L'employé souhaite enregistrer son arrivée et ouvre l'interface de pointage depuis son appareil.
Acteurs	Employé (initiateur)
Système (exécutant et validateur)
Navigateur/GPS (capteur)
Caméra (capteur)
Préconditions	L'employé dispose d'un compte actif.
L'organisation est active (non suspendue).
L'appareil dispose d'un GPS fonctionnel et d'une caméra.
L'employé a accordé les permissions GPS et caméra au navigateur.
Un horaire est affecté à l'employé pour cette date.
Pas de pointage d'arrivée déjà enregistré pour la plage horaire courante.
Vérification 1 — Session	Le système vérifie que la session est valide. Si non : redirection vers la page de connexion.
Vérification 2 — Statut compte	Le système vérifie que le compte est actif. Si suspendu : message 'Compte suspendu, contactez votre administrateur.'
Vérification 3 — Statut organisation	Le système vérifie que l'organisation n'est pas suspendue.
Vérification 4 — Permissions GPS	Le système demande la permission GPS si non encore accordée. Si refusée : message avec instructions d'activation.
Vérification 5 — Acquisition GPS	Demande avec enableHighAccuracy:true, timeout 15s. Si timeout : message 'GPS indisponible, réessayez en étant à l'extérieur ou près d'une fenêtre.'
Vérification 6 — Zone géographique	Calcul de la distance (formule Haversine) entre position actuelle et centre de chaque zone autorisée. Si distance > rayon + tolérance : refus avec affichage de la distance et de la zone requise.
Vérification 7 — GPS simulé	Vérification de l'attribut isMock. Si GPS simulé détecté : refus et alerte Administrateur.
Vérification 8 — Fenêtre horaire	Vérification que l'heure actuelle est dans la fenêtre de pointage autorisée.
Vérification 9 — Doublon	Vérification qu'aucun pointage d'arrivée n'a déjà été enregistré pour cette plage.
Étape A — Activation caméra	La caméra frontale est activée. Un aperçu en temps réel est affiché. Un compte à rebours de 3 secondes s'affiche. La photo est capturée automatiquement (JPEG, qualité 0.85, max 640x480px).
Étape B — Confirmation utilisateur	L'employé voit la photo capturée. Il peut demander une nouvelle capture. Il confirme en cliquant sur 'Valider le pointage'.
Étape C — Envoi serveur	Les données sont envoyées en HTTPS POST : coordonnées GPS, précision, photo (base64 ou multipart), heure client, user-agent, IP.
Étape D — Traitement serveur	Re-validation de toutes les vérifications côté serveur.
Calcul du statut (À l'heure / Retard / Hors horaire).
Calcul du nombre de minutes de retard si applicable.
Sauvegarde en base de données avec tous les métadonnées.
Déclenchement des notifications si retard détecté.
Enregistrement dans le journal d'audit.
Étape E — Confirmation	L'interface affiche : 'Arrivée enregistrée — [HH:MM]'. En cas de retard : 'Arrivée enregistrée avec un retard de N minutes.'
Mode hors ligne	Si pas de connexion : données stockées en IndexedDB (chiffrées), badge 'Hors ligne' affiché. Synchronisation automatique à la reconnexion.
Exceptions	GPS non disponible → message + instructions.
Caméra non disponible → message + instructions.
Hors zone GPS → message avec distance et zone requise.
Hors fenêtre horaire → message avec horaire attendu.
Erreur serveur 5xx → tentative de synchronisation offline.
Session expirée → redirection vers login.
Postconditions	Pointage d'arrivée enregistré en base de données.
Statut calculé et stocké.
Notifications envoyées si retard.
Journal d'audit mis à jour.
Tableau de bord mis à jour en temps réel.
Résultat final	Arrivée de l'employé enregistrée, visible immédiatement par le manager et l'administrateur.

PM-04 — Pointage de départ d'un employé
Identifiant	PM-04
Objectif	Enregistrer le départ de l'employé et calculer la durée de présence effective.
Déclencheur	L'employé quitte son lieu de travail et souhaite enregistrer son départ.
Acteurs	Employé (initiateur)
Système (exécutant)
Préconditions	Un pointage d'arrivée existe pour la plage horaire courante.
Même préconditions que PM-03.
Déroulement	Identique au PM-03 mais avec type DEPART. Le système calcule la durée de présence (heure départ − heure arrivée). Le système calcule les heures supplémentaires et les départs anticipés.
Calculs automatiques	Durée de présence = heure départ − heure arrivée.
Départ anticipé = heure fin prévue − heure départ − tolérance (si positif).
Heures supplémentaires = heure départ − heure fin prévue − seuil (si positif).
Résultat final	Départ enregistré, durée de présence calculée, statut mis à jour.

PM-05 — Synchronisation des pointages hors ligne
Identifiant	PM-05
Objectif	Synchroniser de façon sécurisée les pointages effectués sans connexion Internet.
Déclencheur	La connexion Internet est rétablie après une période de déconnexion pendant laquelle des pointages ont été effectués.
Acteurs	Service Worker (initiateur automatique)
Système serveur (exécutant et validateur)
Préconditions	Des pointages sont stockés dans IndexedDB.
La connexion Internet est rétablie.
Étape 1	Le Service Worker détecte la reconnexion via l'événement 'online'.
Étape 2	Le Service Worker lit tous les pointages en attente depuis IndexedDB.
Étape 3	Pour chaque pointage, le système vérifie : délai depuis pointage vs délai max configuré, cohérence des données GPS, validité de la session.
Étape 4	Si délai dépassé : pointage marqué EN_ATTENTE_VALIDATION pour contrôle humain.
Étape 5	Si GPS invalide à la re-vérification : pointage marqué EN_ATTENTE_VALIDATION.
Étape 6	Pointage valide : enregistrement normal en base de données.
Étape 7	Notification à l'employé (push) : 'Vos pointages hors ligne ont été synchronisés.'
Étape 8	Suppression des données de IndexedDB après synchronisation réussie.
Exceptions	Session expirée à la synchronisation : demande de reconnexion à l'employé.
Pointage déjà synchronisé (doublon) : ignoré avec log.
Erreur serveur : retry avec backoff exponentiel.
Postconditions	Tous les pointages hors ligne sont en base de données ou en attente de validation.
IndexedDB nettoyé.
L'employé et le manager sont notifiés.

4.3 Processus de gestion des absences
PM-06 — Détection automatique d'une absence
Identifiant	PM-06
Objectif	Détecter automatiquement chaque absence non justifiée et déclencher les alertes appropriées.
Déclencheur	Tâche Celery planifiée s'exécutant toutes les 15 minutes pendant les heures ouvrables.
Acteurs	Système Celery (exécutant automatique)
Administrateur (destinataire alerte)
Manager (destinataire alerte)
Employé (destinataire notification)
Logique de détection	Pour chaque employé devant être présent à l'heure H selon son horaire :
Vérifier si un pointage d'arrivée existe dans la fenêtre de pointage autorisée.
Si aucun pointage et fenêtre expirée : créer un enregistrement d'absence automatique.
Vérifier que ce n'est pas un jour férié ou un jour de congé approuvé.
Vérifier que l'employé n'est pas en statut 'En congé'.
Notifications déclenchées	Notification immédiate au Manager de l'employé (push + in-app).
Notification à l'Administrateur (in-app, e-mail selon configuration).
Notification à l'employé : 'Absence enregistrée pour aujourd'hui. Vous pouvez soumettre un justificatif.'
Exceptions	Jour férié : pas d'absence enregistrée.
Congé approuvé : pas d'absence enregistrée.
Employé suspendu ou archivé : pas de traitement.
Créneau enseignant non planifié : pas d'absence.
Postconditions	Absence enregistrée en base de données avec statut NON_JUSTIFIEE.
Notifications envoyées.
Tableau de bord mis à jour.
Journal d'audit mis à jour.

PM-07 — Soumission et validation d'un justificatif d'absence
Identifiant	PM-07
Objectif	Permettre à l'employé de justifier une absence et au responsable de valider ou rejeter le justificatif.
Déclencheur	L'employé reçoit une notification d'absence ou constate une absence dans son historique.
Acteurs	Employé (initiateur)
Manager / Administrateur (validateur)
Système (exécutant)
Préconditions	Une absence est enregistrée pour l'employé.
L'employé est actif.
Le délai de soumission de justificatif n'est pas dépassé (configurable).
Étape 1 — Sélection de l'absence	L'employé accède à son historique et sélectionne l'absence à justifier.
Étape 2 — Saisie du justificatif	L'employé sélectionne le motif (liste configurable), ajoute un commentaire, joint le ou les fichiers justificatifs (max 5 Mo chacun, formats PDF/JPG/PNG acceptés).
Étape 3 — Soumission	L'employé soumet la demande. Le système enregistre la demande avec statut EN_ATTENTE.
Étape 4 — Notification du responsable	Le Manager et l'Administrateur reçoivent une notification : 'Nouveau justificatif d'absence soumis par [Prénom Nom].'
Étape 5 — Consultation	Le Manager consulte la demande avec les pièces jointes dans son interface.
Étape 6 — Décision	Le Manager approuve (justificatif accepté, absence marquée JUSTIFIEE) ou rejette (justificatif refusé, absence reste NON_JUSTIFIEE) avec commentaire obligatoire.
Étape 7 — Notification à l'employé	L'employé reçoit la décision par notification (e-mail + push).
Exceptions	Fichier trop volumineux : erreur avec message de limite.
Format non supporté : erreur avec liste des formats acceptés.
Délai dépassé : formulaire non disponible, contacter l'Administrateur.
Postconditions	Absence mise à jour avec le statut correspondant.
Pièces jointes stockées de façon sécurisée.
Historique des demandes conservé.

4.4 Processus de gestion des congés
PM-08 — Demande de congé par un employé
Identifiant	PM-08
Objectif	Permettre à l'employé de soumettre une demande de congé et suivre son traitement jusqu'à la décision.
Déclencheur	L'employé souhaite poser des jours de congé et accède au formulaire de demande.
Acteurs	Employé (initiateur)
Manager / Administrateur (décideur)
Système (exécutant et calculateur)
Préconditions	L'employé est actif.
Un ou plusieurs types de congés sont configurés.
La demande est soumise au moins N jours à l'avance (N configurable, défaut 3).
Étape 1 — Accès formulaire	L'employé accède au formulaire de demande de congé depuis son tableau de bord.
Étape 2 — Sélection type	L'employé sélectionne le type de congé (liste configurée par l'Administrateur).
Étape 3 — Sélection dates	L'employé sélectionne la date de début et la date de fin. Le calendrier affiche les jours fériés et les congés déjà posés.
Étape 4 — Calcul automatique	Le système calcule automatiquement le nombre de jours ouvrables (hors week-ends et jours fériés) et affiche l'impact sur le solde.
Étape 5 — Vérification solde	Si le solde est insuffisant : avertissement. Si l'organisation n'autorise pas les congés par anticipation : blocage.
Étape 6 — Vérification chevauchement	Vérification des conflits avec d'autres congés déjà approuvés pour cet employé.
Étape 7 — Soumission	L'employé ajoute un commentaire optionnel et soumet la demande.
Étape 8 — Notifications	Manager et Administrateur notifiés. E-mail de confirmation à l'employé.
Étape 9 — Décision du Manager	Le Manager consulte la demande et les disponibilités de l'équipe. Il approuve ou rejette avec commentaire.
Étape 10 — Notification résultat	L'employé est notifié par e-mail et push. Si approuvé, le solde est débité. Si rejeté, l'employé peut re-soumettre une demande modifiée.
Scénarios alternatifs	Si l'Administrateur n'a pas délégué la validation au Manager : l'Administrateur est le valideur.
Si validation à deux niveaux configurée : le Manager valide en premier, puis l'Administrateur confirme.
Si annulation demandée après approbation : nouvel workflow de validation pour l'annulation.
Exceptions	Dates passées : formulaire bloqué.
Délai minimum non respecté : avertissement avec date de soumission minimale.
Postconditions	Demande enregistrée avec statut EN_ATTENTE.
Si approuvée : solde débité, absences futures marquées CONGE_APPROUVE.
Si rejetée : aucun impact sur le solde.

4.5 Processus de notifications
PM-09 — Système de notifications automatiques
Identifiant	PM-09
Objectif	Informer en temps réel tous les acteurs des événements qui les concernent via les canaux appropriés.
Déclencheur	Tout événement significatif dans le système (pointage, absence, retard, demande, décision, alerte).
Acteurs	Système Celery (exécutant)
Destinataires selon l'événement
Architecture	Les notifications sont générées de façon asynchrone via Celery pour ne pas bloquer le processus principal.
Les templates d'e-mail sont personnalisés avec le logo et les couleurs de l'organisation.
Les notifications push utilisent l'API Web Push (VAPID) via le Service Worker.
Les préférences individuelles de notification sont respectées (si l'utilisateur a désactivé un canal, aucune notification n'est envoyée sur ce canal).
Gestion des erreurs	Si l'envoi e-mail échoue : retry x3 avec délai exponentiel.
Si le token push est invalide (appareil changé) : suppression du token et log.
Si le SMS échoue (provider indisponible) : log et alerte Super Admin.
Personnalisation	Chaque utilisateur choisit ses canaux préférés par type d'événement.
L'Administrateur peut forcer certaines notifications critiques (blocage compte, suspension).

4.6 Processus de génération de rapports
PM-10 — Génération de rapports de présence
Identifiant	PM-10
Objectif	Produire des rapports de présence précis et formatés pour différents usages (RH, direction, paie, audit).
Types de rapports	Rapport quotidien : résumé du jour (présents, absents, retards).
Rapport hebdomadaire : synthèse de la semaine avec KPI.
Rapport mensuel : analyse complète avec graphiques et statistiques.
Rapport individuel : fiche de présence d'un employé sur une période.
Rapport de département : vue consolidée d'un département.
Rapport d'agence : vue consolidée d'une agence.
Rapport personnalisé : filtres libres (période, employés, statuts, agences).
Formats d'export	PDF : mise en page professionnelle avec logo de l'organisation, graphiques, tableaux.
Excel (.xlsx) : données tabulaires avec mise en forme conditionnelle.
CSV : données brutes pour import dans systèmes tiers.
Processus technique	La génération est effectuée de façon asynchrone par Celery.
L'utilisateur est notifié (in-app + e-mail) lorsque le rapport est prêt.
Le fichier est disponible en téléchargement pendant 7 jours puis supprimé.
Rapports automatiques	Rapport quotidien : envoyé chaque matin à l'Administrateur et aux Managers.
Rapport hebdomadaire : envoyé chaque lundi matin pour la semaine précédente.
Rapport mensuel : envoyé le 1er du mois pour le mois précédent.

4.7 Processus IA
PM-11 — Interaction avec l'assistant IA
Identifiant	PM-11
Objectif	Permettre aux utilisateurs autorisés d'obtenir des analyses, des prévisions et des recommandations basées sur les données de présence.
Déclencheur	L'utilisateur accède à l'interface de l'assistant IA et pose une question.
Acteurs	Utilisateur (initiateur)
Système (orchestrateur)
Fournisseur IA externe (exécutant LLM)
Base de données (source de données)
Préconditions	L'IA est activée pour l'organisation.
L'utilisateur a les droits d'accès à l'IA pour son rôle.
La clé API du fournisseur IA est configurée et valide.
Étape 1 — Saisie de la question	L'utilisateur saisit sa question en langage naturel dans l'interface de chat.
Étape 2 — Préparation du contexte	Le système extrait les données pertinentes de la base de données (limitées au tenant de l'utilisateur). Les données sont anonymisées si nécessaire selon les paramètres de confidentialité.
Étape 3 — Construction du prompt	Le système construit un prompt structuré contenant : le contexte de l'organisation, les données pertinentes, la question de l'utilisateur, les contraintes de réponse (langue, format, périmètre autorisé).
Étape 4 — Appel API	Le système envoie le prompt à l'API du fournisseur IA configuré.
Étape 5 — Traitement réponse	La réponse de l'IA est reçue, validée et formatée pour l'affichage.
Étape 6 — Affichage	La réponse est affichée dans l'interface de chat. L'historique de la conversation est conservé dans la session.
Étape 7 — Journalisation	La question et la réponse sont enregistrées dans le journal (qui a demandé quoi, quand, quelle réponse).
Limites et sécurité	L'IA ne peut accéder qu'aux données du tenant de l'utilisateur.
Les données d'un autre tenant ne peuvent jamais être incluses dans le contexte.
Le quota mensuel de requêtes est configurable par l'Administrateur.
Si quota dépassé : message d'information et blocage jusqu'au mois suivant.
Les données personnelles nominatives sont masquées selon la configuration de confidentialité.
Postconditions	Réponse fournie à l'utilisateur.
Interaction journalisée.
Quota mis à jour.

PM-12 — Génération de rapports intelligents par l'IA
Identifiant	PM-12
Objectif	Générer automatiquement des analyses et recommandations basées sur l'IA à intervalles réguliers.
Déclencheur	Tâche Celery planifiée (quotidienne, hebdomadaire, mensuelle).
Types de rapports IA	Résumé quotidien intelligent : 'Hier, 3 employés étaient absents sans justificatif dans le département Commercial. C'est 50% de plus que la moyenne hebdomadaire.'
Détection de tendances : 'L'employé X a été en retard 4 fois cette semaine, contre 1 fois en moyenne sur le trimestre.'
Prévision d'absentéisme : 'Sur la base des historiques, un pic d'absences est attendu la semaine prochaine (vacances scolaires).'
Recommandations managériales : 'Le département Logistique présente un taux d'absentéisme de 15%, supérieur au seuil d'alerte de 10%. Un entretien managérial est recommandé.'
Postconditions	Rapport IA envoyé à l'Administrateur et aux Managers concernés.
Rapport archivé dans le système.
Alertes déclenchées si seuils dépassés.

4.8 Processus de sécurité
PM-13 — Gestion d'une tentative d'intrusion ou d'anomalie de sécurité
Identifiant	PM-13
Objectif	Détecter et répondre automatiquement aux tentatives d'intrusion ou aux comportements anormaux.
Déclencheur	Détection d'une anomalie de sécurité par le système.
Scénarios couverts	Brute force : 5 tentatives de connexion échouées consécutives.
GPS simulé : détection d'un GPS mock lors d'un pointage.
Tentative d'accès cross-tenant : un utilisateur tente d'accéder aux données d'un autre tenant.
Session suspecte : connexion depuis une IP géographiquement très différente.
Injection SQL / XSS détectée par le WAF.
Réponse brute force	Blocage du compte pendant la durée configurée.
E-mail de notification à l'utilisateur.
Log dans le journal d'audit.
Alerte à l'Administrateur si dépassement du seuil de blocages répétés.
Réponse GPS simulé	Refus du pointage.
Log dans le journal d'audit avec flag 'GPS_SIMULE'.
Alerte immédiate à l'Administrateur et au Manager.
Réponse cross-tenant	Retour HTTP 403 sans révéler l'existence de la ressource.
Log dans le journal d'audit global.
Alerte au Super Administrateur.
Postconditions	L'attaque est bloquée.
L'événement est journalisé de façon inaltérable.
Les parties concernées sont notifiées.
Des mesures correctives peuvent être prises.

4.9 Processus d'export de données
PM-14 — Export de données par l'Administrateur
Identifiant	PM-14
Objectif	Permettre à l'Administrateur d'exporter les données de présence dans des formats exploitables.
Déclencheur	L'Administrateur ou le Manager demande un export depuis l'interface de rapports.
Préconditions	L'utilisateur a les droits d'export.
Des données existent pour la période demandée.
Étape 1 — Configuration de l'export	L'utilisateur définit : type de rapport, période, filtre (agence, département, employé), format (PDF, Excel, CSV).
Étape 2 — Déclenchement asynchrone	La tâche d'export est envoyée à la file Celery. Un message 'Export en cours de génération' est affiché immédiatement.
Étape 3 — Génération	Celery génère le fichier en arrière-plan. Pour les PDF : utilisation de bibliothèques de rendu PDF. Pour Excel : openpyxl. Pour CSV : csv Python.
Étape 4 — Notification	L'utilisateur reçoit une notification in-app et par e-mail : 'Votre export est prêt, cliquez ici pour le télécharger.'
Étape 5 — Téléchargement	Le fichier est téléchargeable pendant 7 jours depuis un lien sécurisé (token URL unique).
Étape 6 — Nettoyage automatique	Après 7 jours, le fichier est automatiquement supprimé du stockage.
Postconditions	Fichier généré et disponible.
Log de l'export dans le journal d'audit.
Fichier supprimé après 7 jours.


CHAPITRE 5 — CARTOGRAPHIE DES PROCESSUS

Ce chapitre présente la cartographie complète des processus de la plateforme, organisés par famille et avec leurs relations mutuelles. Cette cartographie constitue la base pour la conception des diagrammes BPMN et des diagrammes de séquence UML.
5.1 Processus principaux
Les processus principaux créent directement de la valeur pour les utilisateurs finaux. Ils constituent le cœur métier de la plateforme.

Code	Nom	Description
PP-01	Pointage arrivée employé	Enregistrement sécurisé de l'arrivée. GPS + Photo + Horodatage. Calcul du statut.
PP-02	Pointage départ employé	Enregistrement du départ. Calcul durée présence, heures sup., départ anticipé.
PP-03	Consultation présences temps réel	Affichage instantané des présences, absences et retards sur le tableau de bord.
PP-04	Demande et validation congé	Workflow complet : demande → notification → validation → débit solde.
PP-05	Justification d'absence	Workflow : soumission justificatif → notification → validation → mise à jour statut.
PP-06	Génération de rapport	Production des rapports de présence en PDF, Excel, CSV.
PP-07	Interaction assistant IA	Réponse aux questions sur les données de présence.
PP-08	Synchronisation offline	Synchronisation des pointages effectués sans connexion Internet.
5.2 Processus secondaires
Les processus secondaires supportent les processus principaux en maintenant les données de référence à jour.

Code	Nom	Description
PS-01	Gestion des horaires	Création, modification, affectation des horaires aux employés/postes/départements.
PS-02	Gestion des agences	Création et configuration des sites géographiques avec coordonnées GPS.
PS-03	Gestion des employés	CRUD des comptes employés, affectations, statuts.
PS-04	Gestion des départements/postes	Maintien de la structure organisationnelle.
PS-05	Gestion des congés (types)	Configuration des types de congés et des quotas annuels.
PS-06	Gestion des jours fériés	Configuration du calendrier des jours fériés.
PS-07	Gestion des annonces	Publication d'informations internes aux employés.
PS-08	Import de données	Import en masse d'employés via CSV/Excel.
5.3 Processus de support
Les processus de support garantissent le bon fonctionnement continu de la plateforme.

Code	Nom	Description
PSU-01	Gestion des notifications	Envoi automatique de notifications sur tous les canaux configurés.
PSU-02	Détection automatique absences	Tâche planifiée détectant les absences non pointées en fin de fenêtre horaire.
PSU-03	Génération rapports automatiques	Production quotidienne/hebdomadaire/mensuelle des rapports envoyés par e-mail.
PSU-04	Nettoyage et archivage	Archivage des données anciennes, suppression des exports expirés, nettoyage logs.
PSU-05	Sauvegarde automatique	Sauvegarde quotidienne de la base de données et des fichiers.
PSU-06	Synchronisation offline	Réception et traitement des pointages hors ligne à la reconnexion.
PSU-07	Génération rapports IA	Analyse automatique et génération des rapports intelligents périodiques.
5.4 Processus d'administration
Les processus d'administration gèrent la plateforme SaaS elle-même (niveau Super Admin).

Code	Nom	Description
PA-01	Onboarding organisation	Création et activation d'un nouveau tenant.
PA-02	Suspension organisation	Blocage d'accès d'un tenant avec notification.
PA-03	Monitoring plateforme	Surveillance performances, erreurs, disponibilité.
PA-04	Gestion sauvegardes globales	Sauvegarde, restauration, tests d'intégrité.
PA-05	Configuration IA globale	Ajout et configuration des fournisseurs IA disponibles.
PA-06	Audit global	Consultation du journal d'audit global de la plateforme.
5.5 Processus de sécurité
Les processus de sécurité protègent la plateforme et les données de toute menace.

Code	Nom	Description
PSEC-01	Authentification sécurisée	Connexion, gestion sessions, protection brute force, CAPTCHA.
PSEC-02	Vérification GPS	Validation de la position GPS à chaque pointage, détection de simulation.
PSEC-03	Vérification photo	Capture obligatoire caméra temps réel, interdiction galerie.
PSEC-04	Journalisation audit	Enregistrement inaltérable de tous les événements sensibles.
PSEC-05	Gestion des sessions	Expiration, révocation, protection hijacking.
PSEC-06	Protection contre injections	Validation entrées, ORM exclusif, en-têtes CSP/HSTS.
PSEC-07	Isolation multi-tenant	Middleware tenant, filtrage automatique, vérification cross-tenant.
PSEC-08	Réponse aux incidents	Blocage automatique, alertes, journalisation.
5.6 Relations entre processus
Les processus de la plateforme ne sont pas indépendants. Ils s'appuient les uns sur les autres selon des relations de dépendance, de déclenchement et de données. Voici les principales relations :
Processus source	Relation	Processus cible
PP-01 (Pointage arrivée)	dépend de	PS-01 (Horaires) pour calculer le statut / PS-02 (Agences) pour le GPS / PSEC-02 (Vérification GPS) / PSEC-03 (Photo)
PP-01 (Pointage arrivée)	déclenche	PSU-01 (Notifications retard) / PSEC-04 (Journalisation)
PSU-02 (Détection absences)	dépend de	PS-01 (Horaires) / PP-01 (Pointages existants) / PS-06 (Jours fériés)
PSU-02 (Détection absences)	déclenche	PSU-01 (Notifications) / PP-05 (Justification possible)
PP-04 (Congés)	déclenche	PSU-01 (Notifications) / PSU-02 (exclusion de la détection absences)
PP-06 (Rapports)	dépend de	PP-01+02 (Pointages) / PP-04+05 (Congés/Absences) / PS-01 (Horaires)
PP-07 (IA)	dépend de	Toutes les données métier du tenant (lecture seule) / PA-05 (Config IA)
PP-08 (Offline sync)	déclenche	PSEC-04 (Journalisation) / PSU-01 (Notification synchro)
PA-01 (Onboarding)	déclenche	PA-05 (Config IA) / PSU-01 (E-mail bienvenue)
PA-02 (Suspension)	bloque	Tous les processus PP du tenant concerné

CHAPITRE 6 — ANALYSE DES RÈGLES MÉTIER

Ce chapitre liste exhaustivement toutes les règles métier de la plateforme. Chaque règle est identifiée par un code unique, décrite avec précision, justifiée, et accompagnée de son impact et de ses éventuelles exceptions.
6.1 Règles relatives à l'organisation et aux tenants
ID	Description	Justification	Exceptions
RM-ORG-001	Une organisation dispose d'un identifiant tenant unique (UUID) et d'un slug URL unique. Ces deux identifiants ne peuvent jamais être modifiés après création.	Garantir la stabilité des références et l'intégrité des données historiques.	Aucune exception.
RM-ORG-002	Une organisation doit disposer d'au moins une agence active pour permettre les pointages de ses employés.	Le pointage est toujours rattaché à une agence. Sans agence, il n'y a pas de zone GPS de référence.	L'Administrateur peut configurer une agence fictive pour les organisations en télétravail pur.
RM-ORG-003	La suspension d'une organisation entraîne le blocage immédiat de toutes les sessions actives de ses utilisateurs et l'impossibilité de créer de nouvelles sessions.	Garantir que la suspension est effective instantanément sans délai de grâce.	Le Super Administrateur peut accéder aux données pour des besoins de support technique.
RM-ORG-004	Les données d'une organisation ne peuvent jamais être accessibles par les utilisateurs d'une autre organisation, quelle que soit leur action.	Principe fondamental de l'architecture multi-tenant. Exigence légale (RGPD).	Aucune exception.
RM-ORG-005	Le Super Administrateur ne peut jamais accéder aux données opérationnelles des organisations (employés, pointages, documents).	Séparation des rôles. Protection de la confidentialité des données clients.	En cas de litige légal, un accès d'urgence documenté peut être accordé avec accord du client.
6.2 Règles relatives à l'authentification
ID	Description	Justification	Exceptions
RM-AUTH-001	L'identifiant de connexion est toujours l'adresse e-mail. Il n'existe pas d'autre mode d'identification (pas de nom d'utilisateur textuel).	Unicité garantie de l'identifiant sur toute la plateforme. Simplicité pour l'utilisateur.	Aucune exception.
RM-AUTH-002	La comparaison de l'adresse e-mail est insensible à la casse (majuscules/minuscules équivalentes).	Éviter les erreurs de connexion dues à la casse.	Aucune exception.
RM-AUTH-003	Le mot de passe est sensible à la casse.	Convention de sécurité universelle.	Aucune exception.
RM-AUTH-004	Après N tentatives de connexion échouées consécutives (N configurable, défaut 5), le compte est verrouillé pour une durée D (D configurable, défaut 15 minutes).	Protection contre les attaques brute force et credential stuffing.	Un Administrateur peut débloquer manuellement un compte verrouillé.
RM-AUTH-005	Le message d'erreur affiché en cas d'échec de connexion est toujours générique : 'Identifiants incorrects'. Le système ne révèle jamais si l'e-mail existe ou non.	Prévention de l'énumération d'e-mails (user enumeration attack).	Aucune exception.
RM-AUTH-006	La première connexion d'un utilisateur doit obligatoirement déboucher sur un changement de mot de passe. L'accès aux fonctionnalités est bloqué tant que ce changement n'est pas effectué.	Le mot de passe temporaire est transmis par e-mail non chiffré. Il doit être changé immédiatement.	Aucune exception.
RM-AUTH-007	Un token de réinitialisation de mot de passe est valide pour une utilisation unique et expire après 30 minutes. Un seul token valide peut exister à la fois par compte.	Limiter la fenêtre d'exploitation d'un token compromis.	Aucune exception.
RM-AUTH-008	Tout changement de mot de passe invalide instantanément toutes les sessions actives du compte concerné, à l'exception de la session ayant effectué le changement.	Mesure de sécurité en cas de compromission de compte.	Aucune exception.
6.3 Règles relatives au pointage
ID	Description	Justification	Exceptions
RM-POINT-001	Tout pointage (arrivée ou départ) nécessite obligatoirement une photo prise en temps réel par la caméra frontale de l'appareil. L'utilisation d'une photo de galerie est techniquement impossible.	Prévenir la fraude par substitution d'image. Preuve de présence physique de la personne qui pointe.	Aucune exception.
RM-POINT-002	Tout pointage nécessite une vérification GPS préalable confirmant que l'employé se trouve dans la zone géographique autorisée de son agence (ou d'une de ses agences secondaires).	Garantir la présence physique sur le lieu de travail. Prévenir le pointage à distance.	Mode de validation manuelle activable par l'Admin pour des cas exceptionnels documentés.
RM-POINT-003	Un employé ne peut effectuer qu'un seul pointage d'arrivée et un seul pointage de départ par plage horaire définie.	Prévenir les doublons. Garantir la cohérence des données de présence.	Organisation configurée pour la gestion de pause repas (pointage sortie/retour pause supplémentaire).
RM-POINT-004	Le pointage d'arrivée doit toujours être antérieur au pointage de départ sur la même plage horaire.	Cohérence logique fondamentale du pointage.	Correction manuelle par un Administrateur avec traçabilité complète.
RM-POINT-005	L'heure de référence pour tous les calculs (retard, départ anticipé, heures sup.) est l'heure du serveur, jamais l'heure fournie par le client.	Empêcher la manipulation de l'heure client pour masquer un retard.	Aucune exception.
RM-POINT-006	La détection d'un GPS simulé (mock location) entraîne le refus immédiat du pointage, une alerte à l'Administrateur et une entrée dans le journal d'audit avec flag spécifique.	Prévenir la fraude GPS. Décourager les tentatives de contournement.	Aucune exception.
RM-POINT-007	Un pointage hors ligne est valide s'il est synchronisé dans le délai maximum configuré (défaut 48h). Au-delà, il est marqué EN_ATTENTE_VALIDATION pour contrôle humain.	Permettre le travail sans Internet tout en maintenant un contrôle sur les données synchronisées.	L'Administrateur peut valider manuellement un pointage hors ligne tardif.
RM-POINT-008	Toute modification manuelle d'un pointage (par un Admin ou Manager) doit être tracée dans le journal d'audit avec : l'auteur de la modification, les valeurs avant et après, l'horodatage et la justification.	Garantir l'inaltérabilité de la chaîne de preuve. Permettre les audits.	Aucune exception.
RM-POINT-009	Le retard est calculé uniquement si le dépassement dépasse la tolérance configurée. Retard = heure pointage − (heure prévue + tolérance). Résultat négatif = pas de retard.	Éviter de pénaliser les employés pour quelques secondes ou minutes de différence.	Chaque organisation définit sa tolérance selon sa politique interne.
6.4 Règles relatives aux horaires
ID	Description	Justification	Exceptions
RM-HOR-001	Tout employé actif doit disposer d'un horaire affecté. Sans horaire, le système ne peut pas calculer les statuts de présence ni détecter les absences.	Pré-requis au fonctionnement de toute la logique de présence.	Employé en horaire 'Libre' : horaire spécial sans plage fixe. Pointage toujours accepté sans calcul de statut.
RM-HOR-002	L'horaire individuel prévaut sur l'horaire du poste, qui prévaut sur l'horaire du département, qui prévaut sur l'horaire de l'agence.	Permettre la personnalisation à tous les niveaux organisationnels avec une priorité claire.	Aucune exception.
RM-HOR-003	Un pointage effectué en dehors de la fenêtre de pointage définie pour l'horaire est rejeté avec message explicatif indiquant l'heure d'ouverture de la prochaine fenêtre.	Éviter les pointages parasites en dehors des heures de travail.	L'Administrateur peut autoriser les pointages hors fenêtre avec un avertissement (non rejet).
RM-HOR-004	Pour les horaires en équipe de nuit chevauchant minuit, le pointage de départ effectué après minuit est rattaché à la journée de début de la plage (J), pas à la journée courante (J+1).	Cohérence des données : une présence de nuit doit apparaître sur une seule journée.	Aucune exception.
RM-HOR-005	Pour les enseignants, une absence n'est enregistrée que pour les créneaux de cours planifiés. L'absence d'un enseignant les jours sans cours n'est pas enregistrée et n'est pas à justifier.	Particularité des horaires discontinus des enseignants. Empêcher les fausses absences.	Aucune exception.
RM-HOR-006	Tout changement d'horaire d'un employé doit être historisé. Le système utilise toujours l'horaire applicable à la date exacte du pointage pour les calculs rétrospectifs.	Garantir la cohérence des rapports et des calculs sur des données historiques.	Aucune exception.
6.5 Règles relatives aux absences et congés
ID	Description	Justification	Exceptions
RM-ABS-001	Une absence est automatiquement enregistrée par le système si l'employé n'a pas pointé son arrivée à l'expiration de la fenêtre de pointage définie pour son horaire.	Automatiser la gestion des absences. Éviter les oublis de saisie.	Jours fériés, congés approuvés, employés suspendus ou archivés.
RM-ABS-002	Le délai maximum pour soumettre un justificatif d'absence est configurable par l'organisation. Passé ce délai, la soumission est bloquée et nécessite l'intervention de l'Administrateur.	Encourager la promptitude dans la justification des absences. Permettre à l'organisation de définir sa politique.	Aucune exception technique (l'Admin peut toujours saisir manuellement).
RM-ABS-003	Les jours fériés configurés dans le calendrier de l'organisation ne génèrent jamais d'absence et ne sont jamais décomptés des congés.	Conformité légale. Automatisation du respect des jours fériés.	Organisations travaillant les jours fériés (ex : hôpitaux) : configuration spécifique possible.
RM-ABS-004	Une demande de congé ne peut être soumise que si le solde de congés disponible est suffisant pour couvrir la durée demandée.	Prévenir les soldes négatifs. Respect des droits légaux.	Congés par anticipation configurables pour certains types de congés.
RM-ABS-005	La modification d'un congé approuvé nécessite un nouveau cycle de validation complet. Le solde n'est pas modifié tant que la nouvelle demande n'est pas approuvée.	Maintenir l'intégrité du processus de validation.	Aucune exception.
RM-ABS-006	L'annulation d'un congé approuvé par l'employé ou le responsable restitue automatiquement le nombre de jours correspondant au solde de l'employé.	Cohérence des soldes. Équité pour l'employé.	Annulation après le début du congé : gestion au prorata, selon politique organisationnelle.
RM-ABS-007	Les jours de week-end (selon les jours non ouvrables configurés) ne sont jamais décomptés des congés.	Conformité légale universelle.	Organisations travaillant le week-end : configuration des jours ouvrables spécifique.
6.6 Règles relatives à la sécurité des données
ID	Description	Justification	Exceptions
RM-SEC-001	Tout accès non autorisé à une ressource (cross-tenant, permissions insuffisantes) renvoie une erreur HTTP 403, sans révéler l'existence ou la nature de la ressource.	Prévention de l'information disclosure. Standard de sécurité.	Aucune exception.
RM-SEC-002	Le journal d'audit est en écriture seule. Aucun utilisateur, y compris le Super Administrateur, ne peut modifier ni supprimer une entrée du journal.	Garantir l'inaltérabilité de la trace légale. Confiance dans les données d'audit.	Aucune exception technique.
RM-SEC-003	Les messages d'erreur affichés aux utilisateurs ne révèlent jamais de détails techniques (stack trace, nom de table, chemin fichier, version logicielle).	Prévenir la collecte d'informations techniques exploitables par un attaquant.	Environnement de développement : erreurs détaillées autorisées dans les logs mais pas dans l'interface.
RM-SEC-004	Les données sensibles (numéros d'identité, données personnelles critiques) sont chiffrées au repos avec AES-256.	Conformité RGPD. Protection en cas de compromission de la base de données.	Aucune exception.
RM-SEC-005	Les photos de pointage sont stockées dans un répertoire non accessible directement via le web. L'accès nécessite une authentification et une vérification des droits.	Les photos sont des données personnelles sensibles. Accès restreint obligatoire.	Aucune exception.

CHAPITRE 7 — ANALYSE DES CONTRAINTES MÉTIER

7.1 Contraintes horaires
Contrainte	Description et impact
Fenêtre de pointage obligatoire	Le pointage n'est accepté que pendant la fenêtre de pointage définie pour chaque horaire (ex : 30 min avant l'heure de début jusqu'à 2h après). En dehors, le pointage est rejeté ou marqué HORS_HORAIRE selon la configuration.
Horaires de nuit trans-journaliers	Un horaire de nuit commençant à 22h00 et se terminant à 06h00 le lendemain doit être géré comme une seule plage continue. Le système doit rattacher correctement le pointage de départ du lendemain matin à la plage de travail de la nuit précédente.
Créneaux multiples enseignants	Un enseignant peut avoir plusieurs créneaux le même jour (ex : 08h00-10h00 et 14h00-16h00). Chaque créneau constitue une plage de travail indépendante avec ses propres pointages. L'absence entre deux créneaux n'est pas une absence.
Rotation des équipes	Les organisations en rotation (hôpitaux, usines) ont des plannings de rotation complexes. Le système doit associer le bon horaire d'équipe à chaque employé pour chaque jour.
Tolérance retard	La tolérance est configurable et peut être différente par organisation, par agence, ou par horaire. Elle doit être appliquée de façon cohérente et documentée pour éviter toute contestation.
Délai minimum demande congé	Une demande de congé doit être soumise au moins N jours à l'avance (configurable). Passé ce délai, la demande peut être bloquée automatiquement.
Durée maximale de synchronisation offline	Un pointage hors ligne doit être synchronisé dans les 48h suivant son enregistrement (configurable). Au-delà, il est mis en validation manuelle pour vérification.
7.2 Contraintes GPS
Contrainte	Description et impact
Précision variable des GPS smartphones	La précision GPS d'un smartphone peut varier de 3 à 100+ mètres selon l'environnement (bâtiment, zones denses, ciel ouvert). Le système doit appliquer une marge de tolérance et enregistrer la précision mesurée.
Délai d'acquisition GPS	L'obtention des coordonnées GPS peut prendre de 1 à 15 secondes. Un timeout doit être défini. Si le GPS n'est pas disponible après le timeout, le pointage doit être refusé avec un message adapté.
GPS désactivé sur l'appareil	Si l'employé a désactivé le GPS, le pointage est impossible. Le système doit détecter cette situation et afficher des instructions d'activation claires.
GPS simulé / Mock Location	Des applications Android permettent de simuler une position GPS différente de la position réelle (mock location). Le système doit détecter cela et refuser le pointage. Cette contrainte est une limite technique : la détection n'est pas toujours possible sur iOS.
Rayon GPS minimal	Le rayon GPS ne peut pas être inférieur à 50 mètres (valeur recommandée : 100-200m pour les zones urbaines) pour tenir compte de l'imprécision des GPS smartphones.
Sites sans GPS	Dans certains environnements (sous-sols, centres commerciaux couverts), le GPS peut être indisponible. L'organisation doit être informée de cette limitation lors de la configuration.
Télétravail	Pour les employés en télétravail, une agence 'Télétravail' doit être créée avec les coordonnées du domicile de l'employé. Ces coordonnées doivent être déclarées et validées par l'organisation.
Chantiers et sites changeants	Pour les organisations avec des chantiers ou des missions sur sites changeants (BTP, consultants), la configuration des zones GPS doit être mise à jour régulièrement. L'Administrateur peut ajouter des zones temporaires.
7.3 Contraintes organisationnelles
Contrainte	Description et impact
Multi-tenant strict	Les données de chaque organisation sont isolées techniquement. Aucun mécanisme ne permet de partager des données entre deux tenants, même pour des organisations appartenant au même groupe.
Pas d'accès data aux Super Admin	Le Super Administrateur ne peut pas accéder aux données opérationnelles des organisations pour des raisons légales (RGPD) et contractuelles.
Personnalisation dans les limites	Chaque organisation peut personnaliser sa plateforme (couleurs, logo, paramètres) uniquement dans les limites définies par l'éditeur. La personnalisation ne doit pas permettre de modifier le comportement fonctionnel de sécurité.
Rôles non transférables	Un utilisateur a un seul rôle à la fois dans une organisation. Il ne peut pas cumuler les rôles (ex : être à la fois Manager et Employé pour différentes équipes).
Affectation multi-agences	Un employé peut être affecté à plusieurs agences (pour les cas de mobilité entre sites). Le pointage est autorisé depuis n'importe quelle zone GPS de ses agences affectées.
Hiérarchie des horaires	La hiérarchie de priorité des horaires (individu > poste > département > agence) est figée et ne peut pas être modifiée par l'organisation.
Minimum d'une agence	Une organisation doit toujours avoir au minimum une agence active pour que les pointages soient possibles.
7.4 Contraintes légales et réglementaires
Contrainte	Description et impact
RGPD — Consentement	La collecte de la position GPS et de la photo de l'employé constitue un traitement de données personnelles sensibles. L'organisation cliente est le responsable du traitement. L'éditeur est le sous-traitant. Un DPA (Data Processing Agreement) doit être signé.
RGPD — Droit à l'effacement	Sur demande d'un employé, ses données personnelles doivent pouvoir être supprimées. Cependant, les obligations légales de conservation des données de travail (variables selon les pays) peuvent primer.
RGPD — Portabilité	L'employé peut demander l'export de toutes ses données personnelles dans un format standard (JSON ou CSV).
Conservation des données de travail	Dans de nombreux pays, les données de temps de travail doivent être conservées pendant 3 à 5 ans. Le système doit permettre cette conservation tout en gérant les demandes d'effacement.
Durées légales de travail	Le système doit pouvoir configurer des alertes lorsque les heures travaillées dépassent les limites légales (ex : 10h/jour, 48h/semaine en France). Ces limites varient selon les pays.
Consultation du comité social (France)	Dans les organisations françaises de plus de 50 salariés, la mise en place d'un outil de contrôle de présence doit faire l'objet d'une consultation du CSE (Comité Social et Économique).
Information préalable des employés	Les employés doivent être informés de la mise en place du système de pointage, des données collectées et de leur utilisation (notice RGPD, mentions légales dans l'interface).
7.5 Contraintes spécifiques aux établissements scolaires
Contrainte	Description et impact
Emplois du temps par matière	Les enseignants ont des emplois du temps qui varient par semaine, par trimestre ou par semestre. Le système doit gérer des emplois du temps complexes.
Pas d'absence hors créneaux	Un enseignant n'est pas censé être absent les jours où il n'a pas de cours. Le système ne doit jamais générer d'absence pour un jour sans créneau planifié.
Cours remplacés / annulés	Un cours peut être annulé (l'enseignant est absent) ou remplacé (un autre enseignant intervient). Le système doit permettre de marquer un créneau comme annulé ou de transférer la présence à l'enseignant remplaçant.
Vacances scolaires	Les périodes de vacances scolaires doivent être configurées. Durant ces périodes, aucune absence n'est générée pour les enseignants.
Présence des surveillants et ATSEM	Le personnel non-enseignant (ATSEM, surveillants, personnel administratif) a des horaires fixes et est géré comme des employés standard.
7.6 Contraintes liées à l'IA
Contrainte	Description et impact
Dépendance fournisseur externe	Le module IA dépend de fournisseurs tiers (OpenAI, Anthropic, Mistral). Une indisponibilité du service IA ne doit pas affecter les fonctionnalités core de la plateforme.
Isolation des données IA	Le contexte envoyé à l'API IA ne doit contenir que les données du tenant actif. Il est techniquement impossible de croiser des données entre tenants dans les prompts IA.
Limites de tokens/requêtes	Les fournisseurs IA ont des limites de tokens et des quotas d'utilisation. Le système doit gérer ces limites (quota mensuel par organisation, message clair en cas de dépassement).
Confidentialité des données envoyées	Selon la politique de confidentialité du fournisseur IA, des données personnelles peuvent être transmises à des serveurs tiers. L'organisation doit être informée et donner son accord. Option Ollama (IA locale) disponible pour les organisations très sensibles.
Hallucinations IA	Les réponses de l'IA peuvent contenir des erreurs ou des inventions (hallucinations). Les réponses de l'IA sont présentées comme des recommandations, jamais comme des faits certifiés. L'utilisateur est averti de cette limitation dans l'interface.
Langue de l'IA	La qualité des réponses IA varie selon la langue. Les meilleures performances sont obtenues en anglais. L'organisation peut configurer la langue de l'assistant.

CHAPITRE 8 — ANALYSE DES DONNÉES MÉTIER

Ce chapitre identifie et décrit toutes les données manipulées par la plateforme. Pour chaque entité, nous décrivons son rôle, son utilisation, son cycle de vie, son propriétaire et son niveau de confidentialité.
8.1 Entité : Organisation (Tenant)
Attribut	Détail
Rôle	Entité racine représentant un client de la plateforme SaaS. Toutes les autres entités lui sont rattachées via le tenant_id.
Données clés	ID (UUID), slug, nom légal, nom commercial, type (Entreprise/École/Hôpital/etc.), pays, fuseau horaire, langue, logo, couleurs, statut (Active/Suspendue/Expirée/Supprimée), date de création, paramètres (JSON).
Utilisation	Identification du contexte tenant pour chaque requête. Personnalisation de l'interface. Configuration des règles métier.
Cycle de vie	Création (par Super Admin) → Configuration (par Admin) → Active → Suspendue (si besoin) → Réactivée → Expirée (fin abonnement V2) → Supprimée (archivage).
Propriétaire	Éditeur SaaS (Super Administrateur).
Confidentialité	Interne — Informations commerciales et techniques.
Relations	1 Organisation → N Agences, N Départements, N Postes, N Employés, N Horaires, N Pointages, N Annonces.
8.2 Entité : Agence
Attribut	Détail
Rôle	Site géographique physique appartenant à une organisation. Unité de base du geofencing GPS.
Données clés	ID, tenant_id, nom, code, type, adresse, latitude, longitude, rayon_gps, zones_supplementaires (JSON), horaires, responsable_id, statut, photo.
Utilisation	Vérification GPS lors du pointage. Filtrage des rapports par agence. Affectation des employés.
Cycle de vie	Création → Active → Inactive (désactivation temporaire) → Archivée (historique conservé).
Propriétaire	Administrateur d'organisation.
Confidentialité	Interne à l'organisation. Les coordonnées GPS peuvent être sensibles (sécurité physique).
Relations	1 Agence → N Employés, N Pointages, N Horaires d'agence.
8.3 Entité : Employé
Attribut	Détail
Rôle	Représente un membre du personnel de l'organisation. Entité centrale du système de présence.
Données clés	ID, tenant_id, matricule, prénom, nom, date_naissance, genre, nationalité, numéro_identité (chiffré), photo_profil, email_pro, email_perso, telephone_pro, telephone_perso, adresse_domicile, contact_urgence, poste_id, departement_id, agence_principale_id, agences_secondaires (JSON), type_contrat, date_entree, date_fin_contrat, manager_id, horaire_id, role (ADMIN/MANAGER/SUPERVISEUR/EMPLOYE), statut (Actif/Suspendu/Conge/Archive), solde_conges.
Utilisation	Authentification. Pointage. Calcul des présences. Gestion des congés. Rapports. Notifications.
Cycle de vie	Création (Admin) → Actif → Suspendu (temporaire) → En congé → Actif → Archivé (fin contrat ou départ).
Propriétaire	Administrateur d'organisation.
Confidentialité	CONFIDENTIEL — Données personnelles au sens du RGPD. Accès restreint selon le rôle. L'employé voit ses propres données. Le Manager voit les données professionnelles de son équipe. L'Admin voit toutes les données.
Relations	1 Employé → N Pointages, N Absences, N Congés, N Documents, N Sessions.
8.4 Entité : Horaire
Attribut	Détail
Rôle	Définit les plages de travail attendues pour un employé, un poste, un département ou une agence.
Données clés	ID, tenant_id, nom, type (FIXE/EQUIPE/PERSONNALISE/ENSEIGNANT), jours_actifs (JSON), heure_debut, heure_fin, pause_debut, pause_fin, fenetre_pointage_arrivee (minutes avant/après), fenetre_pointage_depart (minutes avant/après), tolerance_retard, tolerance_depart_anticipe, seuil_heures_sup.
Utilisation	Vérification de la fenêtre de pointage. Calcul des statuts (retard, départ anticipé, heures sup.). Détection automatique des absences.
Cycle de vie	Création → Actif → Modifié (historisation) → Inactif.
Propriétaire	Administrateur d'organisation.
Confidentialité	Interne. Accessible à l'employé concerné (consultation uniquement).
Relations	1 Horaire → N Employés, N Postes, N Départements, N Agences.
8.5 Entité : Pointage
Attribut	Détail
Rôle	Enregistrement de chaque événement de pointage (arrivée ou départ) d'un employé. Entité centrale de toutes les analyses de présence.
Données clés	ID (UUID), tenant_id, employe_id, agence_id, type (ARRIVEE/DEPART), date, heure_serveur, heure_client, latitude, longitude, precision_gps, photo_path, adresse_ip, user_agent, appareil, navigateur, os, heure_prevue, retard_minutes, depart_anticipe_min, heures_supp_min, statut, mode (EN_LIGNE/HORS_LIGNE), sync_at, valide (bool), valide_par, observations, created_at.
Utilisation	Source unique de vérité pour toutes les présences. Utilisé dans tous les rapports, calculs, statistiques et analyses IA.
Cycle de vie	Création (par employé ou synchro offline) → Statut calculé → Validation optionnelle → Conservation selon durée légale → Archivage → Suppression (si fin de conservation légale).
Propriétaire	Employé (créateur) + Organisation (gestionnaire).
Confidentialité	CONFIDENTIEL — Données personnelles incluant photo et position GPS. Soumis au RGPD.
Relations	N Pointages → 1 Employé, 1 Agence, 1 Tenant.
Volume estimé	Environ 2 pointages/jour/employé. Pour 100 employés : 200 pointages/jour, 4200/mois, 50000/an. Conservation sur 5 ans : 250 000 enregistrements par organisation de 100 employés.
8.6 Entité : Absence
Attribut	Détail
Rôle	Enregistrement d'une absence d'un employé sur une journée ou une plage donnée.
Données clés	ID, tenant_id, employe_id, date_debut, date_fin, type_absence, statut (NON_JUSTIFIEE/EN_ATTENTE/JUSTIFIEE/CONGE_APPROUVE), motif, commentaire, justificatif_path, validee_par, date_validation, detection_auto (bool).
Utilisation	Reporting des absences. Calcul des taux d'absence. Alertes managers. Justification par l'employé.
Cycle de vie	Détection automatique (statut NON_JUSTIFIEE) → Soumission justificatif (EN_ATTENTE) → Validation (JUSTIFIEE ou rejet) → Conservation.
Propriétaire	Système (détection automatique) / Employé (justification) / Manager/Admin (validation).
Confidentialité	CONFIDENTIEL — Données personnelles et potentiellement médicales.
8.7 Entité : Congé
Attribut	Détail
Rôle	Demande et approbation de jours de repos planifiés d'un employé.
Données clés	ID, tenant_id, employe_id, type_conge_id, date_debut, date_fin, nb_jours_ouvres, statut (EN_ATTENTE/APPROUVE/REJETE/ANNULE), commentaire_employe, commentaire_valideur, valide_par, date_validation.
Utilisation	Gestion du planning. Calcul des soldes. Exclusion des absences. Alertes de débordement d'effectif.
Cycle de vie	Soumission (EN_ATTENTE) → Validation (APPROUVE/REJETE) → Exécution → Fin congé → Retour actif / Annulation possible.
Propriétaire	Employé (demandeur) / Manager/Admin (valideur).
Confidentialité	Interne. Le motif peut être sensible (maladie, situation familiale).
8.8 Entité : Photo de pointage
Attribut	Détail
Rôle	Preuve photographique de présence physique de l'employé au moment du pointage.
Données clés	Fichier JPEG stocké dans un répertoire sécurisé. Nom de fichier = UUID du pointage. Référence dans la table pointage (photo_path).
Utilisation	Preuve anti-fraude. Consultation en cas de litige. Audit visuel possible par l'Administrateur.
Cycle de vie	Capture (au pointage) → Stockage sécurisé → Conservation (durée légale) → Suppression automatique selon politique.
Propriétaire	Organisation (gestionnaire des données).
Confidentialité	TRÈS CONFIDENTIEL — Biométrique (image du visage). Soumis à des règles spéciales RGPD. Accès restreint : Admin, Manager avec justification, Auditeur autorisé.
Sécurité	Stockage hors racine web. Accès uniquement via URL temporaire signée. Chiffrement au repos recommandé.
8.9 Entité : Journal d'audit
Attribut	Détail
Rôle	Trace inaltérable de tous les événements sensibles de la plateforme.
Données clés	ID, tenant_id, user_id, user_email, user_role, categorie, action, description, objet_type, objet_id, valeurs_avant (JSON), valeurs_apres (JSON), adresse_ip, user_agent, appareil, latitude, longitude, resultat (SUCCESS/FAILURE), details_erreur, timestamp (UTC précis).
Utilisation	Audit de conformité. Investigation sécurité. Preuve légale. Détection d'anomalies.
Cycle de vie	Création (INSERT uniquement, jamais UPDATE ni DELETE) → Conservation selon obligations légales → Archivage hors ligne.
Propriétaire	Système. Aucun utilisateur ne peut modifier ni supprimer.
Confidentialité	Sensible — Accès restreint : Super Admin (journal global), Admin (journal de son organisation).
Volume	Chaque action génère 1 à N entrées. Estimé à 50-200 entrées/jour/organisation.
8.10 Entité : Conversation IA
Attribut	Détail
Rôle	Historique des interactions entre les utilisateurs et l'assistant IA.
Données clés	ID, tenant_id, user_id, session_id, role (user/assistant), contenu, timestamp, fournisseur_ia, modele_ia, tokens_utilises.
Utilisation	Maintien du contexte conversationnel. Journalisation des questions posées. Calcul du quota d'utilisation.
Cycle de vie	Création → Conservation (durée configurable, défaut N jours) → Suppression automatique.
Propriétaire	Organisation.
Confidentialité	CONFIDENTIEL — Peut contenir des questions sur des données personnelles d'employés.

CHAPITRE 9 — ANALYSE DES FLUX MÉTIER

Ce chapitre décrit tous les échanges d'information entre les acteurs de la plateforme. Pour chaque flux, nous précisons qui communique avec qui, quand, pourquoi et comment.
9.1 Flux de données lors du pointage
Code	Source → Cible	Contenu	Canal
FL-01	Employé → Système	Données de pointage : type (arrivée/départ), coordonnées GPS, précision GPS, photo (JPEG base64), heure client, user-agent.	HTTPS POST — multipart/form-data
FL-02	Système → Employé	Confirmation : statut du pointage, heure enregistrée, statut (À l'heure/Retard/Hors horaire), message d'information.	Réponse JSON synchrone
FL-03	Système → Manager	Notification retard : 'X a pointé avec N min de retard.'	Push + In-app
FL-04	Système → Administrateur	Notification anomalie GPS simulé ou pointage hors zone.	E-mail + In-app
FL-05	Service Worker → Serveur	Synchronisation offline : envoi de pointages stockés en IndexedDB.	HTTPS POST — background sync
FL-06	Système → Employé	Confirmation de synchronisation offline réussie.	Push
9.2 Flux de données lors de la gestion des absences
Code	Source → Cible	Contenu	Canal
FL-10	Système → Employé	Notification absence détectée : 'Vous êtes marqué absent pour aujourd'hui. Soumettez un justificatif si nécessaire.'	E-mail + Push + In-app
FL-11	Système → Manager	Alerte absence : 'X est absent aujourd'hui sans justificatif.'	Push + In-app
FL-12	Employé → Système	Soumission justificatif : motif sélectionné, commentaire, fichiers joints (PDF/Image).	HTTPS POST — multipart
FL-13	Système → Manager	Notification nouveau justificatif : 'X a soumis un justificatif d'absence pour [date].'	E-mail + In-app
FL-14	Manager → Système	Décision sur justificatif : approbation ou rejet avec commentaire.	HTTPS POST — JSON
FL-15	Système → Employé	Notification de décision : 'Votre justificatif a été approuvé/rejeté. Motif : [commentaire].'	E-mail + Push
9.3 Flux de données lors de la gestion des congés
Code	Source → Cible	Contenu	Canal
FL-20	Employé → Système	Demande de congé : type, dates, commentaire.	HTTPS POST — JSON
FL-21	Système → Employé	Confirmation de réception et informations : solde actuel, nb jours demandés, solde prévisionnel.	Réponse JSON + E-mail
FL-22	Système → Manager/Admin	Notification nouvelle demande : 'X demande [N] jours de congé du [date] au [date].'	E-mail + In-app
FL-23	Manager → Système	Décision congé : approbation ou rejet avec commentaire.	HTTPS POST — JSON
FL-24	Système → Employé	Notification décision : 'Votre congé a été approuvé/rejeté. Solde restant : [N] jours.'	E-mail + Push
FL-25	Système → Manager/Admin	Résumé hebdomadaire des congés approuvés : planning de l'équipe.	E-mail automatique
9.4 Flux de données administratifs
Code	Source → Cible	Contenu	Canal
FL-30	Super Admin → Système	Création organisation : toutes les informations de configuration initiale.	HTTPS POST — JSON
FL-31	Système → Admin	E-mail de bienvenue : accès, URL de connexion, mot de passe temporaire.	E-mail SMTP
FL-32	Admin → Système	Configuration organisation : agences, horaires, employés, paramètres.	HTTPS POST/PUT — JSON
FL-33	Admin → Système	Import employés : fichier CSV/Excel.	HTTPS POST — multipart
FL-34	Système → Admin	Rapport d'import : lignes importées, lignes en erreur (avec détails), lignes ignorées.	E-mail + Fichier Excel
FL-35	Super Admin → Système	Suspension organisation.	HTTPS POST — JSON
FL-36	Système → Admin	Notification suspension : 'Votre organisation a été suspendue. Contactez [e-mail support].'	E-mail
FL-37	Système → Employés	Notification suspension : déconnexion forcée avec message.	Invalidation session
9.5 Flux de données des rapports
Code	Source → Cible	Contenu	Canal
FL-40	Admin/Manager → Système	Demande de rapport : type, période, filtres, format souhaité.	HTTPS GET/POST — JSON
FL-41	Système → File Celery	Tâche asynchrone de génération du rapport.	Queue Redis
FL-42	Celery → Système	Fichier rapport généré (PDF, Excel, CSV).	Stockage fichier
FL-43	Système → Admin/Manager	Notification rapport prêt : 'Votre rapport est disponible. Lien : [URL]. Valide 7 jours.'	E-mail + In-app
FL-44	Admin → Système	Téléchargement du rapport via lien sécurisé (token URL unique).	HTTPS GET — fichier
FL-45	Système → Admin	Rapport automatique quotidien/hebdo/mensuel.	E-mail avec fichier joint
9.6 Flux de données IA
Code	Source → Cible	Contenu	Canal
FL-50	Utilisateur → Système	Question en langage naturel saisie dans l'interface de chat.	HTTPS POST — JSON
FL-51	Système → BDD	Requête de données pertinentes (limitées au tenant).	ORM Django — MySQL
FL-52	Système → API IA externe	Prompt structuré : contexte + données + question + contraintes.	HTTPS POST — JSON (API fournisseur)
FL-53	API IA → Système	Réponse de l'IA : texte structuré.	HTTPS — JSON stream
FL-54	Système → Utilisateur	Affichage de la réponse dans l'interface de chat.	WebSocket ou polling
FL-55	Système → Journal	Enregistrement de la question, réponse, tokens utilisés, timestamp.	Écriture BDD
FL-56	Système → Admin	Rapport IA automatique quotidien/hebdomadaire.	E-mail
9.7 Flux de données de sécurité
Code	Source → Cible	Contenu	Canal
FL-60	Employé → Système	Tentative de connexion : e-mail + mot de passe hashé.	HTTPS POST — JSON
FL-61	Système → Employé	Résultat connexion : succès (token session) ou échec (message générique).	Réponse JSON + Cookie session
FL-62	Système → Employé	Notification de blocage de compte.	E-mail
FL-63	Système → Admin	Alerte de sécurité : tentatives répétées, GPS simulé, accès suspect.	E-mail + In-app
FL-64	Employé → Système	Demande réinitialisation mot de passe : e-mail.	HTTPS POST — JSON
FL-65	Système → Employé	E-mail avec lien de réinitialisation sécurisé (token UUID, expire 30min).	E-mail SMTP
FL-66	Système → Journal Audit	Enregistrement de tous les événements sécurité.	Écriture BDD — INSERT only

CHAPITRE 10 — ANALYSE DES RISQUES MÉTIER

Ce chapitre identifie et analyse tous les risques pouvant affecter la plateforme, ses utilisateurs et les organisations clientes. Chaque risque est évalué selon sa probabilité, son impact et est accompagné de mesures préventives et d'un plan de mitigation.
10.1 Risques organisationnels
ID	Risque et description	Probabilité	Impact
RO-01	Résistance au changement des employés Les employés peuvent percevoir le système comme une surveillance intrusive. Refus d'utilisation, contournements, tensions sociales.	ÉLEVÉE	ÉLEVÉ
RO-02	Non-adoption par les managers Les managers ne consultent pas les tableaux de bord, ne traitent pas les demandes en temps voulu. La valeur de la plateforme n'est pas exploitée.	MOYENNE	ÉLEVÉ
RO-03	Mauvaise configuration initiale L'Administrateur configure incorrectement les zones GPS, les horaires ou les affectations. Les données générées sont incorrectes.	ÉLEVÉE	ÉLEVÉ
RO-04	Turn-over de l'Administrateur L'Administrateur initial quitte l'organisation sans former son successeur. L'organisation perd la maîtrise de la plateforme.	MOYENNE	ÉLEVÉ
RO-05	Données GPS incorrectes pour les agences Les coordonnées GPS saisies pour une agence sont incorrectes. Tous les pointages depuis cette agence sont refusés.	MOYENNE	CRITIQUE
RO-06	Sur-dimensionnement ou sous-dimensionnement La plateforme est déployée dans une organisation dont la taille ou les besoins ne correspondent pas aux capacités du système.	FAIBLE	MOYEN
10.1.1 Mesures préventives et plans de mitigation
Risque	Mesures préventives et mitigation
RO-01 — Communication et formation	Programme de communication préalable expliquant l'objectif de la plateforme (fiabilité, équité, pas de surveillance). Formation obligatoire des employés avant déploiement. Notice RGPD claire dans l'interface. Politique de confidentialité transparente sur l'usage des photos.
RO-02 — Engagement managérial	Formation obligatoire des managers. Intégration des KPI de la plateforme dans les objectifs managériaux. Simplification maximale de l'interface manager. Alertes automatiques pour réduire la nécessité d'une consultation proactive.
RO-03 — Wizard de configuration guidé	Wizard de configuration step-by-step avec validations à chaque étape. Outil de test GPS intégré (l'Admin peut tester la zone depuis l'interface avant de la valider). Templates de configuration par type d'organisation.
RO-04 — Gestion multi-administrateurs	Permettre la création de plusieurs comptes Administrateur. Documentation de prise en main complète. Sauvegarde de la configuration de l'organisation accessible à tout nouveau Admin.
RO-05 — Validation GPS à la configuration	Outil de visualisation de la zone GPS sur carte avant validation. Possibilité de simuler un test de pointage depuis l'interface d'administration. Alerte si rayon GPS inférieur à 50m.
10.2 Risques techniques
ID	Risque et description	Probabilité	Impact
RT-01	Indisponibilité du service GPS sur l'appareil GPS désactivé, permission refusée, environnement sans signal (sous-sol, intérieur). Blocage des pointages.	ÉLEVÉE	ÉLEVÉ
RT-02	Perte de connexion Internet L'employé ne peut pas envoyer son pointage en temps réel.	ÉLEVÉE	MOYEN
RT-03	Panne de l'infrastructure serveur Indisponibilité de la plateforme. Impossible de pointer, de consulter, d'exporter.	FAIBLE	CRITIQUE
RT-04	Corruption ou perte de données Panne de base de données, suppression accidentelle, corruption de fichiers.	TRÈS FAIBLE	CRITIQUE
RT-05	Dégradation des performances Trop d'utilisateurs simultanés, requêtes non optimisées, manque de ressources serveur.	MOYENNE	ÉLEVÉ
RT-06	Incompatibilité navigateur/appareil L'application ne fonctionne pas sur certains navigateurs ou versions d'OS.	MOYENNE	MOYEN
RT-07	Indisponibilité du fournisseur IA L'API du fournisseur IA est indisponible. Les fonctionnalités IA sont inaccessibles.	MOYENNE	MOYEN
RT-08	Quota e-mail SMTP dépassé Le serveur SMTP atteint sa limite. Les notifications e-mail ne sont plus envoyées.	FAIBLE	ÉLEVÉ
10.2.1 Mesures préventives et plans de mitigation
Risque	Mesures préventives et mitigation
RT-01 — GPS indisponible	Mode hors ligne avec stockage IndexedDB. Mode de validation manuelle configurable pour les cas d'exception. Instructions claires dans l'interface pour activer le GPS. Documentation des environnements sans GPS communiquée lors du déploiement.
RT-02 — Perte connexion	PWA avec Service Worker. Stockage local IndexedDB. Synchronisation automatique à la reconnexion. Indicateur visuel de l'état de connexion dans l'interface.
RT-03 — Panne serveur	Architecture Docker avec redémarrage automatique des conteneurs. Sauvegardes automatiques quotidiennes. Plan de reprise d'activité (RTO < 4h). Monitoring 24/7 avec alertes.
RT-04 — Perte de données	Sauvegardes automatiques quotidiennes sur plusieurs emplacements géographiques. Chiffrement des sauvegardes. Tests de restauration hebdomadaires. RPO < 6h.
RT-05 — Performances	Index de base de données optimisés. Cache Redis pour les données fréquentes. Pagination obligatoire. Tâches lourdes asynchrones (Celery). Monitoring des temps de réponse avec alertes.
RT-07 — IA indisponible	Dégradation gracieuse : si l'IA est indisponible, les fonctionnalités core (pointage, rapports) continuent normalement. Alerte à l'Administrateur. Retry automatique. Possibilité de changer de fournisseur.
10.3 Risques humains
ID	Risque et description	Probabilité	Impact
RH-01	Erreur de saisie par l'Administrateur Création d'un employé avec la mauvaise adresse e-mail, mauvaise agence, mauvais horaire.	ÉLEVÉE	MOYEN
RH-02	Oubli de pointage par l'employé L'employé oublie de pointer son arrivée ou son départ.	TRÈS ÉLEVÉE	FAIBLE
RH-03	Utilisation abusive des droits d'administration Un Administrateur modifie des pointages, supprime des absences ou crée de faux enregistrements.	FAIBLE	ÉLEVÉ
RH-04	Pression managériale Un manager force des employés à pointer depuis des zones non autorisées ou à des heures incorrectes.	FAIBLE	ÉLEVÉ
RH-05	Partage de compte Deux employés utilisent le même compte.	FAIBLE	ÉLEVÉ
RH-06	Perte/vol du mot de passe Un employé perd l'accès à son compte.	MOYENNE	FAIBLE
10.3.1 Mesures préventives et plans de mitigation
Risque	Mesures préventives et mitigation
RH-01 — Erreurs saisie	Validation des données côté client et serveur. Confirmation avant enregistrement. Possibilité de corriger sans perte de données. Notification à l'employé lors de la création (e-mail avec ses informations pour vérification).
RH-02 — Oubli pointage	Notification push rappelant de pointer si l'employé est détecté dans la zone GPS sans avoir pointé (géofencing entrant/sortant - fonctionnalité optionnelle). Alerte au Manager. Possibilité de saisie manuelle par le Manager avec justification.
RH-03 — Abus administrateur	Journal d'audit inaltérable enregistrant toutes les modifications. Rapport mensuel des modifications de pointages envoyé au Super Admin. Séparation des rôles (un Admin ne peut pas se modifier lui-même).
RH-05 — Partage de compte	La combinaison photo + GPS rend le partage difficile à pratiquer discrètement. Détection de connexions simultanées depuis plusieurs appareils (alerte).
10.4 Risques de fraude
ID	Risque et description	Probabilité	Impact
RF-01	Buddy punching Un employé demande à un collègue de pointer à sa place. C'est la fraude la plus répandue dans les systèmes de pointage traditionnels.	TRÈS FAIBLE (avec photo)	ÉLEVÉ
RF-02	Falsification GPS (mock location) L'employé utilise une application de simulation GPS pour usurper une position.	FAIBLE	ÉLEVÉ
RF-03	Manipulation de l'heure système L'employé modifie l'heure de son appareil pour falsifier l'heure du pointage.	FAIBLE	ÉLEVÉ
RF-04	Photo pré-enregistrée / Deepfake L'employé tente d'utiliser une photo statique ou générée par IA à la place d'une photo en direct.	TRÈS FAIBLE	ÉLEVÉ
RF-05	Contournement de la zone GPS L'employé se déplace jusqu'à la zone autorisée, pointe, puis repart.	FAIBLE	FAIBLE
RF-06	Falsification de justificatif d'absence L'employé soumet un faux document médical ou autre justificatif.	MOYENNE	MOYEN
RF-07	Partage de session Un employé laisse sa session active pour qu'un collègue l'utilise.	TRÈS FAIBLE	ÉLEVÉ
10.4.1 Mesures préventives et plans de mitigation
Risque	Mesures préventives et mitigation
RF-01 — Buddy punching	Photo obligatoire en temps réel par la caméra. L'identité du pointeur est visuellement vérifiable. La photo est visible par l'Administrateur et le Manager. Combinaison GPS + Photo rend la fraude quasi impossible à distance.
RF-02 — GPS simulé	Détection de l'attribut isMock via l'API Geolocation du navigateur. Refus immédiat si détecté. Alerte Administrateur. Log avec flag spécifique pour investigation.
RF-03 — Manipulation heure	L'heure de référence est l'heure serveur, jamais l'heure client. La divergence entre heure client et heure serveur est enregistrée pour analyse.
RF-04 — Fausse photo	Contrainte caméra frontale exclusive (facingMode: 'user'). Pas d'accès à l'API de téléchargement de fichier. La photo est capturée directement depuis le flux vidéo en direct. Analyse manuelle possible par l'Admin en cas de doute.
RF-06 — Faux justificatif	Le Manager ou l'Admin doit valider chaque justificatif. Ils peuvent rejeter tout justificatif ne semblant pas authentique. La décision est tracée dans l'audit trail.
10.5 Risques de sécurité informatique
ID	Risque et description	Probabilité	Impact
RSEC-01	Injection SQL Attaque visant à exécuter du code SQL malveillant via les formulaires.	FAIBLE (ORM)	CRITIQUE
RSEC-02	Cross-Site Scripting (XSS) Injection de scripts malveillants dans l'interface.	FAIBLE (templates)	ÉLEVÉ
RSEC-03	CSRF (Cross-Site Request Forgery) Forcé un utilisateur connecté à effectuer des actions non désirées.	FAIBLE (token CSRF)	ÉLEVÉ
RSEC-04	Session Hijacking Vol du token de session d'un utilisateur.	FAIBLE	CRITIQUE
RSEC-05	Brute Force / Credential Stuffing Tentatives massives de connexion avec des mots de passe ou listes de credentials.	ÉLEVÉE	ÉLEVÉ
RSEC-06	Violation de l'isolation multi-tenant Un utilisateur parvient à accéder aux données d'un autre tenant.	TRÈS FAIBLE	CRITIQUE
RSEC-07	Compromission de l'API IA La clé API du fournisseur IA est volée et utilisée frauduleusement.	FAIBLE	ÉLEVÉ
RSEC-08	Upload de fichier malveillant Un fichier malveillant est uploadé via le formulaire de justificatif.	FAIBLE	ÉLEVÉ
10.5.1 Mesures préventives et plans de mitigation
Risque	Mesures préventives et mitigation
RSEC-01 — SQL Injection	ORM Django exclusif pour toutes les requêtes (paramètrisation automatique). Interdiction des requêtes SQL brutes sauf cas exceptionnels documentés. SAST automatique dans le pipeline CI/CD.
RSEC-04 — Session Hijacking	Cookies httpOnly, Secure, SameSite=Strict. Stockage des sessions côté serveur (Redis). Expiration automatique. Régénération du session ID après connexion. Détection de changement d'IP en session.
RSEC-05 — Brute Force	Blocage progressif après N échecs. CAPTCHA après 3 échecs. Rate limiting par IP (10 tentatives/minute). Notification à l'utilisateur. Alertes Administrateur.
RSEC-06 — Cross-Tenant	Middleware tenant Django vérifiant chaque requête. Manager Django personnalisé filtrant automatiquement par tenant_id. Tests d'intégration couvrant les tentatives cross-tenant.
RSEC-07 — Clé API IA	Clés API chiffrées en base de données. Stockage dans les variables d'environnement Docker. Rotation régulière des clés. Limitation du scope des clés API.
RSEC-08 — Upload malveillant	Validation MIME côté serveur. Restriction des formats acceptés. Stockage hors racine web. Scan antivirus (ClamAV recommandé). Renommage UUID des fichiers.
10.6 Risques liés aux données
ID	Risque et description	Probabilité	Impact
RD-01	Non-conformité RGPD Collecte excessive de données, absence de base légale, non-respect des droits des personnes.	MOYENNE	CRITIQUE
RD-02	Demande d'effacement en conflit avec conservation légale Un employé demande l'effacement de ses données alors que l'organisation a l'obligation légale de les conserver.	FAIBLE	ÉLEVÉ
RD-03	Fuite de données (data breach) Accès non autorisé à des données personnelles (photos, positions GPS, informations personnelles).	TRÈS FAIBLE	CRITIQUE
RD-04	Qualité des données dégradée Erreurs d'affectation (mauvais horaire, mauvaise agence) produisant des données de présence incorrectes.	MOYENNE	ÉLEVÉ
10.6.1 Mesures préventives et plans de mitigation
Risque	Mesures préventives et mitigation
RD-01 — Non-conformité RGPD	DPA signé avec chaque organisation cliente (Responsable du traitement). Notice RGPD dans l'interface. Registre des traitements maintenu. DPO (Délégué à la Protection des Données) désigné côté éditeur. Audit RGPD annuel.
RD-02 — Effacement vs conservation	Interface permettant l'anonymisation des données personnelles (remplacement par des identifiants anonymes) tout en conservant les données statistiques nécessaires. Documentation des durées légales par pays.
RD-03 — Fuite de données	Chiffrement TLS en transit. Chiffrement AES-256 au repos pour les données sensibles. Accès restreint aux photos. Segmentation réseau en production. Audit de sécurité annuel. Plan de réponse aux incidents (notification CNIL dans les 72h).

CHAPITRE 11 — ANALYSE DE LA VALEUR MÉTIER

Ce chapitre analyse et quantifie les bénéfices apportés par la plateforme à chaque catégorie de parties prenantes. Cette analyse de valeur justifie l'investissement dans la solution et constitue le socle du discours commercial.
11.1 Valeur pour l'éditeur SaaS
Bénéfice	Description
Revenus récurrents (ARR)	Modèle SaaS par abonnement mensuel/annuel générant des revenus prévisibles et croissants.
Faibles coûts de support	L'automatisation poussée et l'interface intuitive réduisent les sollicitations du support client.
Scalabilité économique	L'architecture multi-tenant permet de servir des centaines d'organisations avec une seule infrastructure. Le coût marginal d'un nouveau tenant est quasi-nul.
Différenciation concurrentielle	La combinaison GPS + Photo + IA + Multi-secteur est un positionnement différenciant par rapport aux outils de pointage classiques.
Données agrégées (anonymisées)	Les données d'utilisation agrégées permettent d'améliorer continuellement le produit.
11.2 Valeur pour l'organisation cliente (Direction Générale)
Bénéfice	Description
Réduction des coûts de fraude	Élimination quasi-totale du buddy punching. Pour une organisation de 100 employés, cela peut représenter 1 à 5% de la masse salariale économisée (estimation : 10 000 à 50 000 € selon le niveau de salaire).
Réduction des coûts administratifs RH	Automatisation des calculs de présence, de retards, d'heures sup. Réduction estimée à 80% du temps de traitement RH. Pour un équivalent 0,5 ETP RH, économie estimée à 15 000-20 000 €/an.
Conformité légale	Preuve du respect des durées légales de travail. Réduction du risque de sanctions légales et de litiges sociaux coûteux.
Décisions managériales éclairées	Les rapports et tableaux de bord permettent des décisions basées sur des données objectives plutôt que sur des impressions.
Image employeur	Un outil moderne, équitable et transparent améliore la perception de l'organisation par les employés.
ROI estimé	Sur la base des gains précédents, le ROI de la plateforme est généralement atteint en moins de 6 mois pour les organisations de plus de 20 employés.
11.3 Valeur pour les managers
Bénéfice	Description
Visibilité temps réel	Le manager sait en permanence qui est présent, absent ou en retard dans son équipe, sans avoir à appeler chaque employé.
Réduction des conflits	Des données objectives et incontestables éliminent les désaccords sur les heures de travail.
Gain de temps	Les alertes automatiques remplacent la surveillance manuelle. Le manager est averti des anomalies sans avoir à les chercher.
Planification facilitée	L'historique des absences et des congés permet une meilleure anticipation des besoins en effectif.
Rapports automatiques	Les rapports hebdomadaires sont générés et envoyés automatiquement, sans intervention du manager.
11.4 Valeur pour les employés
Bénéfice	Description
Équité et transparence	Les règles de présence sont identiques pour tous et appliquées de façon identique. Pas de favoritisme possible.
Accès à ses propres données	Chaque employé peut consulter son historique de présence, ses soldes de congés et ses statistiques personnelles à tout moment.
Simplification administrative	Les demandes de congé et les justificatifs d'absence sont soumis en quelques clics depuis le smartphone.
Rapidité du pointage	Le pointage est réalisé en moins de 10 secondes depuis le smartphone. Pas de file d'attente devant une pointeuse.
Notifications claires	L'employé est informé immédiatement de toute décision sur ses demandes.
Fiabilité	L'employé a la certitude que son pointage est bien enregistré (confirmation immédiate) et que ses données sont exactes.
11.5 Valeur pour les enseignants
Bénéfice	Description
Pointage par créneau	L'enseignant ne pointe que pour ses cours, pas pour toute une journée. Cela correspond à la réalité de son activité.
Pas de fausses absences	Le système ne génère jamais d'absence pour un jour sans cours. L'enseignant n'a pas à justifier des absences fictives.
Visibilité de son emploi du temps	L'interface affiche clairement les créneaux du jour et le statut de chaque intervention.
Gestion simplifiée des remplacements	Un créneau annulé peut être marqué et réattribué sans impacter les statistiques de l'enseignant responsable.
11.6 Valeur pour les responsables RH
Bénéfice	Description
Données paie précises	Les exports de présence sont directement exploitables pour le calcul de la paie, réduisant les erreurs et les re-traitements.
Gestion des soldes automatisée	Les soldes de congés sont mis à jour automatiquement à chaque approbation ou annulation. Pas de calcul manuel.
Alertes d'absentéisme	Le système alerte automatiquement les RH lorsqu'un employé dépasse un seuil d'absences répétées.
Archivage documentaire sécurisé	Les justificatifs d'absence sont stockés de façon sécurisée et retrouvables facilement.
Conformité légale facilitée	En cas d'inspection du travail ou de litige, les données de présence sont disponibles, horodatées et inaltérables.
Analyse RH avancée	Les rapports permettent d'identifier les tendances d'absentéisme par département, âge, type de contrat, etc.

CHAPITRE 12 — INDICATEURS MÉTIER (KPI)

Ce chapitre définit tous les indicateurs clés de performance (KPI) de la plateforme. Chaque KPI est défini avec son nom, sa formule de calcul, sa fréquence de mise à jour, son propriétaire et ses seuils d'alerte.
12.1 KPI de présence
Code	KPI et formule de calcul	Fréquence	Responsable
KPI-01	Taux de présence (Nb employés présents / Nb employés devant être présents) × 100. Ex : 45 présents / 50 attendus = 90%.	Temps réel / Quotidien	Admin, Manager
KPI-02	Taux d'absence (Nb jours d'absence / Nb jours de travail théoriques) × 100 sur une période. Ex : 15 jours absents / 200 jours théoriques = 7.5%.	Hebdomadaire / Mensuel	Admin, RH
KPI-03	Taux de ponctualité (Nb pointages à l'heure / Nb total de pointages d'arrivée) × 100. Ex : 180 ponctuels / 200 total = 90%.	Quotidien / Hebdomadaire	Manager, Admin
KPI-04	Taux de retard (Nb pointages en retard / Nb total de pointages d'arrivée) × 100.	Quotidien / Hebdomadaire	Manager, Admin
KPI-05	Durée moyenne de retard Somme des retards en minutes / Nb de retards. Ex : 450 min / 30 retards = 15 min de retard moyen.	Hebdomadaire / Mensuel	Admin, RH
KPI-06	Taux d'absence justifiée (Nb jours absences justifiées / Nb total jours absents) × 100.	Mensuel	RH, Admin
KPI-07	Taux d'absence non justifiée (Nb jours absences non justifiées / Nb total jours absents) × 100.	Mensuel	RH, Admin, Manager
12.2 KPI de temps de travail
Code	KPI et formule de calcul	Fréquence	Responsable
KPI-08	Heures supplémentaires cumulées Somme de toutes les heures supplémentaires sur la période. Disponible par employé, par département, par agence.	Hebdomadaire / Mensuel	RH, Admin
KPI-09	Heures de départ anticipé cumulées Somme de toutes les minutes de départ anticipé sur la période.	Mensuel	Admin, Manager
KPI-10	Durée moyenne de présence quotidienne Somme des durées de présence / Nb de jours avec pointage arrivée ET départ.	Hebdomadaire / Mensuel	Admin, RH
KPI-11	Écart moyen temps prévu / temps réel (Durée réelle − Durée théorique) moyen sur la période. Positif = heures sup. Négatif = déficit.	Mensuel	Admin, RH
KPI-12	Fréquence d'oubli de pointage de départ Nb de pointages d'arrivée sans pointage de départ correspondant / Nb total de pointages d'arrivée.	Hebdomadaire	Manager, Admin
12.3 KPI de congés
Code	KPI et formule de calcul	Fréquence	Responsable
KPI-13	Solde moyen de congés restant Somme des soldes de congés restants / Nb d'employés actifs. Alerte si solde moyen < seuil (risque de concentration de congés en fin d'année).	Mensuel	RH, Admin
KPI-14	Taux d'utilisation des congés (Nb jours de congés pris / Nb jours de congés acquis) × 100 sur l'année.	Trimestriel / Annuel	RH, Admin
KPI-15	Délai moyen de traitement des demandes de congé Durée moyenne entre la soumission et la décision (en heures ouvrées). Objectif : < 48h ouvrées.	Mensuel	Admin
KPI-16	Taux de refus des demandes de congé (Nb demandes refusées / Nb total de demandes) × 100.	Mensuel	Admin, RH
12.4 KPI de qualité des données
Code	KPI et formule de calcul	Fréquence	Responsable
KPI-17	Taux de pointages hors ligne (Nb pointages hors ligne / Nb total pointages) × 100. Un taux élevé peut indiquer des problèmes de connectivité sur un site.	Hebdomadaire	Admin
KPI-18	Taux de pointages en validation manuelle (Nb pointages EN_ATTENTE_VALIDATION / Nb total pointages) × 100. Objectif : < 2%.	Hebdomadaire	Admin
KPI-19	Taux de modifications manuelles de pointages (Nb pointages modifiés manuellement / Nb total pointages) × 100. Un taux élevé peut indiquer des problèmes de configuration.	Mensuel	Admin, Audit
KPI-20	Taux de détection GPS simulé Nb de tentatives de GPS simulé détectées sur la période.	Mensuel	Admin, Sécurité
12.5 KPI d'utilisation de la plateforme
Code	KPI et formule de calcul	Fréquence	Responsable
KPI-21	Taux d'adoption (Nb employés ayant pointé au moins une fois / Nb employés actifs) × 100. Objectif : 100% dans les 2 semaines suivant le déploiement.	Hebdomadaire (post-déploiement)	Admin
KPI-22	Fréquence d'utilisation de l'IA Nb de requêtes IA par utilisateur par semaine.	Hebdomadaire	Admin
KPI-23	Taux de satisfaction des notifications Nb de notifications lues / Nb de notifications envoyées. Proxy de l'engagement.	Mensuel	Admin
KPI-24	Temps moyen de pointage Durée moyenne entre l'ouverture de l'interface et la confirmation du pointage. Objectif : < 10 secondes.	Mensuel	Éditeur SaaS
KPI-25	Disponibilité de la plateforme (Nb minutes disponibles / Nb minutes totales) × 100 sur le mois. Objectif : ≥ 99.5%.	Mensuel	Éditeur SaaS
12.6 KPI spécifiques aux établissements scolaires
Code	KPI et formule de calcul	Fréquence	Responsable
KPI-ED-01	Taux de présence des enseignants par créneau (Nb créneaux avec pointage / Nb créneaux planifiés) × 100.	Hebdomadaire	Directeur
KPI-ED-02	Nb de cours annulés sur la période Nb de créneaux planifiés marqués comme annulés.	Hebdomadaire	Directeur
KPI-ED-03	Taux de remplacement (Nb cours remplacés / Nb cours annulés) × 100.	Mensuel	Directeur, Admin
12.7 Seuils d'alerte recommandés
Seuil d'alerte	Action recommandée
Taux de présence < 80%	Alerte critique au Manager et à l'Administrateur. Analyse des causes requise.
Taux d'absence > 10% sur un mois	Alerte à la direction RH. Recommandation d'entretien managérial par l'IA.
Taux de retard > 15%	Alerte au Manager. Analyse de la cause : problème d'horaire, de transport, ou comportemental.
Taux d'absence non justifiée > 5%	Alerte RH. Politique de justification à renforcer.
Solde congés moyen < 5 jours en octobre	Alerte RH : risque de surcharge de congés en fin d'année.
Nb de GPS simulés > 0	Alerte immédiate à l'Administrateur et au Manager. Investigation requise.
Taux de pointages en validation manuelle > 5%	Alerte Admin : problème de configuration ou de connectivité.
Délai de traitement congés > 72h	Alerte Admin : des demandes en attente ne sont pas traitées dans les délais.

CHAPITRE 13 — GLOSSAIRE MÉTIER

Ce chapitre définit tous les termes métier utilisés dans la plateforme et dans ce document d'analyse métier. Ce glossaire constitue le vocabulaire de référence partagé entre toutes les parties prenantes du projet.
13.1 Termes organisationnels
Terme	Définition
Organisation / Tenant	Entité cliente de la plateforme SaaS disposant de son propre espace de données isolé. Peut être une entreprise, une école, un hôpital, une ONG, etc.
Multi-tenant	Architecture logicielle où une seule instance du logiciel sert plusieurs organisations clientes de façon totalement isolée.
Agence	Site géographique physique appartenant à une organisation. Unité de base de la gestion des présences. Dispose de ses propres coordonnées GPS et de son rayon de geofencing.
Département	Division organisationnelle d'une organisation regroupant des employés ayant des fonctions similaires (ex : Comptabilité, Logistique, Commercial).
Poste	Fonction ou intitulé de poste d'un employé (ex : Caissier, Infirmier, Enseignant de Mathématiques).
Équipe	Groupe d'employés managés par un même responsable. Peut traverser plusieurs départements.
Hiérarchie organisationnelle	Structure de commandement : Agence → Département → Équipe → Employé.
Onboarding	Processus d'intégration d'une nouvelle organisation sur la plateforme, depuis la création du tenant jusqu'à la première utilisation opérationnelle.
Tenant ID	Identifiant unique UUID d'une organisation sur la plateforme. Présent dans toutes les tables de données pour assurer l'isolation.
13.2 Termes liés aux utilisateurs
Terme	Définition
Super Administrateur	Opérateur global de la plateforme SaaS, appartenant à l'équipe de l'éditeur. Gère les organisations mais n'accède jamais aux données opérationnelles.
Administrateur d'organisation	Responsable de la configuration et de la gestion complète d'une organisation sur la plateforme.
Manager	Responsable d'une équipe, avec accès aux données de présence de ses membres uniquement.
Superviseur	Rôle intermédiaire pouvant superviser plusieurs équipes ou un département. Droits configurables par l'Administrateur.
Employé	Membre du personnel d'une organisation utilisant la plateforme pour pointer et gérer ses données personnelles.
Enseignant	Variante de l'employé avec des horaires discontinus basés sur un emploi du temps de créneaux de cours.
RBAC	Role-Based Access Control — Contrôle d'accès basé sur les rôles. Chaque utilisateur dispose uniquement des accès nécessaires à son rôle.
Session	Période d'authentification active d'un utilisateur. La session expire après inactivité ou après la durée maximale configurée.
13.3 Termes liés au pointage
Terme	Définition
Pointage	Action d'enregistrement de la présence d'un employé (arrivée ou départ) via l'application, avec vérification GPS et capture photo.
Pointage d'arrivée	Enregistrement de l'heure d'arrivée de l'employé sur son lieu de travail.
Pointage de départ	Enregistrement de l'heure de départ de l'employé de son lieu de travail.
Buddy punching	Fraude consistant pour un employé à faire pointer un collègue à sa place. Pratique éliminée par la combinaison GPS + photo en direct.
Mock location / GPS simulé	Simulation d'une position GPS différente de la position réelle, effectuée via une application tierce. Détectée et rejetée par le système.
Géolocalisation	Détermination de la position géographique d'un appareil via le système GPS.
Geofencing (Géorepérage)	Technologie de délimitation d'une zone géographique virtuelle. Le pointage est autorisé uniquement si l'employé se trouve dans cette zone.
Formule Haversine	Formule mathématique utilisée pour calculer la distance entre deux points sur la surface d'une sphère (la Terre). Utilisée pour le calcul de la distance entre l'employé et le centre de la zone autorisée.
Rayon GPS	Distance en mètres définissant le périmètre circulaire autour du centre d'une agence à l'intérieur duquel le pointage est autorisé.
Tolérance GPS	Marge supplémentaire (en mètres) ajoutée au rayon GPS pour tenir compte de l'imprécision des GPS de smartphones.
Photo de pointage	Photo prise en temps réel par la caméra frontale de l'appareil lors du pointage. Preuve biométrique de présence physique.
Mode hors ligne	Fonctionnement de l'application sans connexion Internet. Les pointages sont stockés localement et synchronisés à la reconnexion.
Service Worker	Script JavaScript s'exécutant en arrière-plan dans le navigateur, gérant le cache, le mode hors ligne et les notifications push.
IndexedDB	Base de données locale dans le navigateur utilisée pour stocker les pointages hors ligne de façon chiffrée.
Synchronisation	Transfert automatique des pointages hors ligne vers le serveur dès que la connexion Internet est rétablie.
13.4 Termes liés aux horaires
Terme	Définition
Horaire fixe	Type d'horaire définissant la même plage de travail chaque jour ouvrable (ex : 08h00-17h00 du lundi au vendredi).
Horaire par équipe	Type d'horaire définissant des rotations d'équipes (matin, après-midi, nuit) avec des plages différentes selon l'équipe affectée.
Horaire personnalisé	Type d'horaire défini spécifiquement pour un individu, prenant le dessus sur les horaires de poste ou de département.
Horaire enseignant	Type d'horaire basé sur un emploi du temps de créneaux de cours. Les absences ne sont générées que pour les créneaux planifiés.
Fenêtre de pointage	Plage temporelle pendant laquelle le pointage est accepté (avant et après l'heure théorique). En dehors, le pointage est rejeté ou marqué hors horaire.
Tolérance de retard	Nombre de minutes de grâce accordées après l'heure prévue avant de comptabiliser un retard officiel.
Tolérance de départ anticipé	Nombre de minutes avant l'heure de fin planifiée à partir duquel un départ anticipé est comptabilisé.
Seuil heures supplémentaires	Nombre de minutes au-delà de l'heure de fin à partir duquel les heures supplémentaires sont comptabilisées.
Plage horaire	Intervalle de temps délimitant le début et la fin d'une période de travail pour un horaire donné.
Créneau (enseignants)	Période de cours planifiée pour un enseignant (ex : Lundi 10h00-12h00 — Mathématiques — Salle 12).
13.5 Termes liés aux absences et congés
Terme	Définition
Absence	Non-présence d'un employé sur son lieu de travail lors d'une plage où sa présence est attendue.
Absence non justifiée	Absence pour laquelle aucun justificatif valide n'a été soumis ou approuvé.
Absence justifiée	Absence pour laquelle un justificatif a été soumis et validé par le responsable.
Justificatif d'absence	Document (certificat médical, convocation administrative, etc.) soumis par l'employé pour expliquer une absence.
Congé	Période de repos planifiée et approuvée par le responsable, décomptée du solde de congés de l'employé.
Solde de congés	Nombre de jours de congés restants disponibles pour l'employé.
Congé annuel payé	Type de congé légal rémunéré, acquis progressivement au cours de l'année de travail.
RTT	Réduction du Temps de Travail — jours de repos accordés en compensation des heures travaillées au-delà de 35h/semaine (spécifique France).
Jour férié	Jour non travaillé légalement ou conventionnellement, ne décomptant ni comme absence ni comme congé.
Retard	Arrivée après l'heure de début de travail prévue, au-delà de la tolérance configurée.
Départ anticipé	Départ avant l'heure de fin de travail prévue, en dehors de la tolérance configurée.
Heures supplémentaires	Heures travaillées au-delà de la plage horaire prévue, au-delà du seuil configuré.
Détection automatique	Mécanisme par lequel le système génère automatiquement une absence sans intervention humaine, à l'expiration de la fenêtre de pointage.
13.6 Termes techniques
Terme	Définition
SaaS	Software as a Service — Modèle de distribution de logiciel où l'application est hébergée par l'éditeur et accessible via Internet.
PWA	Progressive Web App — Application web installable sur un appareil comme une application native, fonctionnant hors ligne via Service Worker.
API REST	Interface de programmation suivant le style architectural REST (Representational State Transfer).
ORM	Object-Relational Mapping — Couche d'abstraction entre le code Python et la base de données MySQL (Django ORM).
Celery	Bibliothèque Python de gestion de files de tâches asynchrones. Utilisée pour les exports, notifications, rapports automatiques.
Redis	Base de données en mémoire utilisée comme broker de messages pour Celery et comme cache applicatif.
Docker	Technologie de conteneurisation permettant d'empaqueter une application et ses dépendances dans un conteneur portable.
Middleware	Composant logiciel s'exécutant entre la requête HTTP et le code applicatif. Le middleware tenant identifie et configure le contexte de l'organisation à chaque requête.
UUID	Universally Unique Identifier — Identifiant de 128 bits garantissant l'unicité mondiale sans besoin de coordinateur central.
TLS	Transport Layer Security — Protocole de chiffrement des communications réseau. Successeur de SSL.
HSTS	HTTP Strict Transport Security — En-tête HTTP forçant les navigateurs à toujours utiliser HTTPS.
CSP	Content Security Policy — En-tête HTTP définissant les sources autorisées pour les scripts, styles et médias.
CSRF	Cross-Site Request Forgery — Attaque forçant un utilisateur authentifié à exécuter des actions non désirées.
XSS	Cross-Site Scripting — Injection de scripts malveillants dans une page web.
Argon2id	Algorithme de hachage de mots de passe recommandé par OWASP. Résistant aux attaques GPU et aux attaques par canal auxiliaire.
JWT	JSON Web Token — Format de token compact pour l'échange sécurisé d'informations. Non utilisé pour les sessions (sessions serveur préférées).
VAPID	Voluntary Application Server Identification — Protocole d'identification pour l'envoi de notifications push via l'API Web Push.
Webhook	Mécanisme permettant à un système d'envoyer des notifications HTTP automatiques vers un autre système lors d'événements.
13.7 Termes liés à l'IA
Terme	Définition
LLM	Large Language Model — Modèle de langage de grande taille entraîné sur des corpus massifs de texte. Base des assistants IA (GPT-4, Claude, Mistral).
Prompt	Instruction textuelle envoyée à un modèle IA pour obtenir une réponse.
Context window	Quantité maximale de texte (en tokens) qu'un modèle IA peut traiter en une seule requête.
Token	Unité de traitement d'un modèle IA. Environ 0.75 mots en français. Les coûts IA sont facturés au token.
Hallucination	Réponse incorrecte ou inventée d'un modèle IA présentée avec assurance. Les réponses IA doivent être vérifiées.
RAG	Retrieval-Augmented Generation — Technique d'amélioration des réponses IA en fournissant des données contextuelles extraites d'une base de données.
Ollama	Outil permettant d'exécuter des modèles LLM localement, sans envoyer de données à des serveurs externes.
Fournisseur IA	Entreprise proposant un accès à des modèles IA via API (OpenAI, Anthropic, Mistral AI, etc.).
Quota IA	Limite du nombre de requêtes IA autorisées par mois pour une organisation. Configurable par l'Administrateur.
13.8 Termes liés à la sécurité et la conformité
Terme	Définition
OWASP	Open Web Application Security Project — Organisation internationale produisant des référentiels de sécurité pour les applications web.
OWASP Top 10	Liste des 10 vulnérabilités les plus critiques des applications web publiée par OWASP.
ASVS	Application Security Verification Standard — Standard de vérification de la sécurité applicative OWASP.
RGPD	Règlement Général sur la Protection des Données — Règlement européen (2018) encadrant le traitement des données personnelles.
Données personnelles	Toute information permettant d'identifier directement ou indirectement une personne physique (nom, e-mail, photo, position GPS).
DPA	Data Processing Agreement — Accord entre le responsable du traitement (organisation cliente) et le sous-traitant (éditeur SaaS).
DPO	Data Protection Officer — Délégué à la Protection des Données. Obligatoire pour certaines catégories de traitements.
Audit trail	Journal d'audit complet et inaltérable enregistrant toutes les actions effectuées dans le système.
Principe du moindre privilège	Principe de sécurité selon lequel chaque utilisateur ne dispose que des droits strictement nécessaires à ses fonctions.
Défense en profondeur	Stratégie de sécurité consistant à multiplier les niveaux de protection pour qu'une défaillance n'entraîne pas une compromission totale.
IAM	Identity and Access Management — Gestion des identités et des accès.
SIRET	Système d'Identification du Répertoire des Établissements — Identifiant unique d'un établissement en France.
Chiffrement au repos	Protection des données stockées en les chiffrant sur le support de stockage (disque, base de données).
Chiffrement en transit	Protection des données lors de leur transmission sur le réseau, via TLS/HTTPS.
Pentest	Penetration Testing — Test d'intrusion simulant une attaque réelle pour identifier les vulnérabilités de sécurité.
13.9 Abréviations
Abréviation	Signification
AM	Analyse Métier (ce document)
CDC	Cahier Des Charges
RH	Ressources Humaines
SI	Système d'Information
UX/UI	User Experience / User Interface
BDD	Base De Données
MVP	Minimum Viable Product
SLA	Service Level Agreement — Accord de niveau de service
KPI	Key Performance Indicator — Indicateur Clé de Performance
GPS	Global Positioning System
PWA	Progressive Web App
API	Application Programming Interface
BPMN	Business Process Model and Notation — Notation de modélisation des processus métier
UML	Unified Modeling Language — Langage de modélisation unifié
CDI	Contrat à Durée Indéterminée
CDD	Contrat à Durée Déterminée
ETP	Équivalent Temps Plein
ARR	Annual Recurring Revenue — Revenu annuel récurrent
ROI	Return On Investment — Retour sur investissement
RTO	Recovery Time Objective — Durée maximale d'interruption acceptable
RPO	Recovery Point Objective — Perte de données maximale acceptable
ATSEM	Agent Territorial Spécialisé des Écoles Maternelles (France)
CSE	Comité Social et Économique (France) — Instance représentative du personnel
CNIL	Commission Nationale de l'Informatique et des Libertés (France) — Autorité de protection des données

CONCLUSION DE L'ANALYSE MÉTIER

Cette analyse métier complète constitue la référence fonctionnelle du projet de plateforme SaaS de gestion de présence. Elle a permis d'identifier et de documenter exhaustivement :
    • 13 acteurs distincts avec leurs rôles, responsabilités et interactions.
    • 8 catégories de besoins couvrant tous les aspects fonctionnels, techniques, réglementaires et humains.
    • 14 processus métier détaillés avec déclencheurs, étapes, décisions, exceptions et postconditions.
    • 2 familles de cartographie des processus (principaux, secondaires, support, administration, sécurité, IA).
    • Plus de 50 règles métier identifiées, justifiées et documentées avec leurs exceptions.
    • 7 catégories de contraintes métier couvrant les dimensions horaires, GPS, organisationnelles, légales, sectorielles et IA.
    • 10 entités de données clés avec cycle de vie, propriétaire et niveau de confidentialité.
    • Plus de 40 flux d'information documentés entre tous les acteurs.
    • Plus de 30 risques identifiés avec probabilité, impact et plans de mitigation.
    • Analyse de la valeur métier par acteur avec ROI estimé.
    • 25 KPI définis avec formules de calcul, fréquences et seuils d'alerte.
    • Glossaire complet de plus de 80 termes métier et techniques.

Ce document doit être utilisé comme référence vivante tout au long du développement. Toute évolution du périmètre fonctionnel doit être répercutée dans ce document avant d'être intégrée dans la conception technique.

Les prochaines étapes recommandées sont :
    1. Réalisation des diagrammes BPMN pour les processus principaux (PM-03, PM-04, PM-06, PM-07, PM-08).
    2. Modélisation UML : diagramme de cas d'utilisation, diagramme de classes, diagrammes de séquence.
    3. Analyse fonctionnelle détaillée module par module.
    4. Conception de la base de données (MCD, MPD).
    5. Conception de l'architecture technique (DAT).
    6. Maquettage UX/UI des interfaces critiques (pointage, tableau de bord, gestion congés).
    7. Rédaction des cas de test à partir des règles métier et des processus documentés.