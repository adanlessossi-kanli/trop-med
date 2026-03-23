# Trop-Med — Spécification d'architecture

## 1. Architecture de haut niveau

```
┌─────────────────────────────────────────────────────────┐
│                       Clients                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Web Next.js  │  │ React Native │  │ Client FHIR  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼─────────────────┼─────────────────┼───────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────┐
│                   Cloud AWS (Terraform)                  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │              ALB / API Gateway                     │  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────▼───────────────────────────┐  │
│  │           Backend FastAPI (ECS Fargate)            │  │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────────────┐  │  │
│  │  │ Service  │ │ Passerelle│ │ Services          │  │  │
│  │  │ Auth     │ │ FHIR     │ │ Patient/Clinique  │  │  │
│  │  └──────────┘ └──────────┘ └───────────────────┘  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────────────┐  │  │
│  │  │ Service  │ │ Service  │ │ Service           │  │  │
│  │  │ Chat/WS  │ │ Fichiers │ │ Surveillance      │  │  │
│  │  └──────────┘ └──────────┘ └───────────────────┘  │  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │                              │
│  ┌───────────┐  ┌────────▼────────┐  ┌──────────────┐  │
│  │ MongoDB   │  │ Inférence IA    │  │ S3           │  │
│  │ Atlas     │  │ EC2 GPU         │  │ (Fichiers)   │  │
│  │ (Données) │  │ (Qwen3-14B)    │  │              │  │
│  └───────────┘  └─────────────────┘  └──────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  SQS (tâches async)  │  SNS (notifications)      │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 2. Architecture frontend

### 2.1 Application web Next.js
- App Router avec composants serveur lorsque possible
- Internationalisation via `next-intl` (français/anglais)
- Service Worker pour la mise en cache hors ligne (données patients critiques)
- IndexedDB pour la file d'attente de données hors ligne (synchronisation à la reconnexion)
- Client WebSocket pour le chat en direct et les notifications push

### 2.2 Application mobile React Native
- Logique métier et couche API partagées avec le web via des packages communs
- Mode hors ligne prioritaire avec SQLite local + synchronisation en arrière-plan
- Notifications push via AWS SNS → FCM/APNs

## 3. Architecture backend

### 3.1 Application FastAPI
- Structure modulaire par services (voir l'arborescence ci-dessous)
- Endpoints asynchrones avec `asyncio` pour les opérations d'E/S
- Traitement des tâches en arrière-plan via des consommateurs SQS
- Modèles de ressources FHIR R4 utilisant la bibliothèque `fhir.resources`

### 3.2 Modules de services

| Module | Responsabilité |
|---|---|
| `auth` | Authentification JWT, RBAC, gestion des sessions, MFA |
| `patients` | CRUD, recherche, mapping vers la ressource FHIR Patient |
| `clinical` | Consultations, observations, conditions, médicaments |
| `ai` | Proxy d'inférence LLM, gestion des prompts, formatage des réponses |
| `chat` | Gestionnaire WebSocket, historique des conversations, routage multilingue |
| `files` | Upload/download S3, analyse antivirus, extraction de métadonnées |
| `surveillance` | Pipelines d'agrégation, alertes d'épidémie, tableaux de bord |
| `fhir` | Passerelle FHIR R4, validation des ressources, interopérabilité DSE |
| `notifications` | Intégration SNS, notifications in-app, email/SMS |

### 3.3 Couche d'inférence IA
- MedicalQwen3-Reasoning-14B hébergé sur une instance EC2 GPU (g5.2xlarge+)
- vLLM ou TGI comme serveur d'inférence pour les requêtes par lots
- API interne dédiée (non exposée publiquement)
- File d'attente des requêtes pour gérer l'utilisation du GPU
- La réponse inclut : réponse, score de confiance, références des sources

## 4. Architecture des données

### 4.1 Collections MongoDB Atlas

| Collection | Objectif | Index clés |
|---|---|---|
| `users` | Comptes et profils utilisateurs | `email`, `role` |
| `patients` | Données démographiques des patients (mappées FHIR) | `fhir_id`, `name_text` |
| `encounters` | Visites cliniques | `patient_id`, `date` |
| `observations` | Signes vitaux, résultats de laboratoire | `patient_id`, `code`, `date` |
| `conditions` | Diagnostics | `patient_id`, `code` |
| `medications` | Prescriptions | `patient_id`, `status` |
| `conversations` | Historique des chats | `user_id`, `created_at` |
| `files` | Métadonnées des fichiers (données dans S3) | `patient_id`, `type` |
| `audit_logs` | Tous les événements d'accès aux données | `user_id`, `timestamp` |
| `surveillance` | Données épidémiologiques agrégées | `region`, `disease_code`, `date` |

### 4.2 Chiffrement des données
- Au repos : chiffrement MongoDB Atlas + S3 SSE-KMS
- En transit : TLS 1.3 partout
- Chiffrement au niveau des champs pour les données PII/PHI via MongoDB CSFLE

## 5. Stratégie hors ligne

```
┌──────────────┐    En ligne     ┌──────────────┐
│  Cache local  │ ◄────────────► │  API Cloud    │
│  (IndexedDB/  │                │  (FastAPI)    │
│   SQLite)     │                └──────────────┘
└──────┬───────┘
       │ Hors ligne
       ▼
┌──────────────┐
│  File de sync │  ← Met en file les mutations, les rejoue à la reconnexion
└──────────────┘
```

- Données de lecture critiques (résumés patients, protocoles) mises en cache localement
- Mutations mises en file d'attente avec horodatage, résolution de conflits à la synchronisation (dernière écriture gagne avec revue manuelle pour les données cliniques)
- Le Service Worker intercepte les appels API et sert le cache en mode hors ligne

## 6. Structure des répertoires

```
trop-med/
├── docs/specs/                  # Ces spécifications
├── frontend/                    # Application web Next.js
│   ├── src/
│   │   ├── app/                 # Pages App Router
│   │   ├── components/          # Composants UI partagés
│   │   ├── lib/                 # Client API, utilitaires, i18n
│   │   ├── hooks/               # Hooks React personnalisés
│   │   └── stores/              # Gestion d'état
│   ├── public/
│   └── package.json
├── mobile/                      # Application React Native
│   ├── src/
│   └── package.json
├── backend/                     # Backend FastAPI
│   ├── app/
│   │   ├── api/                 # Gestionnaires de routes
│   │   ├── models/              # Modèles de documents MongoDB
│   │   ├── services/            # Logique métier
│   │   ├── fhir/                # Mappings de ressources FHIR
│   │   ├── ai/                  # Intégration LLM
│   │   ├── core/                # Config, sécurité, dépendances
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── infra/                       # IaC Terraform
│   ├── modules/
│   └── environments/
├── docker/                      # Configurations Docker
│   ├── docker-compose.yml       # Stack de développement local
│   ├── docker-compose.local.yml # Surcharges LocalStack
│   └── Dockerfiles
└── shared/                      # Types/constantes partagés
```
