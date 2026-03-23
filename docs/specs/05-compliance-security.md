# Trop-Med — Spécification de conformité et sécurité

## 1. Conformité HIPAA

### 1.1 Mesures techniques

| Exigence | Implémentation |
|---|---|
| Contrôle d'accès | RBAC avec JWT, MFA pour les cliniciens et administrateurs |
| Contrôles d'audit | Tous les accès aux données de santé journalisés dans la collection `audit_logs` |
| Contrôles d'intégrité | Versionnement des documents MongoDB, versionnement des objets S3 |
| Sécurité de transmission | TLS 1.3 sur toutes les connexions |
| Chiffrement au repos | Chiffrement MongoDB Atlas, S3 SSE-KMS, chiffrement EBS |
| Déconnexion automatique | Expiration JWT (15 min accès, 7 jours rafraîchissement), délai d'inactivité |

### 1.2 Mesures administratives

| Exigence | Implémentation |
|---|---|
| Identifiants utilisateur uniques | Comptes basés sur l'email, pas d'identifiants partagés |
| Accès d'urgence | Procédure de bris de glace administrateur avec journalisation d'audit renforcée |
| Gestion des sessions | Sessions sauvegardées dans Redis, capacité de déconnexion forcée |

### 1.3 Traitement des données de santé (PHI)

- Champs PHI chiffrés au niveau du champ via MongoDB CSFLE
- Champs PHI : `name`, `date_of_birth`, `address`, `phone`, `email`, `national_id`, `medical_record_number`
- Pipeline de dé-identification pour l'accès chercheur (méthode Safe Harbor)
- Aucune donnée PHI dans les logs applicatifs — uniquement les références `patient_id`

## 2. Conformité RGPD

### 2.1 Droits des personnes concernées

| Droit | Implémentation |
|---|---|
| Droit d'accès | `/api/v1/patients/{id}/export` — export complet des données (JSON/PDF) |
| Droit de rectification | Endpoints PUT standards pour la correction des données |
| Droit à l'effacement | Suppression logique + suppression définitive programmée après la période de rétention |
| Droit à la portabilité | Format d'export FHIR R4 |
| Droit à la limitation du traitement | Indicateurs de traitement par patient |

### 2.2 Gestion du consentement

```json
{
  "patient_id": "string",
  "consents": [
    {
      "type": "data_processing",
      "granted": true,
      "timestamp": "ISO8601",
      "version": "1.0"
    },
    {
      "type": "ai_analysis",
      "granted": true,
      "timestamp": "ISO8601",
      "version": "1.0"
    },
    {
      "type": "research_use",
      "granted": false,
      "timestamp": "ISO8601",
      "version": "1.0"
    }
  ]
}
```

- Consentement enregistré avant tout traitement de données
- Consentement granulaire par finalité de traitement
- Le retrait du consentement arrête immédiatement le traitement concerné
- Piste d'audit du consentement maintenue

### 2.3 Rétention des données

| Type de données | Rétention | Après expiration |
|---|---|---|
| Dossiers cliniques | 10 ans (minimum réglementaire) | Archivage puis purge |
| Journaux d'audit | 7 ans | Archivage vers S3 Glacier |
| Conversations chat | 2 ans | Suppression définitive |
| Fichiers uploadés | Liés à la rétention du dossier clinique | Suppression définitive de S3 |
| Comptes utilisateurs | Jusqu'à demande de suppression + 30 jours de grâce | Suppression définitive |

## 3. Sécurité spécifique à l'IA

| Mesure | Description |
|---|---|
| Avertissement | Chaque réponse IA inclut un avertissement de vérification par un clinicien |
| Score de confiance | Les réponses en dessous de 0.6 de confiance sont signalées avec un avertissement explicite |
| Pas de décisions autonomes | L'IA suggère, le clinicien décide — aucune action clinique automatisée |
| Défense contre l'injection de prompts | Assainissement des entrées, isolation du prompt système |
| Surveillance des biais | Audits réguliers des résultats de l'IA selon les données démographiques |
| Piste d'audit | Toutes les requêtes et réponses IA journalisées avec le contexte utilisateur |

## 4. Schéma du journal d'audit

```json
{
  "timestamp": "ISO8601",
  "user_id": "string",
  "role": "string",
  "action": "READ|CREATE|UPDATE|DELETE|AI_QUERY|LOGIN|EXPORT",
  "resource_type": "patient|encounter|observation|file|ai",
  "resource_id": "string",
  "ip_address": "string",
  "user_agent": "string",
  "details": {},
  "phi_accessed": true
}
```

## 5. Réponse aux incidents

| Phase | Action |
|---|---|
| Détection | Détection d'anomalies CloudWatch, alertes d'échec d'authentification |
| Confinement | Verrouillage automatique du compte après 5 tentatives échouées |
| Notification | HIPAA : 60 jours. RGPD : 72 heures à l'autorité de contrôle |
| Récupération | Restauration depuis la sauvegarde MongoDB Atlas, rotation des secrets compromis |
| Post-mortem | Revue documentée, mise à jour des contrôles de sécurité |
