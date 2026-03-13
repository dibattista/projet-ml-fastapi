"""
test_auth.py - Tests de l'authentification JWT
Projet P5 - Futurisys API Attrition

Fixtures utilisées depuis conftest.py :
- client       → TestClient FastAPI avec DB de test
- test_user    → utilisateur inséré en DB (username="testuser", password="testpassword")
- auth_headers → {"Authorization": "Bearer <token_valide>"}
"""

import pytest


# ══════════════════════════════════════════════════════════════
# 1. TESTS DU LOGIN (/token)
# ══════════════════════════════════════════════════════════════

class TestLogin:
    """Tests de l'endpoint POST /token"""

    def test_login_succes(self, client, test_user):
        """
        Cas nominal : bons identifiants → token reçu.
        Le endpoint /token attend un formulaire (OAuth2PasswordRequestForm),
        donc on envoie data= et non json=
        """
        response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "testpassword"
            }
        )
        assert response.status_code == 200

        body = response.json()
        assert "access_token" in body          # Le token est présent
        assert body["token_type"] == "bearer"  # Le type est correct
        assert len(body["access_token"]) > 0   # Le token n'est pas vide

    def test_login_mauvais_mot_de_passe(self, client, test_user):
        """
        Mauvais mot de passe → 401 Unauthorized.
        """
        response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "mauvais_mdp"
            }
        )
        assert response.status_code == 401
        assert "Identifiants incorrects" in response.json()["detail"]

    def test_login_utilisateur_inexistant(self, client):
        """
        Username qui n'existe pas en DB → 401 Unauthorized.
        Pas besoin de test_user ici (on teste l'absence d'utilisateur).
        """
        response = client.post(
            "/token",
            data={
                "username": "fantome",
                "password": "nimportequoi"
            }
        )
        assert response.status_code == 401

    def test_login_champs_vides(self, client):
        """
        Champs vides → erreur de validation (422 Unprocessable Entity).
        FastAPI valide automatiquement les champs requis du formulaire.
        """
        response = client.post("/token", data={})
        assert response.status_code == 422


# ══════════════════════════════════════════════════════════════
# 2. TESTS DE PROTECTION DES ROUTES
# ══════════════════════════════════════════════════════════════

class TestProtectionRoutes:
    """
    Vérifie que les routes protégées refusent les accès non authentifiés.
    On teste sur /predictions/history car elle ne nécessite pas de données ML.
    """

    def test_route_protegee_sans_token(self, client):
        """
        Appel sans token → 401 Unauthorized.
        """
        response = client.get("/predictions/history")
        assert response.status_code == 401

    def test_route_protegee_token_invalide(self, client):
        """
        Token mal formé → 401 Unauthorized.
        """
        headers = {"Authorization": "Bearer token_completement_faux"}
        response = client.get("/predictions/history", headers=headers)
        assert response.status_code == 401

    def test_route_protegee_token_valide(self, client, auth_headers):
        """
        Token valide → accès autorisé (200 ou autre code métier, mais pas 401).
        La table predictions est vide en test, donc on attend 200 avec liste vide.
        """
        response = client.get("/predictions/history", headers=auth_headers)
        assert response.status_code == 200

    def test_route_publique_sans_token(self, client):
        """
        La route racine / est publique → accessible sans token.
        """
        response = client.get("/")
        assert response.status_code == 200


# ══════════════════════════════════════════════════════════════
# 3. TEST DU TOKEN LUI-MÊME
# ══════════════════════════════════════════════════════════════

class TestToken:
    """Vérifie la structure et l'utilisation du token JWT."""

    def test_token_utilisable_apres_login(self, client, test_user):
        """
        Scénario complet : login → récupère token → utilise le token.
        Simule le workflow réel d'un utilisateur.
        """
        # Étape 1 : Login
        login_response = client.post(
            "/token",
            data={"username": "testuser", "password": "testpassword"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Étape 2 : Utilisation du token sur une route protégée
        headers = {"Authorization": f"Bearer {token}"}
        protected_response = client.get("/predictions/history", headers=headers)
        assert protected_response.status_code == 200