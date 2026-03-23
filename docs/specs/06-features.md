# Trop-Med — Spécifications des fonctionnalités

## 1. Questions-réponses médicales

### User Story
En tant que **médecin/infirmier(ère)**, je veux poser des questions cliniques en français ou en anglais et recevoir des réponses fondées sur des preuves avec des niveaux de confiance et des citations de sources.

### Critères d'acceptation
- [ ] Saisie en texte libre avec possibilité de joindre le contexte patient
- [ ] La réponse inclut : réponse, score de confiance (0–1), références des sources, avertissement
- [ ] Les réponses en dessous de 0.6 de confiance affichent un avertissement d'incertitude explicite
- [ ] Supporte le français et l'anglais en entrée/sortie
- [ ] Temps de réponse < 10 secondes pour les requêtes standards
- [ ] Requête et réponse journalisées dans la piste d'audit

### Interface
- Interface de type chat dans le tableau de bord clinicien
- Panneau de citations des sources dépliable
- Copier dans le presse-papiers pour les réponses
- Historique des requêtes passées (recherchable)

---

## 2. Aide à la décision clinique

### User Story
En tant que **médecin**, je veux saisir les symptômes d'un patient et recevoir un diagnostic différentiel classé avec les prochaines étapes suggérées.

### Critères d'acceptation
- [ ] Entrée : symptômes, signes vitaux, données démographiques du patient, antécédents pertinents
- [ ] Sortie : diagnostics différentiels classés avec estimations de probabilité
- [ ] Chaque diagnostic renvoie vers les investigations et options de traitement suggérées
- [ ] Peut être rattaché à un dossier de consultation patient
- [ ] Le clinicien doit explicitement accepter/rejeter les suggestions (pas d'application automatique)

---

## 3. Revue de littérature scientifique

### User Story
En tant que **chercheur**, je veux soumettre un sujet médical et recevoir un résumé synthétisé des résultats de recherche pertinents.

### Critères d'acceptation
- [ ] Entrée : requête thématique ou PDF(s) uploadé(s)
- [ ] Sortie : résumé structuré (résultats clés, notes méthodologiques, implications cliniques)
- [ ] Supporte le traitement par lots de plusieurs articles
- [ ] Résultats exportables en PDF
- [ ] Accessible uniquement aux rôles chercheur et médecin

---

## 4. Communication patient

### User Story
En tant que **patient**, je veux comprendre mon diagnostic et mon plan de traitement dans un langage simple (français ou anglais).

### Critères d'acceptation
- [ ] Le médecin déclenche « simplifier pour le patient » sur toute note clinique
- [ ] La sortie utilise un langage simple au niveau de lecture ~6e année
- [ ] Maintient la précision médicale tout en supprimant le jargon
- [ ] Le patient reçoit la version simplifiée dans sa langue préférée
- [ ] La note clinique originale est préservée, la version simplifiée y est liée

---

## 5. Chatbot de santé multilingue

### User Story
En tant que **patient**, je veux discuter avec un assistant IA en français ou en anglais de mes préoccupations de santé, rendez-vous et médicaments.

### Critères d'acceptation
- [ ] Détection automatique de la langue dès le premier message
- [ ] Gère : triage des symptômes, questions sur les rendez-vous, rappels de médicaments, informations de santé générales
- [ ] Escalade vers un clinicien humain lorsque la confiance est faible ou une urgence est détectée
- [ ] Détection de mots-clés d'urgence (ex. « urgence », « emergency ») déclenche une alerte immédiate
- [ ] Historique des conversations persisté et accessible au clinicien assigné (avec consentement)
- [ ] Fonctionne hors ligne avec des réponses en cache pour les requêtes courantes

---

## 6. Suivi des patients

### User Story
En tant qu'**infirmier(ère)**, je veux enregistrer des patients, saisir les signes vitaux et suivre leur historique de visites.

### Critères d'acceptation
- [ ] Enregistrement du patient avec données démographiques (ressource FHIR Patient)
- [ ] Saisie des signes vitaux (température, tension artérielle, fréquence cardiaque, poids, taille)
- [ ] Chronologie des visites montrant toutes les consultations, observations, conditions
- [ ] Recherche de patients par nom, ID ou numéro de téléphone
- [ ] Enregistrement de patients hors ligne avec synchronisation à la reconnexion

---

## 7. Surveillance épidémiologique

### User Story
En tant que **chercheur/administrateur**, je veux visualiser des tableaux de bord épidémiologiques montrant les tendances des maladies et les alertes d'épidémie.

### Critères d'acceptation
- [ ] Tableau de bord avec : nombre de cas par maladie, carte thermique géographique, graphiques de tendances
- [ ] Plage de dates et filtres régionaux configurables
- [ ] Alertes d'épidémie automatiques lorsque le nombre de cas dépasse le seuil
- [ ] Données anonymisées (pas d'identification individuelle des patients)
- [ ] Export des données du tableau de bord en CSV

---

## 8. Gestion des fichiers

### User Story
En tant que **médecin**, je veux uploader et joindre des résultats de laboratoire, de l'imagerie et des documents aux dossiers patients.

### Critères d'acceptation
- [ ] Upload par glisser-déposer (PDF, PNG, JPEG, CSV, DICOM)
- [ ] Taille maximale de fichier : 50 Mo
- [ ] Fichiers liés au dossier patient et à une consultation spécifique
- [ ] Analyse antivirus à l'upload
- [ ] Téléchargement par URL présignée (durée limitée)
- [ ] Aperçu miniature pour les images

---

## 9. Notifications

### User Story
En tant qu'**utilisateur**, je veux recevoir des notifications en temps réel pour les événements pertinents.

### Types de notifications

| Événement | Destinataires | Canal |
|---|---|---|
| Nouveau résultat de laboratoire | Médecin, Patient | In-app, Push |
| Alerte d'épidémie | Administrateur, Chercheur | In-app, Email |
| Rappel de rendez-vous | Patient | Push, SMS |
| Escalade IA | Médecin | In-app, Push |
| Message chat | Destinataire | In-app, Push |

### Critères d'acceptation
- [ ] Temps réel via WebSocket lorsque en ligne
- [ ] Notification push via FCM/APNs lorsque hors ligne
- [ ] Préférences de notification configurables par utilisateur
- [ ] Marquer comme lu / marquer tout comme lu

---

## 10. Panneau d'administration

### User Story
En tant qu'**administrateur**, je veux gérer les utilisateurs, consulter les journaux d'audit et configurer les paramètres du système.

### Critères d'acceptation
- [ ] CRUD utilisateurs avec attribution de rôles
- [ ] Visualiseur de journaux d'audit avec filtres (utilisateur, action, plage de dates, ressource)
- [ ] Tableau de bord de santé du système (latence API, utilisation GPU, taux d'erreurs)
- [ ] Feature flags pour le déploiement progressif
- [ ] Vue d'ensemble de la gestion du consentement
