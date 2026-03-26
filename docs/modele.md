# Modèle ML — Random Forest

## Contexte métier

La métrique prioritaire est le **Recall** (sensibilité).

!!! question "Pourquoi le Recall ?"
    Un **faux négatif** = un employé qui part sans qu'on l'ait détecté.  
    Coût estimé : **6 mois de salaire** (recrutement, onboarding, perte de savoir-faire).  
    → Mieux vaut alerter à tort que rater un départ.

---

## Comparaison des modèles

4 modèles testés sur les données TechNova (1 470 employés, déséquilibre 16%/84%) :

| Modèle | Recall | Precision | F1-Score |
|--------|--------|-----------|----------|
| Logistic Regression | 74.5% | 38.9% | 51.1% |
| **Random Forest ✅** | **61.7%** | **42.0%** | **50.0%** |
| XGBoost | 31.9% | 51.7% | 39.5% |
| CatBoost | 40.4% | 45.2% | 42.7% |
| Dummy (baseline) | 12.8% | 12.2% | 12.5% |

### Pourquoi Random Forest ?

- ✅ **Meilleur équilibre Recall/Precision** parmi les modèles non-linéaires
- ✅ **Robuste au déséquilibre** de classes via `class_weight='balanced'`
- ✅ **Interprétable** nativement (feature importance + SHAP TreeExplainer rapide)
- ✅ **Stable** : faible variance grâce à l'agrégation de 200 arbres

!!! note "Logistic Regression vs Random Forest"
    La Logistic Regression a un meilleur Recall (74.5%) mais une Precision très faible (38.9%).  
    Trop de fausses alertes surchargerait les équipes RH — le Random Forest offre un meilleur équilibre opérationnel.

---

## Paramètres optimaux

Optimisation via **GridSearchCV** : 36 combinaisons × 5 validations = **180 entraînements**.

```python
param_grid = {
    'n_estimators':    [100, 200, 300],
    'max_depth':       [3, 5, 7, 10],
    'min_samples_leaf':[5, 10, 15],
    'class_weight':    ['balanced']
}

best_params = {
    'n_estimators': 200,        # 200 arbres votent ensemble
    'max_depth': 3,             # Arbres simples → évite l'overfitting
    'min_samples_leaf': 15,     # Min 15 employés par feuille de décision
    'class_weight': 'balanced'  # Compense le déséquilibre 16%/84%
}
```

---

## Feature Engineering

Les features suivantes sont calculées automatiquement dans `app/features.py` :

### `job_changing`

Identifie les profils "instables" qui changent fréquemment d'entreprise.

```python
job_changing = (
    (nombre_experiences_precedentes >= 4) AND
    (annee_experience_totale <= 6)
)
```

**Hypothèse métier :** Un profil avec ≥ 4 expériences en ≤ 6 ans total a un historique de mobilité élevé.

### `feat_junior_poste_risque`

Croisement rôle × niveau d'expérience.

```python
feat_junior_poste_risque = (
    annee_experience_totale <= 7 AND
    poste IN ('Commercial', 'Consultant', 'Technicien')
)
```

**Hypothèse métier :** Les juniors dans des postes à forte pression partent plus souvent.

---

## Données d'entrainement

| Caractéristique | Valeur |
|-----------------|--------|
| Employés | 1 470 |
| Variables brutes | 34 |
| Variables après encoding | 41 |
| Départs (cible = 1) | 16% |
| Restants (cible = 0) | 84% |
| Valeurs manquantes | 0 |

**Sources :** 3 tables jointes — `sirh` (données RH), `evaluation` (notes et satisfaction), `sondage` (bien-être).

---

## Mise à jour du modèle

### Quand mettre à jour ?

| Fréquence | Action |
|-----------|--------|
| Mensuel | Vérifier la dérive des distributions (data drift) |
| Trimestriel | Comparer le Recall sur les nouvelles données |
| Si Recall < 55% | Ré-entraîner le modèle |

### Procédure

```bash
# 1. Ré-entraîner dans le notebook P4
# 2. Sérialiser le nouveau pipeline
python -c "import joblib; joblib.dump(pipeline, 'ml_model/model_pipeline.pkl')"

# 3. Valider les tests fonctionnels
pytest tests/test_functional.py -v

# 4. Si tests OK → PR → develop → main → CI redéploie
git checkout -b feature/update-model
git add ml_model/model_pipeline.pkl
git commit -m "ml: update Random Forest pipeline vX.Y"
git push origin feature/update-model
```

!!! warning "Le modèle est chargé en mémoire au démarrage"
    `model_pipeline.pkl` est chargé une seule fois au lancement de l'API via `joblib.load()`.  
    Un redémarrage est nécessaire après chaque mise à jour du fichier `.pkl`.
