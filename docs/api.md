# API Reference

!!! tip "Documentation interactive"
    La documentation Swagger est disponible sur **`http://localhost:8000/docs`** quand l'API tourne en local.  
    Elle permet de tester tous les endpoints directement depuis le navigateur.

---

## Authentification

L'API utilise **OAuth2 avec JWT Bearer Token**.

### `POST /token`

Obtenir un token d'accès.

**Public** — aucune authentification requise.

=== "Requête"

    ```bash
    curl -X POST "http://localhost:8000/token" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=admin&password=secret"
    ```

=== "Réponse 200"

    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
    ```

=== "Réponse 401"

    ```json
    {
      "detail": "Incorrect username or password"
    }
    ```

!!! info "Utiliser le token"
    Inclure dans le header de chaque requête protégée :  
    `Authorization: Bearer <votre_token>`  
    Le token expire après **30 minutes** (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).

---

## Endpoints publics

### `GET /`

Health check — vérifie que l'API est opérationnelle.

=== "Requête"

    ```bash
    curl http://localhost:8000/
    ```

=== "Réponse 200"

    ```json
    {
      "message": "Bienvenue sur l'API Futurisys",
      "endpoints": ["/predict/filter", "/predict/employee/{id}", "/predictions/history"]
    }
    ```

---

## Endpoints protégés

Tous ces endpoints nécessitent un **Bearer Token** valide.

### `GET /predict/filter`

Filtre les employés selon des critères RH et prédit leur risque de départ.

**Paramètres de requête :**

| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `poste` | string | non | Intitulé du poste (ex: `Consultant`) |
| `heure_supplementaires` | string | non | `Oui` ou `Non` |
| `nombre_experiences_precedentes` | int | non | Nombre min d'expériences (≥) |
| `annee_experience_totale` | int | non | Années d'expérience max (≤) |

!!! warning "Au moins un filtre requis"
    Sans aucun paramètre → `400 Bad Request`

=== "Requête"

    ```bash
    curl -X GET \
      "http://localhost:8000/predict/filter?poste=Consultant&heure_supplementaires=Oui" \
      -H "Authorization: Bearer <token>"
    ```

=== "Réponse 200"

    ```json
    {
      "filter_used": {
        "poste": "Consultant",
        "heure_supplementaires": "Oui"
      },
      "total_employees": 62,
      "total_at_risk": 39,
      "risk_rate": 0.629,
      "predictions": [
        {
          "employee_id": 4,
          "prediction": "Part",
          "probability": 0.653
        },
        {
          "employee_id": 10,
          "prediction": "Part",
          "probability": 0.528
        }
      ]
    }
    ```

=== "Réponse 400"

    ```json
    {
      "detail": "Au moins un filtre est requis"
    }
    ```

=== "Réponse 404"

    ```json
    {
      "detail": "Aucun employé trouvé avec ces filtres"
    }
    ```

---

### `GET /predict/employee/{employee_id}`

Prédit le risque de départ d'un employé individuel.

**Paramètre de chemin :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| `employee_id` | int | Identifiant unique de l'employé |

=== "Requête"

    ```bash
    curl -X GET "http://localhost:8000/predict/employee/42" \
      -H "Authorization: Bearer <token>"
    ```

=== "Réponse 200"

    ```json
    {
      "employee_id": 42,
      "prediction": "Part",
      "probability": 0.73,
      "risk_level": "Élevé"
    }
    ```

=== "Réponse 404"

    ```json
    {
      "detail": "Employé 42 introuvable"
    }
    ```

**Niveaux de risque :**

| `risk_level` | Probabilité |
|-------------|-------------|
| `Faible` | < 0.40 |
| `Modéré` | 0.40 – 0.60 |
| `Élevé` | > 0.60 |

---

### `GET /predictions/history`

Retourne l'historique de toutes les prédictions effectuées (logging en base).

=== "Requête"

    ```bash
    curl -X GET "http://localhost:8000/predictions/history" \
      -H "Authorization: Bearer <token>"
    ```

=== "Réponse 200"

    ```json
    {
      "total": 127,
      "predictions": [
        {
          "id": 127,
          "employee_id": 42,
          "prediction": "Part",
          "probability": 0.73,
          "risk_level": "Élevé",
          "filter_used": null,
          "created_at": "2026-03-26T10:30:00"
        }
      ]
    }
    ```

---

## Codes HTTP

| Code | Signification | Cas d'usage |
|------|---------------|-------------|
| `200` | Succès | Prédiction retournée |
| `400` | Bad Request | Aucun filtre fourni |
| `401` | Non authentifié | Token manquant ou expiré |
| `403` | Non autorisé | Compte inactif |
| `404` | Introuvable | Employé ou filtre sans résultat |
| `422` | Validation échouée | Paramètre invalide (ex: `heure_supplementaires=Oui2`) |
| `500` | Erreur serveur | Erreur interne |

---

## Sécurité

| Pratique | Implémentation |
|----------|---------------|
| **Hachage mots de passe** | bcrypt via `passlib` — jamais stockés en clair |
| **Tokens JWT** | Signés HS256, expiration configurable |
| **Secrets** | Variables d'environnement `.env` (non commité) |
| **Validation** | Schémas Pydantic v2 sur tous les endpoints |

!!! danger "En production"
    - Remplacer `SECRET_KEY` par une clé aléatoire (min 32 chars)
    - Utiliser HTTPS
    - Configurer `ACCESS_TOKEN_EXPIRE_MINUTES` selon la politique de sécurité
