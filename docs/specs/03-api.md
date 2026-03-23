# Trop-Med — Spécification de l'API

## 1. Principes de conception de l'API

- RESTful avec charges utiles JSON
- Versionnée : `/api/v1/...`
- Conforme FHIR R4 pour les ressources cliniques
- Tous les endpoints nécessitent une authentification sauf `/auth/login`, `/auth/register`
- Limitation de débit par rôle (patients : 60/min, cliniciens : 300/min, administrateurs : 600/min)
- Toutes les réponses incluent un `request_id` pour le traçage

## 2. Authentification et autorisation

### Endpoints

| Méthode | Chemin | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Inscription d'un utilisateur |
| POST | `/api/v1/auth/login` | Connexion, retourne les jetons JWT (accès + rafraîchissement) |
| POST | `/api/v1/auth/refresh` | Rafraîchir le jeton d'accès |
| POST | `/api/v1/auth/logout` | Invalider la session |
| POST | `/api/v1/auth/mfa/setup` | Activer l'authentification multifacteur |
| POST | `/api/v1/auth/mfa/verify` | Vérifier le code MFA |

### Charge utile JWT
```json
{
  "sub": "user_id",
  "role": "doctor|nurse|researcher|patient|admin",
  "locale": "fr|en",
  "exp": 1234567890
}
```

### Matrice RBAC

| Ressource | Admin | Médecin | Infirmier(ère) | Chercheur | Patient |
|---|---|---|---|---|---|
| Utilisateurs (gestion) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Patients (tous) | ✅ | ✅ | ✅ (lecture) | ✅ (anon.) | Les siens uniquement |
| Données cliniques | ✅ | ✅ | ✅ (limité) | ✅ (anon.) | Les siennes uniquement |
| Assistant IA | ✅ | ✅ | ✅ (triage) | ✅ | ✅ (chatbot) |
| Surveillance | ✅ | ✅ (lecture) | ❌ | ✅ | ❌ |
| Journaux d'audit | ✅ | ❌ | ❌ | ❌ | ❌ |
| Fichiers (upload) | ✅ | ✅ | ✅ | ❌ | ✅ (les siens) |

## 3. Gestion des patients

| Méthode | Chemin | Description |
|---|---|---|
| GET | `/api/v1/patients` | Lister les patients (paginé, recherchable) |
| POST | `/api/v1/patients` | Créer un dossier patient |
| GET | `/api/v1/patients/{id}` | Obtenir un patient par ID |
| PUT | `/api/v1/patients/{id}` | Mettre à jour un patient |
| DELETE | `/api/v1/patients/{id}` | Suppression logique d'un patient |
| GET | `/api/v1/patients/{id}/timeline` | Chronologie clinique complète |

### Paramètres de requête (GET liste)
- `q` — Recherche plein texte (nom, ID)
- `page`, `limit` — Pagination (par défaut : page=1, limit=20)
- `sort` — Champ de tri
- `status` — active, inactive

## 4. Ressources cliniques (FHIR R4)

| Méthode | Chemin | Ressource FHIR |
|---|---|---|
| GET/POST | `/api/v1/fhir/Encounter` | Encounter (consultation) |
| GET/POST | `/api/v1/fhir/Observation` | Observation (signes vitaux, laboratoire) |
| GET/POST | `/api/v1/fhir/Condition` | Condition (diagnostics) |
| GET/POST | `/api/v1/fhir/MedicationRequest` | MedicationRequest (prescriptions) |
| GET/POST | `/api/v1/fhir/DiagnosticReport` | DiagnosticReport (rapports diagnostiques) |
| GET | `/api/v1/fhir/{resource}/{id}` | Obtenir une ressource FHIR par ID |
| PUT | `/api/v1/fhir/{resource}/{id}` | Mettre à jour une ressource FHIR |

Tous les endpoints FHIR acceptent et retournent du JSON FHIR R4.

## 5. IA / LLM

| Méthode | Chemin | Description |
|---|---|---|
| POST | `/api/v1/ai/query` | Questions-réponses médicales |
| POST | `/api/v1/ai/differential` | Diagnostic différentiel à partir des symptômes |
| POST | `/api/v1/ai/literature` | Synthèse d'articles de recherche |
| POST | `/api/v1/ai/translate` | Simplification de texte médical pour les patients |

### Requête : `/api/v1/ai/query`
```json
{
  "question": "string",
  "context": { "patient_id": "optionnel", "locale": "fr|en" },
  "max_tokens": 1024
}
```

### Réponse
```json
{
  "answer": "string",
  "confidence": 0.87,
  "sources": ["source1", "source2"],
  "disclaimer": "Ceci est généré par l'IA et doit être vérifié par un clinicien.",
  "locale": "fr"
}
```

## 6. Chat (WebSocket)

### Connexion
```
wss://api.tropmed.example/ws/chat?token={jwt}
```

### Types de messages

**Client → Serveur :**
```json
{ "type": "message", "content": "string", "locale": "fr|en" }
{ "type": "typing", "status": true }
```

**Serveur → Client :**
```json
{ "type": "ai_response", "content": "string", "confidence": 0.9, "sources": [] }
{ "type": "notification", "title": "string", "body": "string" }
{ "type": "typing", "status": true }
```

## 7. Fichiers

| Méthode | Chemin | Description |
|---|---|---|
| POST | `/api/v1/files/upload` | Upload de fichier (multipart, max 50 Mo) |
| GET | `/api/v1/files/{id}` | Obtenir les métadonnées d'un fichier |
| GET | `/api/v1/files/{id}/download` | Télécharger un fichier (URL S3 présignée) |
| GET | `/api/v1/patients/{id}/files` | Lister les fichiers d'un patient |
| DELETE | `/api/v1/files/{id}` | Suppression logique d'un fichier |

### Types supportés
- `application/pdf` — Rapports de laboratoire, documents
- `image/png`, `image/jpeg`, `image/dicom` — Imagerie médicale
- `text/csv` — Imports de données

## 8. Surveillance

| Méthode | Chemin | Description |
|---|---|---|
| GET | `/api/v1/surveillance/dashboard` | Métriques épidémiologiques agrégées |
| GET | `/api/v1/surveillance/trends` | Données de tendances des maladies |
| GET | `/api/v1/surveillance/alerts` | Alertes d'épidémie actives |
| POST | `/api/v1/surveillance/report` | Soumettre un rapport de surveillance |

### Paramètres de requête
- `region` — Filtre géographique
- `disease_code` — Filtre par code CIM-10
- `date_from`, `date_to` — Plage de dates
- `granularity` — jour, semaine, mois

## 9. Notifications

| Méthode | Chemin | Description |
|---|---|---|
| GET | `/api/v1/notifications` | Lister les notifications de l'utilisateur |
| PUT | `/api/v1/notifications/{id}/read` | Marquer comme lue |
| PUT | `/api/v1/notifications/read-all` | Marquer toutes comme lues |

## 10. Format de réponse d'erreur

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Message lisible par un humain",
    "details": [],
    "request_id": "uuid"
  }
}
```

| Code HTTP | Code | Utilisation |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Entrée invalide |
| 401 | `UNAUTHORIZED` | Jeton manquant/invalide |
| 403 | `FORBIDDEN` | Rôle insuffisant |
| 404 | `NOT_FOUND` | Ressource introuvable |
| 429 | `RATE_LIMITED` | Trop de requêtes |
| 500 | `INTERNAL_ERROR` | Erreur serveur |
