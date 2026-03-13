"""
test_routes.py - Tests des endpoints FastAPI
Projet P5 - Futurisys API Attrition

On teste les 4 endpoints de main.py :
- GET /                          → route publique (santé)
- GET /predict/filter            → prédiction par filtre
- GET /predict/employee/{id}     → prédiction par employé
- GET /predictions/history       → historique des prédictions

Fixtures utilisées depuis conftest.py :
- client       → TestClient FastAPI avec DB de test
- auth_headers → token JWT valide
"""

import pytest
from sqlalchemy import text
from conftest import insert_employee

# ══════════════════════════════════════════════════════════════
# 1. TESTS DE LA ROUTE RACINE /
# ══════════════════════════════════════════════════════════════

class TestRootEndpoint:
    """La route / est publique, pas besoin de token."""

    def test_root_status_200(self, client):
        """La route racine répond 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contient_message(self, client):
        """La réponse contient le message de bienvenue."""
        response = client.get("/")
        body = response.json()
        assert "message" in body
        assert "Futurisys" in body["message"]

    def test_root_contient_endpoints(self, client):
        """La réponse liste les endpoints disponibles."""
        response = client.get("/")
        body = response.json()
        assert "endpoints" in body
        assert len(body["endpoints"]) > 0


# ══════════════════════════════════════════════════════════════
# 2. TESTS DE /predict/filter
# ══════════════════════════════════════════════════════════════

class TestPredictFilter:
    """Tests de l'endpoint GET /predict/filter"""

    def test_sans_token_retourne_401(self, client):
        """Sans token → 401."""
        response = client.get("/predict/filter?poste=Consultant")
        assert response.status_code == 401

    def test_sans_filtre_retourne_400(self, client, auth_headers):
        """Sans aucun filtre → 400 Bad Request."""
        response = client.get("/predict/filter", headers=auth_headers)
        assert response.status_code == 422

    def test_filtre_inexistant_retourne_404(self, client, auth_headers):
        """Filtre valide mais aucun employé trouvé → 404."""
        response = client.get(
            "/predict/filter?poste=Consultant",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_filtre_valide_retourne_200(self, client, db_session, auth_headers):
        """Filtre valide avec employé en DB → 200 avec prédictions."""
        insert_employee(db_session, employee_id=1)

        response = client.get(
            "/predict/filter?poste=Consultant",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_structure_reponse_filter(self, client, db_session, auth_headers):
        """La réponse contient les champs attendus."""
        insert_employee(db_session, employee_id=1)

        response = client.get(
            "/predict/filter?poste=Consultant",
            headers=auth_headers
        )
        body = response.json()

        assert "filter_used" in body
        assert "total_employees" in body
        assert "total_at_risk" in body
        assert "risk_rate" in body
        assert "predictions" in body
        assert isinstance(body["predictions"], list)

    def test_total_employees_correct(self, client, db_session, auth_headers):
        """Le total d'employés correspond au nombre inséré."""
        insert_employee(db_session, employee_id=1)

        response = client.get(
            "/predict/filter?poste=Consultant",
            headers=auth_headers
        )
        body = response.json()
        assert body["total_employees"] == 1

    def test_poste_invalide_retourne_422(self, client, auth_headers):
        """Valeur de poste inconnue → 422 rejeté par Pydantic."""
        response = client.get(
            "/predict/filter?poste=InexistantXYZ",
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_heure_sup_invalide_retourne_422(self, client, auth_headers):
        """Valeur heure_sup ni Oui ni Non → 422."""
        response = client.get(
            "/predict/filter?heure_sup=maybe",
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_departement_invalide_retourne_422(self, client, auth_headers):
        """Département inconnu → 422."""
        response = client.get(
            "/predict/filter?departement=Martiens",
            headers=auth_headers
        )
        assert response.status_code == 422


# ══════════════════════════════════════════════════════════════
# 3. TESTS DE /predict/employee/{id}
# ══════════════════════════════════════════════════════════════

class TestPredictEmployee:
    """Tests de l'endpoint GET /predict/employee/{employee_id}"""

    def test_sans_token_retourne_401(self, client):
        """Sans token → 401."""
        response = client.get("/predict/employee/1")
        assert response.status_code == 401

    def test_employe_inexistant_retourne_404(self, client, auth_headers):
        """ID qui n'existe pas en DB → 404."""
        response = client.get("/predict/employee/9999", headers=auth_headers)
        assert response.status_code == 404

    def test_employe_valide_retourne_200(self, client, db_session, auth_headers):
        """Employé existant → 200."""
        insert_employee(db_session, employee_id=1)

        response = client.get("/predict/employee/1", headers=auth_headers)
        assert response.status_code == 200

    def test_structure_reponse_employee(self, client, db_session, auth_headers):
        """La réponse contient les champs de prédiction."""
        insert_employee(db_session, employee_id=1)

        response = client.get("/predict/employee/1", headers=auth_headers)
        body = response.json()

        assert "employee_id" in body
        assert "prediction" in body
        assert "probability" in body
        assert "risk_level" in body

    def test_prediction_valeur_valide(self, client, db_session, auth_headers):
        """La prédiction est 'Part' ou 'Reste'."""
        insert_employee(db_session, employee_id=1)

        response = client.get("/predict/employee/1", headers=auth_headers)
        body = response.json()

        assert body["prediction"] in ["Part", "Reste"]

    def test_probabilite_entre_0_et_1(self, client, db_session, auth_headers):
        """La probabilité est bien entre 0 et 1."""
        insert_employee(db_session, employee_id=1)

        response = client.get("/predict/employee/1", headers=auth_headers)
        body = response.json()

        assert 0.0 <= body["probability"] <= 1.0


# ══════════════════════════════════════════════════════════════
# 4. TESTS DE /predictions/history
# ══════════════════════════════════════════════════════════════

class TestPredictionsHistory:
    """Tests de l'endpoint GET /predictions/history"""

    def test_sans_token_retourne_401(self, client):
        """Sans token → 401."""
        response = client.get("/predictions/history")
        assert response.status_code == 401

    def test_historique_vide_retourne_200(self, client, auth_headers):
        """Historique vide → 200 avec liste vide."""
        response = client.get("/predictions/history", headers=auth_headers)
        assert response.status_code == 200

        body = response.json()
        assert body["total_predictions"] == 0
        assert body["predictions"] == []

    def test_historique_apres_prediction(self, client, db_session, auth_headers):
        """Après une prédiction → l'historique contient 1 entrée."""
        insert_employee(db_session, employee_id=1)

        # Déclenche une prédiction → elle est loggée automatiquement
        client.get("/predict/employee/1", headers=auth_headers)

        # Vérifie que la prédiction est bien dans l'historique
        response = client.get("/predictions/history", headers=auth_headers)
        body = response.json()

        assert body["total_predictions"] == 1
        assert body["predictions"][0]["employee_id"] == 1

    def test_filtre_par_employee_id(self, client, db_session, auth_headers):
        """Le filtre par employee_id fonctionne."""
        insert_employee(db_session, employee_id=1)
        client.get("/predict/employee/1", headers=auth_headers)

        response = client.get(
            "/predictions/history?employee_id=1",
            headers=auth_headers
        )
        body = response.json()
        assert body["total_predictions"] >= 1
        assert all(p["employee_id"] == 1 for p in body["predictions"])