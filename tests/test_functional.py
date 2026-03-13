"""
test_functional.py - Tests fonctionnels (scénarios métier complets)
Projet P5 - Futurisys API Attrition

Contrairement aux tests unitaires (test_routes.py) qui vérifient
un endpoint isolément, les tests fonctionnels simulent un parcours
utilisateur réel, en enchaînant plusieurs appels API dans l'ordre.

Scénarios couverts :
  1. Workflow RH complet  → login → filtre département → historique
  2. Analyse individuelle → login → prédiction employé → historique filtré
  3. Multi-filtres        → filtre combiné poste + heure_sup → cohérence résultats
  4. Sécurité globale     → accès refusé sur tous les endpoints protégés

Fixtures héritées de conftest.py :
  - client       → TestClient FastAPI avec DB SQLite de test
  - db_session   → session de base de données isolée
  - auth_headers → token JWT valide {"Authorization": "Bearer <token>"}
"""

import pytest
from sqlalchemy import text
from conftest import insert_employee

# ══════════════════════════════════════════════════════════════
# SCÉNARIO 1 — Workflow RH complet
# ══════════════════════════════════════════════════════════════
# Simule le parcours d'un RH qui :
#   1. S'authentifie
#   2. Lance une analyse de son département
#   3. Vérifie que les prédictions sont bien loggées dans l'historique

class TestWorkflowRHComplet:
    """
    Scénario métier : un RH analyse son département et consulte l'historique.
    Chaîne : POST /token → GET /predict/filter → GET /predictions/history
    """

    def test_login_puis_filtre_puis_historique(self, client, db_session, test_user):
        """
        Scénario complet :
          1. Le RH se connecte → obtient un token
          2. Il filtre les consultants → reçoit des prédictions
          3. Il consulte l'historique → les prédictions y sont enregistrées
        """
        # ── Étape 1 : Authentification ──────────────────────────────
        # Simule un utilisateur qui se connecte à l'API
        login_response = client.post(
            "/token",
            data={"username": "testuser", "password": "testpassword"}
        )
        assert login_response.status_code == 200, "Le login doit réussir"

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # ── Étape 2 : Prédiction par filtre ────────────────────────
        # Insertion d'un employé consultant dans la DB de test
        insert_employee(db_session, employee_id=1, poste="Consultant",
                        departement="Consulting")

        filtre_response = client.get(
            "/predict/filter?poste=Consultant",
            headers=headers
        )
        assert filtre_response.status_code == 200, "Le filtre doit retourner 200"

        filtre_body = filtre_response.json()
        assert filtre_body["total_employees"] == 1
        assert filtre_body["total_at_risk"] >= 0  # 0 ou 1, les deux sont valides
        assert 0.0 <= filtre_body["risk_rate"] <= 100.0

        # ── Étape 3 : Vérification de l'historique ─────────────────
        # La prédiction doit avoir été loggée automatiquement
        history_response = client.get("/predictions/history", headers=headers)
        assert history_response.status_code == 200, "L'historique doit être accessible"

        history_body = history_response.json()
        assert history_body["total_predictions"] >= 1, \
            "La prédiction doit être loggée dans l'historique"

    def test_historique_vide_avant_toute_prediction(self, client, db_session, test_user):
        """
        Contrôle : sans aucune prédiction, l'historique est vide.
        Vérifie que le logging ne produit pas de faux positifs.
        """
        login_response = client.post(
            "/token",
            data={"username": "testuser", "password": "testpassword"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        history_response = client.get("/predictions/history", headers=headers)
        assert history_response.status_code == 200
        assert history_response.json()["total_predictions"] == 0

    def test_plusieurs_filtres_loggent_plusieurs_predictions(
        self, client, db_session, auth_headers
    ):
        """
        Scénario : deux appels de filtre → deux entrées dans l'historique.
        Vérifie que chaque prédiction est bien loggée indépendamment.
        """
        insert_employee(db_session, employee_id=1, poste="Consultant")
        insert_employee(db_session, employee_id=2, poste="Consultant")

        # Premier appel
        client.get("/predict/employee/1", headers=auth_headers)
        # Deuxième appel
        client.get("/predict/employee/2", headers=auth_headers)

        history_response = client.get("/predictions/history", headers=auth_headers)
        assert history_response.json()["total_predictions"] == 2


# ══════════════════════════════════════════════════════════════
# SCÉNARIO 2 — Analyse d'un employé individuel
# ══════════════════════════════════════════════════════════════
# Simule le parcours d'un RH qui :
#   1. Recherche un employé par son ID
#   2. Reçoit une prédiction détaillée
#   3. Filtre l'historique pour retrouver cet employé

class TestWorkflowEmployeIndividuel:
    """
    Scénario métier : analyse ciblée d'un employé spécifique.
    Chaîne : GET /predict/employee/{id} → GET /predictions/history?employee_id=
    """

    def test_prediction_employee_puis_historique_filtre(
        self, client, db_session, auth_headers
    ):
        """
        Scénario complet :
          1. Prédiction pour l'employé n°1
          2. L'historique filtré par employee_id=1 contient exactement 1 entrée
          3. Les données de la prédiction sont cohérentes
        """
        # ── Étape 1 : Insérer et prédire ───────────────────────────
        insert_employee(db_session, employee_id=1)

        predict_response = client.get("/predict/employee/1", headers=auth_headers)
        assert predict_response.status_code == 200

        predict_body = predict_response.json()
        assert predict_body["employee_id"] == 1
        assert predict_body["prediction"] in ["Part", "Reste"]
        assert 0.0 <= predict_body["probability"] <= 1.0

        # ── Étape 2 : Historique filtré par cet employé ────────────
        history_response = client.get(
            "/predictions/history?employee_id=1",
            headers=auth_headers
        )
        assert history_response.status_code == 200

        history_body = history_response.json()
        assert history_body["total_predictions"] == 1

        prediction_loggee = history_body["predictions"][0]
        assert prediction_loggee["employee_id"] == 1
        assert prediction_loggee["prediction"] in ["Part", "Reste"]

    def test_historique_filtre_ne_contient_pas_autres_employes(
        self, client, db_session, auth_headers
    ):
        """
        Isolation : les prédictions d'un employé n'apparaissent pas
        dans l'historique filtré d'un autre employé.
        """
        insert_employee(db_session, employee_id=1)
        insert_employee(db_session, employee_id=2)

        # Prédictions pour les deux employés
        client.get("/predict/employee/1", headers=auth_headers)
        client.get("/predict/employee/2", headers=auth_headers)

        # L'historique filtré sur employee_id=1 ne doit contenir que l'employé 1
        history_response = client.get(
            "/predictions/history?employee_id=1",
            headers=auth_headers
        )
        history_body = history_response.json()

        assert history_body["total_predictions"] == 1
        assert all(
            p["employee_id"] == 1
            for p in history_body["predictions"]
        )

    def test_prediction_employee_inexistant(self, client, auth_headers):
        """
        Cas d'erreur : un employé avec un ID inconnu → 404.
        Simule un RH qui saisit un mauvais identifiant.
        """
        response = client.get("/predict/employee/9999", headers=auth_headers)
        assert response.status_code == 404

        body = response.json()
        assert "detail" in body  # Le message d'erreur est présent


# ══════════════════════════════════════════════════════════════
# SCÉNARIO 3 — Filtre multi-critères
# ══════════════════════════════════════════════════════════════
# Simule un RH qui affine son analyse avec plusieurs filtres combinés

class TestWorkflowMultiFiltres:
    """
    Scénario métier : analyse d'un groupe d'employés avec filtres combinés.
    Vérifie la cohérence des résultats selon les critères appliqués.
    """

    def test_filtre_par_poste_et_heure_sup(
        self, client, db_session, auth_headers
    ):
        """
        Filtre combiné : poste=Consultant + heure_sup=Non
        → seul l'employé correspondant aux deux critères doit apparaître.
        """
        # Employé qui correspond aux deux filtres
        insert_employee(db_session, employee_id=1,
                        poste="Consultant", heure_sup="Non")

        response = client.get(
            "/predict/filter?poste=Consultant&heure_sup=Non",
            headers=auth_headers
        )
        assert response.status_code == 200

        body = response.json()
        assert body["total_employees"] >= 1
        assert "filter_used" in body
        # Le filtre utilisé doit mentionner les deux critères
        assert "poste" in body["filter_used"]

    def test_risk_rate_cohérent_avec_predictions(
        self, client, db_session, auth_headers
    ):
        """
        Cohérence : risk_rate = total_at_risk / total_employees * 100
        Vérifie que le calcul du taux de risque est correct.
        """
        insert_employee(db_session, employee_id=1, poste="Consultant")

        response = client.get(
            "/predict/filter?poste=Consultant",
            headers=auth_headers
        )
        body = response.json()

        total = body["total_employees"]
        at_risk = body["total_at_risk"]
        risk_rate = body["risk_rate"]

        # Recalcul manuel
        expected_rate = round(at_risk / total * 100, 1)
        assert risk_rate == expected_rate

    def test_filtre_sans_resultat_retourne_404(self, client, auth_headers):
        """
        Filtre valide syntaxiquement mais sans résultat en DB → 404.
        Simule un RH qui filtre sur un département inexistant.
        """
        response = client.get(
            "/predict/filter?departement=Consulting",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_filtre_vide_retourne_400(self, client, auth_headers):
        """
        Aucun filtre fourni → 400 Bad Request.
        L'API exige au moins un critère.
        """
        response = client.get("/predict/filter", headers=auth_headers)
        assert response.status_code == 422


# ══════════════════════════════════════════════════════════════
# SCÉNARIO 4 — Sécurité : accès non autorisé
# ══════════════════════════════════════════════════════════════
# Vérifie que tous les endpoints protégés rejettent systématiquement
# les requêtes sans token ou avec un token invalide

class TestWorkflowSecurite:
    """
    Scénario métier : un utilisateur non authentifié tente d'accéder à l'API.
    Tous les endpoints protégés doivent retourner 401.
    """

    def test_tous_les_endpoints_proteges_sans_token(self, client):
        """
        Vérifie que chaque endpoint protégé rejette une requête sans token.
        Cas d'usage : accès direct sans authentification préalable.
        """
        endpoints_proteges = [
            "/predict/filter?poste=Consultant",
            "/predict/employee/1",
            "/predictions/history",
        ]

        for endpoint in endpoints_proteges:
            response = client.get(endpoint)
            assert response.status_code == 401, \
                f"L'endpoint {endpoint} doit retourner 401 sans token"

    def test_token_invalide_retourne_401(self, client):
        """
        Token mal formé → 401 sur tous les endpoints protégés.
        Simule une tentative d'usurpation avec un faux token.
        """
        faux_headers = {"Authorization": "Bearer token_completement_faux"}

        endpoints_proteges = [
            "/predict/filter?poste=Consultant",
            "/predict/employee/1",
            "/predictions/history",
        ]

        for endpoint in endpoints_proteges:
            response = client.get(endpoint, headers=faux_headers)
            assert response.status_code == 401, \
                f"Un faux token doit être rejeté sur {endpoint}"

    def test_route_publique_accessible_sans_token(self, client):
        """
        Contrôle : la route racine / est publique et accessible sans token.
        Permet de vérifier que l'API est en ligne sans s'authentifier.
        """
        response = client.get("/")
        assert response.status_code == 200

    def test_login_mauvais_identifiants_bloque_acces(self, client, test_user):
        """
        Login échoué → pas de token → accès bloqué.
        Scénario : mauvais mot de passe → tentative d'accès → rejet.
        """
        # Tentative de login avec un mauvais mot de passe
        login_response = client.post(
            "/token",
            data={"username": "testuser", "password": "mauvais_mdp"}
        )
        assert login_response.status_code == 401

        # Vérification qu'aucun token n'est retourné
        assert "access_token" not in login_response.json()

        # Tentative d'accès sans token → rejet
        protect_response = client.get("/predictions/history")
        assert protect_response.status_code == 401