# Tests

## Lancer les tests

```bash
# Tous les tests
pytest

# Avec rapport de couverture (terminal)
pytest --cov=app --cov-report=term-missing

# Rapport HTML (navigable)
pytest --cov=app --cov-report=html
# → ouvrir htmlcov/index.html

# Tests fonctionnels uniquement
pytest tests/test_functional.py -v
```

---

## Résultats actuels

!!! success "91% de couverture — 71 tests passants"

| Fichier | Statements | Manquants | Couverture |
|---------|-----------|-----------|-----------|
| `app/auth.py` | 48 | 2 | **96%** |
| `app/main.py` | 76 | 2 | **97%** |
| `app/predict.py` | 44 | 0 | **100%** |
| `app/schemas.py` | 72 | 13 | **82%** |
| `app/features.py` | 29 | 6 | **79%** |
| `app/database.py` | 20 | 4 | **50%** |
| **Total** | **291** | **27** | **91%** |

!!! note "`app/database.py` à 50% — pourquoi ?"
    La fonction `get_db` n'est pas appelée directement en CI.  
    En tests, SQLite in-memory est injecté via fixtures `conftest.py`.  
    Ce n'est pas un défaut — c'est une contrainte d'architecture CI/CD volontaire.

---

## Organisation des tests

### `tests/test_routes.py` — Tests unitaires endpoints

Teste tous les endpoints FastAPI avec le `TestClient`.

| Test | Code attendu | Scénario |
|------|-------------|----------|
| `test_root_status_200` | 200 | Route `/` publique |
| `test_sans_token_retourne_401` | 401 | Endpoint protégé sans token |
| `test_sans_filtre_retourne_400` | 400 | `/predict/filter` sans paramètre |
| `test_filtre_inexistant_retourne_404` | 404 | Filtre valide mais aucun employé |
| `test_filtre_valide_retourne_200` | 200 | Filtre avec employé en DB |
| `test_structure_reponse_filter` | — | Champs `total_employees`, `risk_rate`... |
| `test_employe_inexistant_retourne_404` | 404 | ID inconnu |
| `test_prediction_valeur_valide` | — | `prediction` ∈ {"Part", "Reste"} |
| `test_probabilite_entre_0_et_1` | — | `probability` ∈ [0.0, 1.0] |

### `tests/test_predict.py` — Tests fonctions ML

Teste les fonctions Python pures — **sans base de données ni token**.

```python
def make_employee_df(**kwargs):
    """Construit un DataFrame minimal valide (1 employé)."""
    data = {
        "id_employee": 1,
        "age": 30,
        "poste": "Consultant",
        "heure_supplementaires": "Non",
        "nombre_experiences_precedentes": 2,
        "annee_experience_totale": 5,
        # ...
    }
    data.update(kwargs)
    return pd.DataFrame([data])
```

| Fonction testée | Ce qui est vérifié |
|----------------|-------------------|
| `encode_employee_data()` | Nombre de features, valeurs numériques |
| `predict_employees()` | Prédiction ∈ {"Part", "Reste"}, probabilité [0,1] |

### `tests/test_functional.py` — Tests comportementaux

Vérifie que le modèle se **comporte comme prévu** sur des cas métier précis.

#### Test 1 — Seuil `job_changing`

```python
def test_job_changing_augmente_risque():
    """
    Un profil avec job_changing=True doit avoir
    une probabilité de départ plus élevée.
    """
    df_stable = make_employee_df(
        nombre_experiences_precedentes=1,
        annee_experience_totale=10
    )
    df_mobile = make_employee_df(
        nombre_experiences_precedentes=5,   # >= 4 ✓
        annee_experience_totale=4           # <= 6 ✓
    )
    prob_stable = predict_employees(encode_employee_data(df_stable))["probability"]
    prob_mobile = predict_employees(encode_employee_data(df_mobile))["probability"]
    assert prob_mobile > prob_stable
```

#### Test 2 — Feature `feat_junior_poste_risque`

Vérifie que les juniors dans des postes à risque ont une probabilité de départ plus élevée que les seniors dans le même poste.

#### Test 3 — Impact heures supplémentaires

Vérifie que `heure_supplementaires=Oui` augmente la probabilité de départ par rapport à `Non`, toutes choses égales par ailleurs.

---

## Infrastructure de test

### `tests/conftest.py`

```python
# Base de données SQLite in-memory pour CI
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False}
)

@pytest.fixture
def client(db_session):
    """TestClient FastAPI avec DB de test injectée."""
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    """Token JWT valide pour les tests protégés."""
    response = client.post("/token", data={"username": "test", "password": "test"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

!!! info "Pourquoi SQLite en CI ?"
    Évite la dépendance PostgreSQL dans GitHub Actions.  
    SQLite in-memory est identique fonctionnellement pour les tests — 
    SQLAlchemy abstrait les différences de dialecte.
