"""
conftest.py - Configuration partagée pour tous les tests Pytest
Projet P5 - Futurisys API Attrition
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── Imports du projet ──────────────────────────────────────────
from app.main import app
from app.database import get_db
from database.create_db import Base, User
from app.auth import create_access_token, get_password_hash


# ══════════════════════════════════════════════════════════════
# 1. BASE DE DONNÉES DE TEST (SQLite en mémoire)
# ══════════════════════════════════════════════════════════════
# On utilise SQLite à la place de PostgreSQL pour les tests :
# - Pas besoin d'un serveur PostgreSQL lancé
# - La base se crée et se détruit automatiquement
# - Chaque session de test repart d'une base propre

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine_test = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Nécessaire pour SQLite
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test
)


# ══════════════════════════════════════════════════════════════
# 2. FIXTURE : SESSION BASE DE DONNÉES
# ══════════════════════════════════════════════════════════════
@pytest.fixture(scope="function")
def db_session():
    """
    Crée les tables, fournit une session de test,
    puis supprime tout après chaque test.
    scope="function" → chaque test repart d'une base vide
    """
    Base.metadata.create_all(bind=engine_test)   # Crée les tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine_test)  # Nettoie après le test


# ══════════════════════════════════════════════════════════════
# 3. FIXTURE : CLIENT HTTP DE TEST
# ══════════════════════════════════════════════════════════════
@pytest.fixture(scope="function")
def client(db_session):
    """
    Crée un TestClient FastAPI qui utilise la DB de test.
    L'override remplace get_db (PostgreSQL) par db_session (SQLite).
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # La fermeture est gérée par la fixture db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()  # Remet les dépendances d'origine


# ══════════════════════════════════════════════════════════════
# 4. FIXTURE : UTILISATEUR DE TEST
# ══════════════════════════════════════════════════════════════
@pytest.fixture(scope="function")
def test_user(db_session):
    """
    Crée un utilisateur de test dans la DB.
    Utilisé pour tester l'authentification.
    """
    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ══════════════════════════════════════════════════════════════
# 5. FIXTURE : HEADERS D'AUTHENTIFICATION
# ══════════════════════════════════════════════════════════════
@pytest.fixture(scope="function")
def auth_headers(test_user):
    """
    Génère un token JWT valide pour les routes protégées.
    Usage dans les tests : client.get("/predict/...", headers=auth_headers)
    """
    token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}

# ══════════════════════════════════════════════════════════════
# HELPER PARTAGÉ : Insérer un employé de test
# ══════════════════════════════════════════════════════════════
from sqlalchemy import text

def insert_employee(db_session, employee_id=1, poste="Consultant",
                    departement="Consulting", heure_sup="Non"):
    """
    Helper partagé entre test_routes.py et test_functional.py.
    Insère un employé complet dans sirh, evaluation et sondage.
    """
    db_session.execute(text("""
        INSERT INTO sirh (
            id_employee, age, genre, revenu_mensuel, statut_marital,
            departement, poste, nombre_experiences_precedentes,
            nombre_heures_travailless, annee_experience_totale,
            annees_dans_l_entreprise, annees_dans_le_poste_actuel
        ) VALUES (
            :id, 30, 'M', 5000, 'Celibataire',
            :dept, :poste, 2, 40, 5, 3, 2
        )
    """), {"id": employee_id, "dept": departement, "poste": poste})

    db_session.execute(text("""
        INSERT INTO evaluation (
            eval_number, satisfaction_employee_environnement,
            note_evaluation_precedente, niveau_hierarchique_poste,
            satisfaction_employee_nature_travail, satisfaction_employee_equipe,
            satisfaction_employee_equilibre_pro_perso, note_evaluation_actuelle,
            heure_supplementaires, augementation_salaire_precedente
        ) VALUES (
            :id, 3, 3, 2, 3, 3, 3, 3, :heure_sup, '10 %'
        )
    """), {"id": employee_id, "heure_sup": heure_sup})

    db_session.execute(text("""
        INSERT INTO sondage (
            code_sondage, a_quitte_l_entreprise, nombre_participation_pee,
            nb_formations_suivies, nombre_employee_sous_responsabilite,
            distance_domicile_travail, niveau_education, domaine_etude,
            ayant_enfants, frequence_deplacement,
            annees_depuis_la_derniere_promotion, annes_sous_responsable_actuel
        ) VALUES (
            :id, 'Non', 2, 2, 0, 10, 3, 'Informatique',
            'Y', 'Occasionnel', 1, 2
        )
    """), {"id": employee_id})

    db_session.commit()