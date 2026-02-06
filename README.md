# 🎯 TechNova - Analyse de l'Attrition des Employés

## 📋 Contexte

TechNova Partners, une ESN (Entreprise de Services du Numérique), fait face à un taux de démission élevé (16%). Ce projet vise à :

- Identifier les causes principales de départ
- Construire un modèle prédictif pour détecter les employés à risque
- Proposer des leviers d'action concrets

## 📊 Données Disponibles

| Source | Description | Contenu principal |
|--------|-------------|-------------------|
| **SIRH** | Données RH | Poste, âge, salaire, ancienneté, département |
| **EVAL** | Évaluations | Notes de performance, satisfaction employé |
| **SONDAGE** | Bien-être | Questionnaire annuel + indicateur de départ |

**Population :** 1 470 employés

## 🛠️ Stack Technique

- **Python 3.11+**
- **Manipulation données :** Pandas, NumPy
- **Visualisation :** Matplotlib, Seaborn
- **Machine Learning :** Scikit-learn, XGBoost, CatBoost
- **Équilibrage classes :** Imbalanced-learn
- **Interprétabilité :** SHAP

## 📁 Structure du Projet

```
technova-attrition-analysis/
├── data/
│   ├── extrait_sirh.csv
│   ├── extrait_eval.csv
│   └── extrait_sondage.csv
├── notebooks/
│   ├── 01_exploration_fusion.ipynb
│   └── 02_preparation_modelisation.ipynb
├── graphics/
│   └── (visualisations exportées)
├── pyproject.toml
└── README.md
```

## 🚀 Installation

### Prérequis

- Python 3.11 ou supérieur
- Poetry ([installation](https://python-poetry.org/docs/#installation))
- VSCode avec l'extension **Jupyter** (recommandé)

### Étapes d'installation

```bash
# 1. Cloner le projet
git clone <url-du-repo>
cd technova-attrition-analysis

# 2. Installer les dépendances avec Poetry
poetry install

# 3. Activer l'environnement
poetry shell

# 4. Enregistrer le kernel Jupyter (important pour VSCode)
python -m ipykernel install --user --name=technova-attrition
```

## 💻 Lancer le projet

### Option 1 : Avec VSCode (recommandé)

1. Ouvrir le dossier du projet dans VSCode
2. Ouvrir un notebook `.ipynb`
3. Si VSCode demande un kernel :
   - Cliquer sur **"Change Kernel"**
   - Puis **"Select Another Kernel..."**
   - Puis **"Python Environments..."**
   - Choisir **"technova-attrition-analysis... (Poetry Env)"**

> ⚠️ **Si le kernel n'apparaît pas**, relancer la commande :
> ```bash
> python -m ipykernel install --user --name=technova-attrition
> ```

### Option 2 : Avec Jupyter dans le navigateur

```bash
# Activer l'environnement si pas déjà fait
poetry shell

# Lancer Jupyter
jupyter notebook
```

## 🔧 Dépannage

| Problème | Solution |
|----------|----------|
| `jupyter: command not found` | Lancer `poetry install` puis `poetry shell` |
| Kernel non trouvé dans VSCode | Relancer `python -m ipykernel install --user --name=technova-attrition` |
| Packages non importés | Vérifier qu'on est dans le bon environnement avec `poetry env info` |
| VSCode demande pip/ipykernel | Cliquer "Change Kernel" et sélectionner l'environnement Poetry |

## 📈 Méthodologie

### Phase 1 : Exploration
- Nettoyage et fusion des 3 sources
- Analyse des profils démissionnaires vs restants
- Identification des corrélations clés

### Phase 2 : Modélisation
- Modèle baseline (Dummy)
- Modèles linéaires et non-linéaires
- Gestion du déséquilibre des classes
- Feature engineering

### Phase 3 : Interprétation
- Feature importance globale (SHAP Beeswarm)
- Feature importance locale (Waterfall plots)
- Recommandations actionnables

## 📝 Auteur

**Barbara Di Battista**  
Projet réalisé dans le cadre du parcours Data Analyst / IA - OpenClassrooms

## 📄 Licence

Projet académique - Usage éducatif uniquement
