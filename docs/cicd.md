# CI/CD — GitHub Actions & HF Spaces

## Vue d'ensemble

```
Push sur develop ou main
        │
        ▼
┌─────────────────────┐
│ GitHub Actions CI   │
│ 1. checkout         │
│ 2. setup Python 3.12│
│ 3. poetry install   │
│ 4. pytest --cov=app │
└──────────┬──────────┘
           │ ✅ Tests passent
           ▼
┌─────────────────────┐
│ Déploiement         │
│ HF Spaces           │
│ (orphan branch)     │
└─────────────────────┘
```

---

## Pipeline GitHub Actions

### Fichier `.github/workflows/ci.yml`

```yaml
name: CI — Tests & Deploy

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python 3.12
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies
        run: poetry install

      - name: Run tests
        env:
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
        run: poetry run pytest --cov=app --cov-report=term-missing

      - name: Deploy to HF Spaces
        if: github.ref == 'refs/heads/main'
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: bash deploy_hf.sh
```

### Points clés

| Élément | Détail |
|---------|--------|
| **Déclencheurs** | Push sur `develop` et `main` |
| **OS** | Ubuntu latest |
| **Python** | 3.12 (même version que prod) |
| **DB en CI** | SQLite in-memory (pas de PostgreSQL) |
| **SECRET_KEY** | Injectée via GitHub Secrets — jamais en dur |
| **Deploy** | Uniquement sur `main` |

---

## Secrets GitHub

Configurer dans **Settings → Secrets and variables → Actions** :

| Secret | Description | Obligatoire |
|--------|-------------|-------------|
| `SECRET_KEY` | Clé JWT de l'API | ✅ |
| `HF_TOKEN` | Token Hugging Face pour le déploiement | ✅ (si deploy auto) |

---

## Déploiement Hugging Face Spaces

### Pourquoi le pattern orphan branch ?

!!! warning "Problème avec les fichiers binaires"
    Le fichier `ml_model/model_pipeline.pkl` est un binaire (≈ plusieurs MB).  
    Git LFS ou un historique avec ce fichier bloque les push vers HF.  
    **Solution :** créer une branche sans aucun historique à chaque déploiement.

### Procédure manuelle

```bash
# 1. Créer une branche orpheline (sans historique)
git checkout --orphan hf-deploy

# 2. Ajouter tous les fichiers
git add .
git commit -m "deploy: v1.5.0"

# 3. Forcer le push vers HF (remote 'hf' configuré)
git push hf main --force

# 4. Revenir sur sa branche et supprimer l'orpheline
git checkout feature/ma-branche
git branch -D hf-deploy
```

### Configurer le remote HF

```bash
git remote add hf https://huggingface.co/spaces/barbaradi/futurisys-attrition
# ou avec token :
git remote add hf https://barbaradi:$HF_TOKEN@huggingface.co/spaces/barbaradi/futurisys-attrition
```

### Script `deploy_hf.sh`

```bash
#!/bin/bash
git checkout --orphan hf-deploy
git add .
git commit -m "deploy: $(date +%Y-%m-%d)"
git push hf main --force
git checkout -
git branch -D hf-deploy
```

---

## Git Flow

Le projet utilise **Git Flow** comme stratégie de branches :

| Branche | Usage |
|---------|-------|
| `main` | Production — code stable et testé |
| `develop` | Intégration — prochaine release |
| `feature/*` | Développement de nouvelles fonctionnalités |
| `release/*` | Préparation d'une release (tests finaux) |
| `hotfix/*` | Corrections urgentes en production |

### Workflow standard

```bash
# Démarrer une feature
git flow feature start ma-feature

# Terminer et merger dans develop
git flow feature finish ma-feature

# Préparer une release
git flow release start v1.6.0
git flow release finish v1.6.0
# → merge dans main ET develop + tag automatique
```

!!! tip "Supprimer les vieilles branches release"
    Avant `git flow release start`, vérifier qu'aucune branche `release/*` n'existe :
    ```bash
    git branch -D release/v1.4.0
    git push origin --delete release/v1.4.0
    ```
    Les tags existants font échouer `git flow release finish` sinon.
