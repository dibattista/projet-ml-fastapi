<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/dibattista/projet-ml-fastapi">
    <img src="images/logo-P5.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Futurisys — API Prédiction d'Attrition des Employés</h3>

  <p align="center">
    Une API REST sécurisée qui déploie un modèle Random Forest pour détecter le risque de départ des employés chez TechNova Partners.
    <br />
    <a href="http://localhost:8000/docs"><strong>📖 Swagger UI »</strong></a>
    <br />
    <br />
    <a href="https://barbaradi-futurisys-attrition.hf.space/demo">🎮 Démo en ligne</a>
    &middot;
    <a href="https://github.com/dibattista/projet-ml-fastapi/issues/new?labels=bug&template=bug-report---.md">🐛 Signaler un bug</a>
    &middot;
    <a href="https://github.com/dibattista/projet-ml-fastapi/issues/new?labels=enhancement&template=feature-request---.md">💡 Proposer une feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>📋 Table des matières</summary>
  <ol>
    <li>
      <a href="#about-the-project">À propos du projet</a>
      <ul>
        <li><a href="#built-with">Stack technique</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Démarrage rapide</a>
      <ul>
        <li><a href="#prerequisites">Prérequis</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Utilisation & Exemples</a></li>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#ml-model">Modèle ML & Performances</a></li>
    <li><a href="#tests">Tests</a></li>
    <li><a href="#cicd">CI/CD</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">Licence</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#documentation">Documentation</a></li>
    <li><a href="#acknowledgments">Remerciements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Futurisys Demo][product-screenshot]](https://barbaradi-futurisys-attrition.hf.space/demo)

**Contexte :** TechNova Partners, une ESN de 1 000+ employés, fait face à un **taux de démission de 16%**. Le coût de remplacement estimé par départ dépasse 6 mois de salaire.

**Solution :** Ce projet déploie le modèle **Random Forest** entraîné en P4 sous forme d'**API REST sécurisée**. Il permet aux équipes RH de :

* 🔮 Prédire le risque de départ d'un employé individuel ou d'un groupe filtré
* 📊 Consulter l'historique de toutes les prédictions (logging en base de données)
* 🔐 Accéder de façon sécurisée via authentification JWT
* 🎮 Utiliser une interface no-code via la démo Gradio

> **Périmètre POC :** L'API opère sur les employés existants stockés en base. Elle filtre, prédit, et logue. Elle n'accepte pas de nouvelles saisies d'employés (hors scope P5).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![FastAPI][FastAPI-badge]][FastAPI-url]
* [![Python][Python-badge]][Python-url]
* [![PostgreSQL][PostgreSQL-badge]][PostgreSQL-url]
* [![scikit-learn][sklearn-badge]][sklearn-url]
* [![Pytest][Pytest-badge]][Pytest-url]
* [![Docker][Docker-badge]][Docker-url]
* [![GitHub Actions][GHA-badge]][GHA-url]
* [![Hugging Face][HF-badge]][HF-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

* Python 3.12+
* Poetry — gestionnaire de dépendances
  ```sh
  curl -sSL https://install.python-poetry.org | python3 -
  ```
* PostgreSQL (en local ou via Docker)
  ```sh
  python --version   # >= 3.12
  poetry --version
  psql --version
  ```

### Installation

1. Cloner le dépôt
   ```sh
   git clone https://github.com/dibattista/projet-ml-fastapi.git
   cd projet-ml-fastapi
   ```
2. Installer les dépendances
   ```sh
   poetry install
   poetry shell
   ```
3. Configurer les variables d'environnement
   ```sh
   cp .env.example .env
   ```
4. Éditer `.env` avec vos valeurs
   ```env
   # Base de données
   DATABASE_URL=postgresql://user:password@localhost:5432/attrition_db

   # JWT — générer une clé : python -c "import secrets; print(secrets.token_hex(32))"
   SECRET_KEY=votre-cle-secrete-longue-et-aleatoire
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
   > ⚠️ Ne jamais committer le fichier `.env` — il est dans `.gitignore`

5. Initialiser la base de données
   ```sh
   python database/create_db.py
   python database/init_data.py
   ```
6. Lancer l'API
   ```sh
   uvicorn app.main:app --reload
   ```
   * API : `http://localhost:8000`
   * Swagger UI : `http://localhost:8000/docs`

7. Mettre à jour l'URL remote Git
   ```sh
   git remote set-url origin https://github.com/dibattista/projet-ml-fastapi.git
   git remote -v # confirmer le changement
   ```

8. Ajouter les captures d'écran (optionnel, pour le README)
   ```sh
   mkdir -p images
   # → copier dans images/screenshot.png  : capture de la démo Gradio (filtres + résultats)
   # → copier dans images/swagger.png     : capture du Swagger UI http://localhost:8000/docs
   # → copier dans images/logo.png        : logo du projet (80x80px)
   git add images/
   git commit -m "docs: add screenshots"
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

### 1. Authentification (obligatoire)
 Les credentials de démonstration sont disponibles sur demande auprès de l'auteur.

```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=<your_username>&password=<your_password>"
```

Réponse → utiliser `access_token` dans le header de toutes les requêtes :
```
Authorization: Bearer <votre_token>

```
### Aperçu de l'interface

| Démo Gradio | Swagger UI |
|-------------|-----------|
| [![Demo][product-screenshot]](https://barbaradi-futurisys-attrition.hf.space/demo) | [![Swagger][swagger-screenshot]](http://localhost:8000/docs) |

### Interface Gradio — Démo no-code

La démo est construite avec **Gradio Blocks**, thème **Glass**, et organisée en 4 onglets :

| Onglet | Description |
|--------|-------------|
| 🔐 **Connexion** | Authentification par nom d'utilisateur / mot de passe. Le token de session est conservé en `gr.State` pour toutes les actions suivantes. |
| 🔍 **Prédiction par filtre** | Filtres combinables (poste, heures supplémentaires, nb expériences, années d'expérience). Les résultats s'affichent sous forme de **deux KPI cards HTML** côte à côte : total d'employés analysés (bleu) et nombre + pourcentage à risque (orange/rouge), suivis du détail JSON. |
| 👤 **Prédiction par employé** | Saisie d'un ID employé. Affiche une fiche HTML avec jauge de risque de départ, jauge de probabilité de rester, et verdict coloré (🔴 / 🟢). |
| 📋 **Historique** | Charge les N dernières prédictions loguées en base, affichées en tableau JSON. |

**Choix de design :**
- Thème `gr.themes.Glass()` pour l'aspect visuel translucide
- KPI cards avec `backdrop-filter: blur` et semi-transparence pour s'intégrer au thème Glass
- Les messages d'erreur et d'état retournent du HTML coloré cohérent avec la palette

### 2. Prédiction par filtre — `GET /predict/filter`

Au moins un filtre requis (sinon `400 Bad Request`).

| Paramètre | Type | Exemple |
|-----------|------|---------|
| `poste` | string | `Consultant` |
| `heure_supplementaires` | `Oui`/`Non` | `Oui` |
| `nombre_experiences_precedentes` | int (min ≥) | `4` |
| `annee_experience_totale` | int (max ≤) | `6` |

```bash
curl -X GET "http://localhost:8000/predict/filter?poste=Consultant&heure_supplementaires=Oui" \
  -H "Authorization: Bearer <token>"
```

### 3. Prédiction individuelle — `GET /predict/employee/{id}`

```bash
curl -X GET "http://localhost:8000/predict/employee/42" \
  -H "Authorization: Bearer <token>"
```

Réponse :
```json
{
  "employee_id": 42,
  "prediction": "Part",
  "probability": 0.73,
  "risk_level": "Élevé"
}
```

### 4. Historique — `GET /predictions/history`

```bash
curl -X GET "http://localhost:8000/predictions/history" \
  -H "Authorization: Bearer <token>"
```

_Pour plus d'exemples, voir la [Documentation Swagger](http://localhost:8000/docs) et la [Démo Gradio](https://barbaradi-futurisys-attrition.hf.space/demo)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ARCHITECTURE -->
## Architecture

### Structure du projet

```
projet-ml-fastapi/
├── app/
│   ├── main.py              # Endpoints FastAPI + routing
│   ├── auth.py              # Authentification JWT (OAuth2)
│   ├── database.py          # Connexion SQLAlchemy + session
│   ├── predict.py           # Logique ML (filtrage SQL, encoding, prédiction, logging)
│   ├── features.py          # Feature engineering (job_changing, feat_junior_poste_risque)
│   └── schemas.py           # Modèles Pydantic v2 (validation I/O)
├── database/
│   ├── create_db.py         # Création des tables + modèles ORM
│   └── init_data.py         # Insertion des données initiales
├── ml_model/
│   └── model_pipeline.pkl   # Pipeline Random Forest sérialisé (joblib)
├── gradio_demo/
│   └── app.py               # Interface démo Gradio (HF Spaces)
├── tests/
│   ├── conftest.py          # Fixtures pytest (client, db SQLite in-memory, token)
│   ├── test_routes.py       # Tests endpoints FastAPI
│   ├── test_predict.py      # Tests fonctions ML (encode, predict)
│   └── test_functional.py   # Tests comportementaux (seuils métier, biais)
├── docs/                    # Documentation MkDocs Material (6 pages)
├── .github/workflows/ci.yml # Pipeline GitHub Actions
├── .env.example
├── mkdocs.yml               # Configuration MkDocs
├── deploy_hf.sh             # Script déploiement Hugging Face Spaces
├── pyproject.toml           # Dépendances Poetry
├── Dockerfile               # Image Docker (HF Spaces, port 7860)
└── README.md
```

### Base de données (5 tables)

```
┌──────────────────────────────────┐
│  USERS (authentification API)    │
│  id PK | username                │
│  hashed_password | is_active     │
└──────────────────────────────────┘

SIRH ──────┐
           ├── jointure sur id_employee
EVALUATION ┤
           │                     ┌──────────────────────────────────┐
SONDAGE ───┘── 1 employé         │ PREDICTIONS (logging API)         │
               a N predictions ──▶ id PK | employee_id FK            │
                                 │ prediction | probability          │
                                 │ risk_level | filter_used (JSON)   │
                                 │ created_at                        │
                                 └──────────────────────────────────┘
```

> **Note SQL :** `heure_supplementaires` appartient à la table `evaluation` (alias `e.`), pas à `sirh`.

### Choix techniques justifiés

| Choix | Justification |
|-------|---------------|
| **FastAPI** | Validation Pydantic automatique, Swagger intégré, async performant |
| **PostgreSQL** | Relationnel robuste, jointures multi-tables pour données RH |
| **JWT Bearer** | Standard OAuth2, stateless, compatible tous clients HTTP |
| **SQLite en CI** | Évite la dépendance PostgreSQL dans GitHub Actions |
| **Gradio imports directs** | Évite deadlocks uvicorn 1 worker — appels Python vs HTTP interne |
| **Orphan branch HF deploy** | Évite que les binaires (.pkl) bloquent l'historique Git |

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ML MODEL -->
## ML Model

### Comparaison des modèles (métrique prioritaire : Recall)

> Un faux négatif = un employé qui part sans détection préalable → coût élevé (recrutement, formation).

| Modèle | Recall | Precision | F1-Score |
|--------|--------|-----------|----------|
| Logistic Regression | 74.5% | 38.9% | 51.1% |
| **Random Forest ✅** | **61.7%** | **42.0%** | **50.0%** |
| XGBoost | 31.9% | 51.7% | 39.5% |
| CatBoost | 40.4% | 45.2% | 42.7% |
| Dummy (baseline) | 12.8% | 12.2% | 12.5% |

**Pourquoi Random Forest ?** Meilleur équilibre Recall/Precision, robuste au déséquilibre de classes (16%/84%), interprétable via SHAP TreeExplainer.

### Paramètres optimaux — GridSearchCV (180 entraînements, 36 combinaisons × 5 validations)

```python
best_params = {
    'n_estimators': 200,       # 200 arbres votent ensemble
    'max_depth': 3,            # Arbres simples → évite l'overfitting
    'min_samples_leaf': 15,    # Min 15 employés par feuille de décision
    'class_weight': 'balanced' # Compense le déséquilibre des classes
}
```

### Features engineered (`app/features.py`)

* `job_changing` — `nombre_experiences_precedentes >= 4` ET `annee_experience_totale <= 6`
* `feat_junior_poste_risque` — croisement rôle × niveau d'expérience

### Mise à jour du modèle

```sh
# 1. Ré-entraîner (notebook P4)
# 2. Sérialiser le nouveau pipeline
python -c "import joblib; joblib.dump(pipeline, 'ml_model/model_pipeline.pkl')"
# 3. Valider les tests fonctionnels
pytest tests/test_functional.py -v
# 4. PR → develop → main → CI redéploie automatiquement
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- TESTS -->
## Tests

```sh
# Tous les tests
pytest

# Avec rapport de couverture
pytest --cov=app --cov-report=term-missing

# Tests fonctionnels uniquement
pytest tests/test_functional.py -v
```

### Organisation

| Fichier | Type | Ce qui est testé |
|---------|------|-----------------|
| `test_routes.py` | Unitaire | Endpoints FastAPI — codes 200, 400, 401, 404, structure JSON |
| `test_predict.py` | Unitaire | Fonctions ML — `encode_employee_data`, `predict_employees` |
| `test_functional.py` | Fonctionnel | Comportement métier — seuil `job_changing`, `feat_junior_poste_risque`, impact heures sup |

### Couverture — 87% (71 tests passants)

| Fichier | Statements | Couverture |
|---------|-----------|-----------|
| `app/auth.py` | 48 | 96% |
| `app/main.py` | 76 | 97% |
| `app/predict.py` | 44 | 100% |
| `app/schemas.py` | 72 | 82% |
| `app/features.py` | 29 | 79% |
| `app/database.py` | 20 | 50% |
| **Total** | **950** | **87%** |

> `app/database.py` à 50% : la fonction `get_db` n'est pas appelée directement en CI (SQLite in-memory injecté via fixtures). Ce n'est pas un défaut de test — c'est une contrainte d'architecture CI/CD volontaire.

> **CI :** les tests utilisent SQLite in-memory — aucune dépendance PostgreSQL dans le pipeline.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CICD -->
## CI/CD

Le pipeline GitHub Actions se déclenche sur push vers `develop` et `main` :

1. Checkout + setup Python 3.12
2. `poetry install`
3. `pytest --cov=app` (SQLite in-memory, `SECRET_KEY` en secret GitHub)
4. ✅ Tests OK → déploiement automatique sur Hugging Face Spaces

## Déploiement Hugging Face Spaces

Le déploiement sur HF Spaces se fait via le script automatisé :

```bash
# Depuis develop (par défaut)
bash deploy_hf.sh

# Depuis main
bash deploy_hf.sh main
```

Le script :
- Crée une branche orphan propre
- Sélectionne uniquement les fichiers nécessaires
- Génère le README HF automatiquement
- Push vers HF Spaces
- Nettoie automatiquement

**Fichiers déployés :** app/, gradio_demo/, ml_model/, database/, Dockerfile, requirements.txt

| Secret GitHub | Usage |
|---------------|-------|
| `SECRET_KEY` | Clé JWT (jamais en dur dans le code) |
| `HF_TOKEN` | Token Hugging Face pour le déploiement |

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] API FastAPI avec endpoints prédiction + historique
- [x] Authentification JWT sécurisée
- [x] Base de données PostgreSQL (5 tables)
- [x] Tests unitaires & fonctionnels
- [x] Pipeline CI/CD GitHub Actions
- [x] Démo Gradio sur Hugging Face Spaces
- [x] Tests fonctionnels comportementaux (job_changing, junior_poste_risque, heures sup)
- [x] README complet
- [x] Documentation technique MkDocs
- [ ] Dashboard monitoring (data drift)
- [ ] Rate limiting sur les endpoints

Voir les [issues ouvertes](https://github.com/dibattista/projet-ml-fastapi/issues) pour la liste complète.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Workflow de développement

Ce projet suit la méthodologie **Git Flow** avec les branches suivantes :

* `main` — code stable en production (versions taguées)
* `develop` — intégration continue des features
* `feature/*` — développement de nouvelles fonctionnalités
* `release/*` — préparation des versions stables

### Créer une nouvelle feature

```bash
# 1. Se placer sur develop
git checkout develop
git pull origin develop

# 2. Créer la feature branch
git flow feature start nom-feature

# 3. Développer et commiter régulièrement
git add .
git commit -m "feat: description de la fonctionnalité"

# 4. Merger dans develop (merge manuel avec --no-ff)
git checkout develop
git merge feature/nom-feature --no-ff

# 5. Pousser develop ET la feature branch
git push origin develop
git push origin feature/nom-feature
```

> **Note :** Les branches features sont conservées pour traçabilité et visualisation de l'historique.

### Créer une release

Quand plusieurs features sont prêtes pour une version stable :

```bash
# 1. Supprimer l'ancienne release si elle existe
git branch -D release/vX.X.X
git push origin --delete release/vX.X.X

# 2. Créer la nouvelle release depuis develop
git flow release start vX.Y.Z

# 3. Merger dans main
git checkout main
git merge release/vX.Y.Z --no-ff
git push origin main

# 4. Créer et pousser le tag
git tag -a vX.Y.Z -m "Release vX.Y.Z - Description"
git push origin vX.Y.Z

# 5. Synchroniser develop
git checkout develop
git merge release/vX.Y.Z --no-ff
git push origin develop

# 6. Pousser la branche release
git push origin release/vX.Y.Z
```

**Semantic Versioning :**
- `vX.0.0` — Breaking changes (major)
- `vX.Y.0` — Nouvelles fonctionnalités (minor)
- `vX.Y.Z` — Corrections de bugs (patch)

### Déploiement sur Hugging Face Spaces

Le déploiement se fait via le script automatisé :

```bash
# Depuis develop (par défaut)
bash deploy_hf.sh

# Depuis main
bash deploy_hf.sh main

# Depuis une feature spécifique
bash deploy_hf.sh feature/nom-feature
```

**Le script :**
- Crée une branche orphan propre (sans historique)
- Sélectionne uniquement les fichiers nécessaires
- Génère le README Hugging Face automatiquement
- Push vers HF Spaces avec force
- Nettoie automatiquement la branche temporaire

**Fichiers déployés :** `app/`, `gradio_demo/`, `ml_model/`, `database/`, `Dockerfile`, `requirements.txt`

**URL de l'application :** https://huggingface.co/spaces/BarbaraDI/futurisys-attrition

### CI/CD

Les tests sont lancés automatiquement via **GitHub Actions** à chaque push sur `develop` ou `main` :

- ✅ Exécution de 62 tests unitaires et fonctionnels
- ✅ Vérification de la couverture de code
- ✅ Validation du pipeline ML
- ✅ Gestion des fichiers binaires avec Git LFS

**Configuration :** `.github/workflows/ci.yml`

### Visualisation Git Flow

L'extension **Git Graph** (VS Code) permet de visualiser l'ensemble des branches, merges et tags pour suivre l'historique du projet.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distribué sous licence MIT. Voir `LICENSE.txt` pour plus d'informations.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

**Barbara Di Battista** — Étudiante AI Engineering (OpenClassrooms)

[![LinkedIn][linkedin-shield]][linkedin-url]

Lien projet : [https://github.com/dibattista/projet-ml-fastapi](https://github.com/dibattista/projet-ml-fastapi)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- DOCUMENTATION -->
## Documentation

La documentation technique complète est disponible via MkDocs :
```bash
# Lancer la doc en local
mkdocs serve
# → http://localhost:8000/projet-ml-fastapi/
```

| Page | Contenu |
|------|---------|
| [Accueil](docs/index.md) | Architecture globale, stack technique |
| [Installation](docs/installation.md) | Local, Supabase, HF Spaces |
| [API Reference](docs/api.md) | Endpoints, exemples curl, codes HTTP |
| [Modèle ML](docs/modele.md) | Random Forest, GridSearch, features |
| [Tests](docs/tests.md) | Couverture 91%, organisation |
| [CI/CD](docs/cicd.md) | GitHub Actions, orphan branch, Git Flow |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [FastAPI](https://fastapi.tiangolo.com) — framework API moderne
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template) — structure de ce README
* [Shields.io](https://shields.io) — badges dynamiques
* [Hugging Face Spaces](https://huggingface.co/spaces) — hébergement démo gratuit
* [Supabase](https://supabase.com) — PostgreSQL managé en cloud
* [OpenClassrooms](https://openclassrooms.com) — programme AI Engineer

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/dibattista/projet-ml-fastapi.svg?style=for-the-badge
[contributors-url]: https://github.com/dibattista/projet-ml-fastapi/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/dibattista/projet-ml-fastapi.svg?style=for-the-badge
[forks-url]: https://github.com/dibattista/projet-ml-fastapi/network/members
[stars-shield]: https://img.shields.io/github/stars/dibattista/projet-ml-fastapi.svg?style=for-the-badge
[stars-url]: https://github.com/dibattista/projet-ml-fastapi/stargazers
[issues-shield]: https://img.shields.io/github/issues/dibattista/projet-ml-fastapi.svg?style=for-the-badge
[issues-url]: https://github.com/dibattista/projet-ml-fastapi/issues
[license-shield]: https://img.shields.io/github/license/dibattista/projet-ml-fastapi.svg?style=for-the-badge
[license-url]: https://github.com/dibattista/projet-ml-fastapi/blob/main/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/barbara-di-battista

[FastAPI-badge]: https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white
[FastAPI-url]: https://fastapi.tiangolo.com
[Python-badge]: https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://python.org
[PostgreSQL-badge]: https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white
[PostgreSQL-url]: https://www.postgresql.org
[sklearn-badge]: https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white
[sklearn-url]: https://scikit-learn.org
[Pytest-badge]: https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white
[Pytest-url]: https://pytest.org
[Docker-badge]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://docker.com
[GHA-badge]: https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white
[GHA-url]: https://github.com/features/actions
[HF-badge]: https://img.shields.io/badge/🤗_Hugging_Face-FFD21E?style=for-the-badge
[HF-url]: https://huggingface.co/spaces/barbaradi/futurisys-attrition
[product-screenshot]: images/HF-app.png
[swagger-screenshot]: images/swagger.png