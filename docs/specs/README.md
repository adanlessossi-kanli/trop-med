# Trop-Med — Spécifications techniques

> Plateforme de médecine tropicale alimentée par l'IA pour le suivi des patients, la surveillance épidémiologique et l'aide à la décision clinique.

## Documents

| # | Document | Description |
|---|---|---|
| 01 | [Vue d'ensemble](01-overview.md) | Objectif, capacités, utilisateurs, stack technique, contraintes |
| 02 | [Architecture](02-architecture.md) | Architecture système, modèle de données, stratégie hors ligne, structure des répertoires |
| 03 | [API](03-api.md) | Endpoints REST, protocole WebSocket, matrice RBAC, gestion des erreurs |
| 04 | [Infrastructure](04-infrastructure.md) | Services AWS, modules Terraform, configuration Docker/LocalStack, CI/CD |
| 05 | [Conformité et sécurité](05-compliance-security.md) | HIPAA, RGPD, sécurité IA, journalisation d'audit, réponse aux incidents |
| 06 | [Fonctionnalités](06-features.md) | Spécifications détaillées des fonctionnalités avec user stories et critères d'acceptation |

## Référence rapide

- **Stack** : Next.js + FastAPI + MongoDB Atlas + MedicalQwen3-14B
- **Infra** : AWS (Terraform) — ECS Fargate, EC2 GPU, S3, SQS/SNS, CloudFront
- **Dev local** : Docker Compose + LocalStack
- **Conformité** : HIPAA + RGPD
- **Langues** : Français, Anglais
- **Plateformes** : Web + Mobile (React Native)
