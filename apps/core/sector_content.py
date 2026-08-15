"""Contenu des pages sectorielles publiques (référencement) — un secteur par
entrée, affiché par apps.core.views.SectorLandingView. Les affirmations sont
volontairement limitées aux fonctionnalités réellement disponibles (géofencing
par site, horaires flexibles, congés/absences, exports, journal d'audit)."""

SECTORS = {
    "entreprises": {
        "name": "Entreprises",
        "h1": "Le pointage géolocalisé pour vos équipes multi-sites",
        "meta_title": "Pointage géolocalisé pour entreprises multi-sites — GeoPresence",
        "meta_description": "GeoPresence vérifie la présence de vos équipes sur chaque site, calcule automatiquement retards et heures supplémentaires, et centralise congés et absences.",
        "intro": "Bureaux, agences commerciales, chantiers ou entrepôts : dès qu'une entreprise a plus d'un site, le pointage papier ou la déclaration sur l'honneur ne suffit plus. GeoPresence vérifie la position réelle de chaque collaborateur au moment du pointage et calcule automatiquement retards, départs anticipés et heures supplémentaires.",
        "points": [
            {"icon": "pin", "title": "Une zone GPS par site", "text": "Chaque agence définit son propre rayon autorisé (50 à 5000 m). Un pointage hors zone est refusé et journalisé."},
            {"icon": "calendar", "title": "Des horaires qui collent au terrain", "text": "Horaires fixes, en rotation ou par créneau, avec gestion automatique des équipes à cheval sur minuit."},
            {"icon": "shield", "title": "Une traçabilité opposable", "text": "Chaque pointage et chaque validation de congé est consigné dans un journal d'audit non modifiable."},
        ],
    },
    "ecoles": {
        "name": "Établissements scolaires",
        "h1": "Le pointage géolocalisé pour le personnel de vos établissements",
        "meta_title": "Pointage géolocalisé pour écoles et établissements scolaires — GeoPresence",
        "meta_description": "Suivez la présence du personnel enseignant et administratif sur chaque site, gérez les absences et les remplacements, avec une zone GPS propre à chaque établissement.",
        "intro": "Un établissement, plusieurs bâtiments, parfois plusieurs sites : GeoPresence permet à la direction de vérifier que le personnel enseignant et administratif est bien présent à l'heure prévue, et de traiter les demandes de congé ou d'absence sans tableur ni fiche papier.",
        "points": [
            {"icon": "building", "title": "Un site par établissement", "text": "Chaque bâtiment ou campus a sa propre zone GPS autorisée, gérée depuis un seul tableau de bord."},
            {"icon": "clipboard", "title": "Absences et remplacements suivis", "text": "Motifs, validation par la direction, historique consultable et exportable à tout moment."},
            {"icon": "shield", "title": "Données isolées par établissement", "text": "Les données de votre établissement restent strictement isolées de celles des autres organisations."},
        ],
    },
    "universites": {
        "name": "Universités",
        "h1": "Le pointage géolocalisé pour le personnel de vos facultés et campus",
        "meta_title": "Pointage géolocalisé pour universités et campus — GeoPresence",
        "meta_description": "GeoPresence suit la présence du personnel administratif et technique sur chacun de vos campus, avec des horaires par service et des congés centralisés.",
        "intro": "Facultés, laboratoires, bibliothèques, services administratifs : une université fonctionne souvent comme plusieurs organisations en une. GeoPresence gère les horaires et la présence du personnel service par service, avec une vue d'ensemble depuis un seul tableau de bord.",
        "points": [
            {"icon": "building", "title": "Plusieurs campus, un seul outil", "text": "Chaque site ou faculté a sa propre zone GPS autorisée et ses propres horaires."},
            {"icon": "calendar", "title": "Des horaires par service", "text": "Horaires fixes, en rotation ou par créneau, adaptés à chaque équipe."},
            {"icon": "clipboard", "title": "Congés et absences centralisés", "text": "Demandes, validations et soldes gérés de bout en bout, pour tout le personnel."},
        ],
    },
    "restaurants": {
        "name": "Restaurants",
        "h1": "Le pointage géolocalisé pour vos équipes en salle et en cuisine",
        "meta_title": "Pointage géolocalisé pour restaurants — GeoPresence",
        "meta_description": "Fini les feuilles de pointage papier : GeoPresence vérifie la présence de vos équipes, gère les horaires en rotation et les services de nuit, et calcule les heures supplémentaires.",
        "intro": "Services fractionnés, horaires en rotation, équipes de nuit à cheval sur minuit : la restauration a des besoins d'horaires que les outils de pointage classiques gèrent mal. GeoPresence calcule automatiquement les heures supplémentaires, y compris sur ces horaires irréguliers.",
        "points": [
            {"icon": "clock", "title": "Équipes de nuit gérées nativement", "text": "Un service qui commence avant minuit et finit après est calculé correctement, sans bricolage."},
            {"icon": "pin", "title": "Impossible de pointer pour un collègue", "text": "La position GPS est vérifiée à chaque pointage, en direct sur une carte interactive."},
            {"icon": "building", "title": "Un ou plusieurs établissements", "text": "Chaîne ou restaurant indépendant : chaque adresse a sa propre zone GPS autorisée."},
        ],
    },
    "pharmacies": {
        "name": "Pharmacies",
        "h1": "Le pointage géolocalisé pour vos équipes en officine",
        "meta_title": "Pointage géolocalisé pour pharmacies — GeoPresence",
        "meta_description": "GeoPresence garantit une couverture continue de votre officine : présence vérifiée par GPS, horaires précis, et preuve de présence en cas de contrôle.",
        "intro": "Une pharmacie doit être couverte à chaque instant d'ouverture. GeoPresence vérifie que chaque membre de l'équipe pointe bien depuis l'officine, avec une zone GPS resserrée, et donne au titulaire une preuve fiable de présence.",
        "points": [
            {"icon": "pin", "title": "Une zone GPS resserrée", "text": "Le rayon autorisé se règle finement (à partir de 50 m) pour coller à la surface réelle de l'officine."},
            {"icon": "clock", "title": "Retards et heures sup automatiques", "text": "Aucune ressaisie manuelle : le statut de chaque pointage est calculé dès l'arrivée."},
            {"icon": "shield", "title": "Une preuve opposable", "text": "Journal d'audit en écriture seule, consultable en cas de contrôle ou de litige."},
        ],
    },
    "cliniques": {
        "name": "Cliniques & hôpitaux",
        "h1": "Le pointage géolocalisé pour le personnel soignant et administratif",
        "meta_title": "Pointage géolocalisé pour cliniques et hôpitaux — GeoPresence",
        "meta_description": "GeoPresence suit la présence du personnel sur chaque service ou site de soin, gère les rotations jour/nuit et les heures supplémentaires, avec un journal d'audit opposable.",
        "intro": "Rotations jour/nuit, doubles vacations, plusieurs sites de soins : le personnel hospitalier a des horaires exigeants à suivre précisément. GeoPresence calcule automatiquement les heures supplémentaires et conserve un journal d'audit non modifiable pour chaque pointage.",
        "points": [
            {"icon": "calendar", "title": "Rotations jour/nuit", "text": "Horaires en rotation gérés automatiquement, y compris les équipes de nuit à cheval sur minuit."},
            {"icon": "clock", "title": "Heures supplémentaires calculées", "text": "Le dépassement d'horaire est détecté et enregistré sans intervention manuelle."},
            {"icon": "shield", "title": "Un journal d'audit inaltérable", "text": "Chaque pointage est tracé, en écriture seule, sans exception."},
        ],
    },
    "ong": {
        "name": "ONG",
        "h1": "Le pointage géolocalisé pour vos équipes sur le terrain",
        "meta_title": "Pointage géolocalisé pour ONG et équipes terrain — GeoPresence",
        "meta_description": "GeoPresence permet aux ONG de vérifier la présence de leurs équipes sur chaque site ou mission, avec un historique exportable en CSV, Excel ou PDF pour vos bailleurs.",
        "intro": "Missions terrain, antennes locales, zones parfois reculées : les ONG doivent souvent prouver la présence effective de leurs équipes sur site, y compris pour leurs propres bailleurs de fonds. GeoPresence enregistre position GPS, horaire et statut de chaque pointage, exportables en CSV, Excel ou PDF.",
        "points": [
            {"icon": "pin", "title": "Une zone GPS par mission", "text": "Chaque site d'intervention a sa propre zone GPS autorisée, aussi ponctuelle soit-elle."},
            {"icon": "clipboard", "title": "Des exports prêts pour vos bailleurs", "text": "Historique des pointages, congés et absences exportable en CSV, Excel ou PDF."},
            {"icon": "shield", "title": "Isolation stricte des données", "text": "Les données de votre organisation restent strictement séparées de celles des autres."},
        ],
    },
    "administrations": {
        "name": "Administrations",
        "h1": "Le pointage géolocalisé pour vos services et guichets",
        "meta_title": "Pointage géolocalisé pour administrations — GeoPresence",
        "meta_description": "GeoPresence aide les administrations à vérifier la présence des agents sur chaque site ou guichet, avec un journal d'audit non modifiable, même par un administrateur.",
        "intro": "Plusieurs guichets, plusieurs services, parfois plusieurs communes : GeoPresence donne aux administrations un moyen fiable de vérifier la présence des agents sur chaque site, avec une traçabilité complète.",
        "points": [
            {"icon": "building", "title": "Un site par guichet ou service", "text": "Chaque site a sa propre zone GPS autorisée et ses propres horaires."},
            {"icon": "shield", "title": "Un audit non modifiable", "text": "Journal d'audit en écriture seule, non modifiable, même par un administrateur."},
            {"icon": "clipboard", "title": "Congés et absences centralisés", "text": "Demandes, validations et soldes gérés de bout en bout pour tous les agents."},
        ],
    },
    "associations": {
        "name": "Associations",
        "h1": "Le pointage géolocalisé pour vos équipes et antennes locales",
        "meta_title": "Pointage géolocalisé pour associations — GeoPresence",
        "meta_description": "GeoPresence permet aux associations de suivre la présence de leurs équipes sur chaque antenne ou lieu d'activité, avec une isolation stricte des données.",
        "intro": "Petite équipe ou plusieurs antennes locales, salariés ou permanents : GeoPresence reste simple à mettre en place tout en offrant les mêmes garanties de fiabilité, position GPS vérifiée et horaires respectés, que pour une grande organisation.",
        "points": [
            {"icon": "pin", "title": "Une zone GPS par antenne", "text": "Chaque lieu d'activité a sa propre zone GPS autorisée."},
            {"icon": "calendar", "title": "Des horaires flexibles", "text": "Fixes, en rotation ou par créneau, adaptés à la réalité de chaque équipe."},
            {"icon": "shield", "title": "Isolation stricte des données", "text": "Vos données restent strictement séparées de celles des autres organisations."},
        ],
    },
}
