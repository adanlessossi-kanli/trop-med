# Trop-Med — Vue d'ensemble du projet

## 1. Objectif

Trop-Med est une plateforme de médecine tropicale alimentée par l'IA pour le suivi des patients, la surveillance épidémiologique et l'aide à la décision clinique. Elle est destinée aux professionnels de santé et aux patients dans des environnements multilingues (français/anglais) à faible connectivité — avec un focus principal sur le Togo et les contextes similaires.

## 2. Capacités principales

| Capacité | Description |
|---|---|
| Questions-réponses médicales | Réponses fondées sur des preuves avec indication du niveau d'incertitude |
| Aide à la décision clinique | Diagnostic différentiel, évaluation des traitements, application des protocoles |
| Revue de littérature scientifique | Synthèse d'articles médicaux, extraction des résultats clés |
| Communication patient | Concepts médicaux complexes traduits en langage accessible |
| Chatbot multilingue | Interface conversationnelle français/anglais pour patients et soignants |
| Suivi des patients | Enregistrement, historique des visites, plans de traitement, résultats |
| Surveillance épidémiologique | Tableaux de bord épidémiologiques, détection d'épidémies, analyse des tendances |

## 3. Utilisateurs et rôles

| Rôle | Niveau d'accès |
|---|---|
| Administrateur | Configuration complète du système, gestion des utilisateurs, journaux d'audit |
| Médecin | Fonctionnalités cliniques complètes, assistant IA, prescriptions |
| Infirmier(ère) | Accueil des patients, signes vitaux, triage, accès IA limité |
| Chercheur | Données anonymisées, revue de littérature, tableaux de bord de surveillance |
| Patient | Ses propres dossiers, chatbot, prise de rendez-vous, notifications |

## 4. Stack technique

| Couche | Technologie |
|---|---|
| Frontend | Next.js (React), TypeScript |
| Mobile | React Native (partage de code avec le web) |
| API Backend | Python (FastAPI) |
| IA/LLM | MedicalQwen3-Reasoning-14B sur EC2 GPU |
| Base de données | MongoDB Atlas |
| Standard DSE | HL7 FHIR R4 |
| Temps réel | WebSockets (chat en direct, notifications) |
| Stockage de fichiers | AWS S3 (résultats de laboratoire, imagerie, PDF, CSV) |
| Infrastructure | AWS, provisionnée via Terraform |
| Développement local | Docker Compose + LocalStack |
| Langues | Français, Anglais |

## 5. Conformité

- HIPAA (chiffrement des données de santé au repos et en transit, pistes d'audit, BAA avec les fournisseurs)
- RGPD (gestion du consentement, portabilité des données, droit à l'effacement)

## 6. Flux de travail — Comment utiliser

1. **Accéder à la plateforme** — Se connecter via l'application web ou mobile avec les identifiants attribués selon votre rôle.
2. **Sélectionner le mode de fonctionnement** — Choisir entre le *mode réflexion* pour les tâches de raisonnement médical complexe (diagnostic différentiel avec chaîne de raisonnement, synthèse de recherche) ou le *mode direct* pour les requêtes cliniques rapides (références médicamenteuses, consultation de protocoles).
3. **Saisir votre requête médicale** — Formuler clairement votre question ou tâche en fournissant le contexte pertinent : symptômes du patient, antécédents médicaux ou paramètres de recherche.
4. **Examiner la réponse** — En mode réflexion, observer le processus de raisonnement étape par étape ; en mode direct, recevoir des réponses immédiates.
5. **Vérifier et appliquer** — Recouper les informations générées par l'IA avec les recommandations cliniques et le jugement professionnel avant toute application.
6. **Itérer si nécessaire** — Affiner vos requêtes en fonction des réponses initiales pour obtenir des informations médicales plus spécifiques ou détaillées.

### Bonnes pratiques

- Fournir un contexte complet incluant les données démographiques du patient, les symptômes et les antécédents médicaux pertinents
- Utiliser le mode réflexion pour le diagnostic différentiel, la planification thérapeutique et l'analyse de cas complexes
- Exploiter le mode direct pour les interactions médicamenteuses, les calculs de posologie ou la consultation de protocoles
- Toujours valider les recommandations de l'IA par rapport à la littérature médicale actuelle et aux protocoles institutionnels
- Préserver la confidentialité des patients en anonymisant toutes les données avant la saisie

### Considérations importantes

- **Confidentialité et sécurité des données** — S'assurer que toutes les données des patients sont correctement anonymisées avant traitement. Mettre en œuvre des protocoles de sécurité robustes incluant le chiffrement, les contrôles d'accès et la journalisation d'audit pour maintenir la conformité HIPAA et protéger les informations médicales sensibles.
- **Validation clinique** — Établir des protocoles clairs pour valider les recommandations générées par l'IA par rapport aux directives cliniques actuelles et aux normes institutionnelles. Les professionnels de santé doivent toujours appliquer leur jugement clinique et leur expertise lors de l'évaluation des résultats du modèle.
- **Formation des utilisateurs** — Fournir une formation complète au personnel de santé sur la formulation efficace des requêtes, l'interprétation des résultats du modèle et la compréhension de ses limites. Cela garantit une utilisation optimale tout en maintenant une supervision clinique appropriée.

### Limites et utilisation responsable

- Le modèle fournit des informations et des suggestions mais ne peut pas remplacer le jugement médical professionnel
- Les réponses doivent être vérifiées par rapport à la littérature médicale actuelle et aux protocoles institutionnels
- Le modèle peut ne pas avoir accès aux développements médicaux ou aux approbations de médicaments les plus récents
- Les cas complexes nécessitant une expérience clinique nuancée peuvent requérir une consultation d'expert supplémentaire
- Les variations culturelles et régionales des pratiques médicales peuvent ne pas être entièrement prises en compte dans l'entraînement du modèle

### Développements futurs et feuille de route

- Intégration avec des bases de données médicales en temps réel pour des informations à jour sur les médicaments et les directives cliniques
- Capacités multimodales améliorées intégrant l'imagerie médicale et l'interprétation des tests diagnostiques
- Personnalisation améliorée basée sur les protocoles institutionnels et les pratiques médicales régionales
- Fonctionnalités d'explicabilité avancées fournissant des chaînes de raisonnement transparentes pour les décisions cliniques
- Support linguistique élargi pour les communautés linguistiques mal desservies dans le domaine de la santé

## 7. Utilisation

### 7.1 Application web
- Accéder à l'URL de la plateforme et se connecter avec ses identifiants
- Les cliniciens accèdent à l'assistant IA, aux dossiers patients et aux outils cliniques depuis le tableau de bord
- Les patients accèdent au chatbot, à leurs propres dossiers et à la prise de rendez-vous
- Basculement de langue (français/anglais) disponible dans la barre de navigation supérieure

### 7.2 Application mobile
- Télécharger l'application React Native et se connecter avec les mêmes identifiants
- Mode hors ligne prioritaire : les résumés patients et les protocoles courants sont mis en cache localement
- Les données saisies hors ligne sont mises en file d'attente et synchronisées automatiquement à la reconnexion

### 7.3 Modes de l'assistant IA

| Mode | Cas d'utilisation | Comportement |
|---|---|---|
| Réflexion | Diagnostic différentiel, planification thérapeutique, analyse de cas complexes | Affiche les étapes de raisonnement avant la réponse finale |
| Direct | Interactions médicamenteuses, calculs de posologie, références de protocoles | Retourne des réponses concises immédiates |

### 7.4 Accès API
- Les systèmes tiers et les clients FHIR peuvent s'intégrer via l'API REST à `/api/v1/`
- Authentification via jetons JWT obtenus depuis `/api/v1/auth/login`
- Limites de débit par rôle (patients : 60/min, cliniciens : 300/min, administrateurs : 600/min)

## 8. Configuration

### 8.1 Variables d'environnement

| Variable | Description | Source |
|---|---|---|
| `MONGODB_URI` | Chaîne de connexion MongoDB | AWS Secrets Manager |
| `JWT_SECRET` | Clé de signature JWT | AWS Secrets Manager |
| `AWS_S3_BUCKET` | Nom du bucket de stockage de fichiers | Sortie Terraform |
| `AI_INFERENCE_URL` | Point de terminaison d'inférence GPU | Sortie Terraform |
| `REDIS_URL` | Point de terminaison ElastiCache pour sessions/cache | Sortie Terraform |
| `SQS_TASK_QUEUE_URL` | URL de la file d'attente des tâches asynchrones | Sortie Terraform |
| `SNS_NOTIFICATION_TOPIC` | ARN du sujet de notification | Sortie Terraform |
| `FHIR_BASE_URL` | Point de terminaison FHIR du DSE externe | Configuration manuelle |
| `APP_LOCALE` | Langue par défaut (`fr` ou `en`) | Configuration manuelle |

### 8.2 Configuration du modèle IA
- Modèle : MedicalQwen3-Reasoning-14B servi via vLLM ou TGI sur EC2 GPU (g5.2xlarge)
- Mode réflexion : activé par défaut pour les endpoints `/ai/differential` et `/ai/literature`
- Mode direct : activé par défaut pour les endpoints `/ai/query` et `/ai/translate`
- Seuil de confiance : les réponses en dessous de 0.6 déclenchent des avertissements d'incertitude explicites
- Nombre maximal de tokens, température et autres paramètres d'inférence configurables par endpoint

### 8.3 Localisation
- Langue par défaut définie via la variable d'environnement `APP_LOCALE`
- Internationalisation du frontend gérée via `next-intl` avec les fichiers de traduction dans `frontend/src/lib/i18n/`
- Réponses IA générées dans la langue spécifiée dans la requête (`locale: "fr|en"`)

### 8.4 Canaux de notification
- In-app : livraison en temps réel via WebSocket
- Push : AWS SNS → FCM (Android) / APNs (iOS)
- Email/SMS : abonnements aux sujets SNS, configurables par utilisateur dans les préférences de notification

## 9. Déploiement

### 9.1 Développement local

```bash
# Démarrer tous les services (backend, frontend, MongoDB, Redis, LocalStack, mock IA)
docker compose up -d

# Backend avec rechargement automatique
docker compose up backend --build

# Serveur de développement frontend
cd frontend && npm run dev

# Exécuter les tests
docker compose exec backend pytest

# Insérer des données d'exemple
docker compose exec backend python -m app.scripts.seed
```

LocalStack émule S3, SQS, SNS et Secrets Manager localement — aucun compte AWS nécessaire pour le développement.

### 9.2 Provisionnement de l'infrastructure (Terraform)

```bash
cd infra

# Initialiser Terraform
terraform init

# Planifier pour l'environnement cible
terraform plan -var-file=environments/dev.tfvars

# Appliquer
terraform apply -var-file=environments/dev.tfvars
```

Modules Terraform : `vpc`, `ecs`, `ec2-gpu`, `s3`, `elasticache`, `sqs-sns`, `cloudfront`, `secrets`, `monitoring`.

### 9.3 Pipeline CI/CD (GitHub Actions)

| Étape | Déclencheur | Actions |
|---|---|---|
| Lint et vérification de types | Tous les pushs | ESLint, mypy, Prettier |
| Tests unitaires | Tous les pushs | pytest, Jest |
| Tests d'intégration | Tous les pushs | Docker Compose + LocalStack |
| Analyse de sécurité | Tous les pushs | Trivy (conteneurs), Bandit (Python) |
| Build et push | À la fusion | Images Docker → Amazon ECR |
| Déploiement dev | Push sur `develop` | Déploiement automatique via ECS |
| Déploiement staging | Push sur `main` | Déploiement automatique via ECS |
| Déploiement prod | Approbation manuelle | Déploiement contrôlé via ECS |

### 9.4 Architecture de production

| Composant | Service AWS | Spécification |
|---|---|---|
| API Backend | ECS Fargate | 2 vCPU, 4 Go RAM, auto-scaling 2–10 tâches |
| Inférence IA | EC2 GPU | g5.2xlarge (A10G), sous-réseau privé, serveur vLLM |
| Frontend | S3 + CloudFront | Export statique avec CDN mondial |
| Base de données | MongoDB Atlas | M10+ dédié, peering VPC |
| Cache | ElastiCache Redis | Stockage de sessions, limitation de débit |
| Fichiers | S3 | Chiffrement SSE-KMS, versionnement |
| Messagerie | SQS + SNS | Tâches asynchrones, notifications push |
| Surveillance | CloudWatch + X-Ray | Logs, métriques, traçage, alarmes |
| Sécurité | WAF + Shield | Règles OWASP, protection DDoS |

## 10. Contraintes clés

- Doit fonctionner dans des environnements à faible connectivité / capable de fonctionner hors ligne
- Toutes les réponses IA doivent inclure des niveaux de confiance et des citations de sources
- Les données des patients doivent être chiffrées de bout en bout
- Le système doit supporter simultanément l'interface et les réponses IA en français et en anglais
