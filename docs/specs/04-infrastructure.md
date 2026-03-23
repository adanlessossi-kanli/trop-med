# Trop-Med — Spécification d'infrastructure et DevOps

## 1. Infrastructure AWS (Terraform)

### 1.1 Calcul

| Composant | Service | Spécification |
|---|---|---|
| API Backend | ECS Fargate | 2 vCPU, 4 Go RAM, auto-scaling 2–10 tâches |
| Inférence IA | EC2 GPU | g5.2xlarge (1x A10G, 8 vCPU, 32 Go), serveur vLLM |
| Frontend | S3 + CloudFront | Export statique ou Amplify Hosting |

### 1.2 Réseau

| Composant | Configuration |
|---|---|
| VPC | 2 zones de disponibilité, sous-réseaux publics + privés |
| ALB | Terminaison HTTPS, routage basé sur le chemin |
| Groupes de sécurité | Backend : entrée ALB uniquement. GPU : entrée backend uniquement |
| Passerelle NAT | Pour le trafic sortant du sous-réseau privé (MongoDB Atlas, etc.) |

### 1.3 Stockage et données

| Composant | Service |
|---|---|
| Base de données | MongoDB Atlas (M10+ dédié, peering VPC) |
| Stockage de fichiers | S3 (SSE-KMS, versionnement, politiques de cycle de vie) |
| Secrets | AWS Secrets Manager |
| Cache | ElastiCache Redis (stockage de sessions, limitation de débit) |

### 1.4 Messagerie et événements

| Composant | Service | Objectif |
|---|---|---|
| File de tâches | SQS | Tâches asynchrones (traitement de fichiers, lots IA) |
| Notifications | SNS | Notifications push, email, SMS |
| Événements | EventBridge | Alertes de surveillance, événements d'audit |

### 1.5 Surveillance et journalisation

| Composant | Service |
|---|---|
| Logs | CloudWatch Logs (JSON structuré) |
| Métriques | CloudWatch Metrics + tableaux de bord personnalisés |
| Traçage | AWS X-Ray |
| Alertes | CloudWatch Alarms → SNS |

## 2. Structure des modules Terraform

```
infra/
├── main.tf
├── variables.tf
├── outputs.tf
├── environments/
│   ├── dev.tfvars
│   ├── staging.tfvars
│   └── prod.tfvars
└── modules/
    ├── vpc/
    ├── ecs/
    ├── ec2-gpu/
    ├── s3/
    ├── elasticache/
    ├── sqs-sns/
    ├── cloudfront/
    ├── secrets/
    └── monitoring/
```

## 3. Développement local (Docker + LocalStack)

### 3.1 docker-compose.yml

| Service | Image | Objectif |
|---|---|---|
| `backend` | Personnalisée (Dockerfile) | Application FastAPI |
| `frontend` | Personnalisée (Dockerfile) | Serveur de développement Next.js |
| `mongodb` | `mongo:7` | MongoDB local |
| `redis` | `redis:7-alpine` | Cache/sessions |
| `localstack` | `localstack/localstack` | S3, SQS, SNS, Secrets Manager |
| `ai-mock` | Personnalisée | Réponses LLM simulées pour le développement (pas de GPU nécessaire) |

### 3.2 Services LocalStack

```
SERVICES=s3,sqs,sns,secretsmanager
```

- Bucket S3 : `tropmed-files-local`
- Files SQS : `tropmed-tasks-local`, `tropmed-notifications-local`
- Secrets : `tropmed/db-uri`, `tropmed/jwt-secret`

### 3.3 Flux de développement

```bash
# Démarrer tous les services
docker compose up -d

# Backend avec rechargement automatique
docker compose up backend --build

# Serveur de développement frontend
cd frontend && npm run dev

# Exécuter les tests backend
docker compose exec backend pytest

# Insérer des données d'exemple
docker compose exec backend python -m app.scripts.seed
```

## 4. Pipeline CI/CD

```
Push → GitHub Actions
  ├── Lint et vérification de types (frontend + backend)
  ├── Tests unitaires
  ├── Tests d'intégration (docker compose + LocalStack)
  ├── Analyse de sécurité (Trivy, Bandit)
  ├── Build des images Docker → ECR
  └── Déploiement
      ├── dev     → automatique sur push vers `develop`
      ├── staging → automatique sur push vers `main`
      └── prod    → porte d'approbation manuelle
```

## 5. Renforcement de la sécurité

| Mesure | Implémentation |
|---|---|
| WAF | AWS WAF sur ALB (règles OWASP) |
| DDoS | AWS Shield Standard |
| Rotation des secrets | Rotation automatique Secrets Manager (30 jours) |
| Analyse des conteneurs | Analyse des images ECR au push |
| Isolation réseau | Instance GPU dans un sous-réseau privé, pas d'IP publique |
| Piste d'audit | Tous les appels API journalisés avec ID utilisateur, IP, action |
| Sauvegarde des données | Sauvegardes automatiques MongoDB Atlas (quotidiennes, rétention 7 jours) |
| TLS | TLS 1.3 imposé sur tous les endpoints |

## 6. Variables d'environnement

| Variable | Description | Source |
|---|---|---|
| `MONGODB_URI` | Chaîne de connexion MongoDB | Secrets Manager |
| `JWT_SECRET` | Clé de signature JWT | Secrets Manager |
| `AWS_S3_BUCKET` | Bucket de stockage de fichiers | Sortie Terraform |
| `AI_INFERENCE_URL` | Endpoint d'inférence de l'instance GPU | Sortie Terraform |
| `REDIS_URL` | Endpoint ElastiCache | Sortie Terraform |
| `SQS_TASK_QUEUE_URL` | File de tâches asynchrones | Sortie Terraform |
| `SNS_NOTIFICATION_TOPIC` | ARN du sujet de notification | Sortie Terraform |
| `FHIR_BASE_URL` | Endpoint FHIR du DSE externe | Configuration |
| `APP_LOCALE` | Langue par défaut (fr/en) | Configuration |
