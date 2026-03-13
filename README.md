# 🚀 Futurisys - API Prédiction Attrition des Employés (P5)

## 📋 Présentation du projet

**Contexte :** TechNova Partners, une ESN, fait face à un taux de démission de 16%.  
Ce projet déploie le modèle Random Forest entraîné en P4 sous forme d'**API REST** accessible par les équipes RH.

**Objectif :** Fournir un POC (Proof of Concept) fonctionnel permettant de :
- Prédire le risque de départ d'un employé ou d'un groupe filtré
- Consulter l'historique des prédictions
- Sécuriser l'accès via authentification JWT

**Modèle embarqué :** Random Forest optimisé — Recall 61.7% / F1-Score 50.0%

---

## 🛠️ Stack Technique

| Composant | Technologie |
|-----------|-------------|
| **API** | FastAPI 0.11x |
| **Base de données** | PostgreSQL + SQLAlchemy |
| **Authentification** | JWT (python-jose) + bcrypt (passlib) |
| **Modèle ML** | scikit-learn / joblib |
| **Gestion dépendances** | Poetry + Python 3.12 |
| **Tests** | Pytest + pytest-cov |
| **CI/CD** | GitHub Actions |

---

## 📁 Structure du Projet

```
p5-futurisys-api/
├── app/
│   ├── main.py              # Endpoints FastAPI
│   ├── auth.py              # Authentification JWT
│   ├── database.py          # Connexion SQLAlchemy
│   ├── predict.py           # Logique de prédiction ML
│   └── schemas.py           # Modèles Pydantic
├── database/
│   ├── create_db.py         # Création des tables + modèles ORM
│   └── init_data.py         # Script d'insertion des données initiales
├── ml_model/
│   └── model_pipeline.pkl   # Modèle sérialisé (joblib)
├── tests/
│   ├── test_api.py          # Tests fonctionnels des endpoints
│   ├── test_auth.py         # Tests authentification
│   └── test_db.py           # Tests intégrité base de données
├── .github/
│   └── workflows/
│       └── ci.yml           # Pipeline GitHub Actions
├── .env.example             # Template variables d'environnement
├── pyproject.toml           # Dépendances Poetry
└── README.md
```

---

## 🗄️ Architecture de la Base de Données

La base PostgreSQL `attrition_db` contient **4 tables** :

```
sirh          → données RH (poste, salaire, ancienneté...)
evaluation    → notes de performance et satisfaction
sondage       → questionnaire bien-être annuel
predictions   → logging des prédictions effectuées via l'API
```

**Jointure :** Les tables `sirh`, `evaluation` et `sondage` sont jointes sur `id_employee`.  
**Logging :** Chaque appel de prédiction est enregistré dans la table `predictions` avec : `employee_id`, `prediction`, `probability`, `filter_used`, `created_at`.

### Initialiser la base de données

```bash
# Créer les tables
python database/create_db.py

# Insérer les données
python database/init_data.py
```

---

## 🚀 Installation

### Prérequis

- Python 3.12+
- Poetry ([installation](https://python-poetry.org/docs/#installation))
- PostgreSQL (en local ou via Docker)

### Étapes d'installation

```bash
# 1. Cloner le projet
git clone <url-du-repo>
cd p5-futurisys-api

# 2. Installer les dépendances
poetry install

# 3. Activer l'environnement
poetry shell

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditer le fichier .env avec vos valeurs
```

### Variables d'environnement (`.env`)

```env
# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/attrition_db

# JWT - IMPORTANT : changer en production !
SECRET_KEY=votre-cle-secrete-longue-et-aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> ⚠️ **Ne jamais committer le fichier `.env`** — il est dans `.gitignore`

---

## 💻 Lancer l'API

```bash
# Depuis la racine du projet (env activé)
uvicorn app.main:app --reload

# L'API est disponible sur :
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
# → http://localhost:8000/redoc (ReDoc)
```

---

## 🔐 Authentification

L'API utilise **OAuth2 avec JWT (Bearer Token)**.

### Fonctionnement

1. L'utilisateur appelle `POST /token` avec ses identifiants
2. L'API retourne un `access_token` JWT (valide 30 min)
3. L'utilisateur inclut ce token dans le header de chaque requête : `Authorization: Bearer <token>`

### Endpoints publics (sans authentification)
- `GET /` — health check
- `POST /token` — obtenir un token

### Endpoints protégés (token requis)
- `GET /predict/filter`
- `GET /predict/employee/{id}`
- `GET /predictions/history`

### Exemple d'utilisation

```bash
# 1. Obtenir un token
curl -X POST "http://localhost:8000/token" \
  -d "username=admin&password=secret"

# 2. Utiliser le token
curl -X GET "http://localhost:8000/predict/filter?poste=Consultant" \
  -H "Authorization: Bearer <votre_token>"
```

---

## 🔒 Sécurité

| Pratique | Implémentation |
|----------|---------------|
| **Hachage mots de passe** | bcrypt via `passlib` — jamais stockés en clair |
| **Tokens JWT** | Signés avec `HS256`, expiration configurable |
| **Secrets** | Variables d'environnement via `.env` (non commité) |
| **Validation données** | Schémas Pydantic sur tous les endpoints |
| **Erreurs HTTP** | 401 (non authentifié), 403 (non autorisé), 404, 422 |

> ⚠️ **En production :** remplacer `SECRET_KEY` par une clé aléatoire longue (min 32 chars) et utiliser HTTPS.

---

## 📡 Endpoints de l'API

### `GET /predict/filter`
Filtre les employés et prédit leur risque de départ.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `poste` | string (optionnel) | Ex: `Consultant` |
| `heure_sup` | string (optionnel) | `Oui` ou `Non` |
| `departement` | string (optionnel) | Ex: `Commercial` |

> Au moins un filtre est requis.

**Réponse :**
```json
{
  "filter_used": "poste=Consultant",
  "total_employees": 12,
  "total_at_risk": 3,
  "risk_rate": 25.0,
  "predictions": [...]
}
```

### `GET /predict/employee/{employee_id}`
Prédit le risque pour un employé spécifique.

### `GET /predictions/history`
Consulte l'historique des prédictions loggées.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `limit` | int | Nombre max de résultats (défaut: 50) |
| `employee_id` | int (optionnel) | Filtrer par employé |

---

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Avec rapport de couverture
pytest --cov=app --cov-report=html

# Le rapport HTML est généré dans htmlcov/index.html
```

Les tests couvrent :
- **Tests fonctionnels :** tous les endpoints (200, 401, 404, 422)
- **Tests authentification :** token valide, expiré, invalide
- **Tests base de données :** intégrité des données, requêtes CRUD

---

## ⚙️ CI/CD — GitHub Actions

Le pipeline `.github/workflows/ci.yml` s'exécute à chaque push/PR sur `main` et `develop`.

**Étapes automatisées :**
1. Installation des dépendances Poetry
2. Exécution des tests Pytest
3. Génération du rapport de couverture
4. (optionnel) Déploiement si tous les tests passent

---

## 📊 Processus de Stockage des Données

**Données source :** Les 3 fichiers CSV (SIRH, EVAL, SONDAGE) sont chargés en base via `init_data.py` — lecture unique au démarrage.

**Logging des prédictions :** Chaque prédiction est automatiquement loggée dans la table `predictions` avec timestamp — permet l'audit et le suivi des alertes RH dans le temps.

**Côté analytique :** La table `predictions` peut alimenter un tableau de bord RH pour suivre l'évolution du risque par département, poste ou période.

---

## 📝 Auteur

**Barbara Di Battista**  
Projet P5 — Déploiement ML — Parcours IA Engineer — OpenClassrooms

## 📄 Licence

Projet académique — Usage éducatif uniquement
