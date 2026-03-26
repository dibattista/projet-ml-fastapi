# Installation & Configuration

## Prérequis

Avant de commencer, vérifier que vous avez :

| Outil | Version minimale | Vérification |
|-------|-----------------|--------------|
| Python | 3.12+ | `python --version` |
| Poetry | 1.8+ | `poetry --version` |
| PostgreSQL | 14+ | `psql --version` |
| Git | — | `git --version` |

### Installer Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

---

## Installation locale

### 1. Cloner le dépôt

```bash
git clone https://github.com/dibattista/projet-ml-fastapi.git
cd projet-ml-fastapi
```

### 2. Installer les dépendances

```bash
poetry install
poetry shell
```

### 3. Variables d'environnement

```bash
cp .env.example .env
```

Éditer `.env` :

```env
# ── Base de données ──────────────────────────────
DATABASE_URL=postgresql://user:password@localhost:5432/attrition_db

# ── JWT ──────────────────────────────────────────
# Générer une clé sécurisée :
# python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=votre-cle-secrete-longue-et-aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

!!! danger "Sécurité"
    Ne jamais committer le fichier `.env` — il est dans `.gitignore`.  
    En production, utiliser des secrets d'environnement (GitHub Secrets, Supabase env vars).

### 4. Initialiser la base de données

```bash
# Créer les tables (sirh, evaluation, sondage, predictions, users)
python database/create_db.py

# Insérer les données initiales (1470 employés TechNova)
python database/init_data.py
```

### 5. Lancer l'API

```bash
uvicorn app.main:app --reload
```

L'API est disponible sur :

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | Health check |
| `http://localhost:8000/docs` | **Swagger UI (recommandé)** |
| `http://localhost:8000/redoc` | ReDoc |

---

## Déploiement cloud (Hugging Face Spaces)

### Configuration Supabase

Supabase est utilisé comme PostgreSQL managé pour le déploiement HF Spaces.

1. Créer un projet sur [supabase.com](https://supabase.com)
2. Récupérer l'URL de connexion dans **Settings → Database → Connection string**
3. Configurer dans les secrets HF Spaces :

```env
DATABASE_URL=postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres
```

### Dockerfile

L'application tourne dans un container Docker sur HF Spaces (port 7860) :

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install poetry && poetry install --no-dev
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

### Pattern de déploiement

!!! note "Orphan branch — pourquoi ?"
    Les fichiers binaires (`.pkl`) dans l'historique Git bloquent les push vers HF.  
    La solution : créer une branche orpheline sans historique à chaque déploiement.

```bash
# À répéter à chaque déploiement
git checkout --orphan hf-deploy
git add .
git commit -m "deploy: v1.5.0"
git push hf main --force   # remote HF configuré
git checkout feature/ma-branche
git branch -D hf-deploy
```

---

## Structure des fichiers de configuration

```
projet-ml-fastapi/
├── .env.example          ← template variables d'environnement
├── pyproject.toml        ← dépendances Poetry
├── pytest.ini            ← configuration pytest
├── Dockerfile            ← image Docker pour HF Spaces
└── .github/
    └── workflows/
        └── ci.yml        ← pipeline GitHub Actions
```
