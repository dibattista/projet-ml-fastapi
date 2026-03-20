"""
test_functional.py - Tests fonctionnels
Projet P5 - Futurisys API Attrition

Trois familles de tests :

1. TestBiaisGenreStatutMarital
   → Qualité du modèle : pas de discrimination sur genre/statut marital

2. TestImpactHeuresSup
   → Comportement du modèle : réagit-il au signal le plus fort ?
   → Seuil de 0.02 fondé sur l'analyse SHAP du P4

3. TestScenarioUtilisateur
   → Scénarios complets du point de vue du RH qui utilise l'API
   → Enchaînement d'actions : login → filtre → historique
"""

import pytest
import pandas as pd
from conftest import insert_employee

from app.predict import encode_employee_data, predict_employees


# ══════════════════════════════════════════════════════════════
# HELPER PARTAGÉ (tests sans DB)
# ══════════════════════════════════════════════════════════════

def make_employee_df(**kwargs):
    """
    Construit un DataFrame minimal valide (1 employé).
    Reproduit la structure de la jointure sirh + evaluation + sondage.
    kwargs permet de surcharger des valeurs pour tester des cas spécifiques.
    """
    data = {
        # ── SIRH ──
        "id_employee": 1,
        "age": 30,
        "genre": "M",
        "revenu_mensuel": 5000,
        "statut_marital": "Celibataire",
        "departement": "Consulting",
        "poste": "Consultant",
        "nombre_experiences_precedentes": 2,
        "nombre_heures_travailless": 40,
        "annee_experience_totale": 5,
        "annees_dans_l_entreprise": 3,
        "annees_dans_le_poste_actuel": 2,

        # ── EVALUATION ──
        "satisfaction_employee_environnement": 3,
        "note_evaluation_precedente": 3,
        "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_equipe": 3,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "note_evaluation_actuelle": 3,
        "heure_supplementaires": "Non",
        "augementation_salaire_precedente": "10 %",

        # ── SONDAGE ──
        "a_quitte_l_entreprise": "Non",
        "nombre_participation_pee": 2,
        "nb_formations_suivies": 2,
        "nombre_employee_sous_responsabilite": 0,
        "distance_domicile_travail": 10,
        "niveau_education": 3,
        "domaine_etude": "Informatique",
        "ayant_enfants": "Y",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 1,
        "annes_sous_responsable_actuel": 2,

        # ── CLÉS DE JOINTURE ──
        "eval_number": 1,
        "code_sondage": 1,
    }
    data.update(kwargs)
    return pd.DataFrame([data])


def get_probability(df: pd.DataFrame) -> float:
    """
    Helper : encode + prédit et retourne la probabilité de départ (float).
    """
    df_encoded = encode_employee_data(df)
    result = predict_employees(df_encoded)
    return float(result["probability"].iloc[0])


# ══════════════════════════════════════════════════════════════
# FAMILLE 1 - BIAIS GENRE ET STATUT MARITAL
# ══════════════════════════════════════════════════════════════

class TestBiaisGenreStatutMarital:
    """
    Vérifie que le modèle ne produit pas de biais significatif
    sur les variables démographiques genre et statut_marital.

    Principe : deux profils identiques sur tout sauf genre (ou statut_marital)
    doivent obtenir des probabilités de départ très proches (delta < 0.05).

    Seuil choisi : 0.05 (5 points de %), cohérent avec les valeurs SHAP
    du P4 où statut_marital contribue ~0.01 et genre ~0.0 à la prédiction.
    """

    SEUIL_BIAIS = 0.05

    # ── Tests sur le genre ──

    def test_genre_meme_proba_profil_standard(self):
        """
        Profil standard : seul le genre change (M → F).
        La différence de probabilité doit être < 0.05.
        """
        df_homme = make_employee_df(genre="M")
        df_femme = make_employee_df(genre="F")

        prob_h = get_probability(df_homme)
        prob_f = get_probability(df_femme)
        delta = abs(prob_h - prob_f)

        assert delta < self.SEUIL_BIAIS, (
            f"Biais genre détecté : delta={delta:.4f} "
            f"(H={prob_h:.3f}, F={prob_f:.3f})"
        )

    def test_genre_meme_proba_profil_heure_sup(self):
        """
        Profil avec heures sup : seul le genre change.
        Le biais genre ne doit pas être amplifié par cette combinaison.
        """
        df_homme = make_employee_df(genre="M", heure_supplementaires="Oui")
        df_femme = make_employee_df(genre="F", heure_supplementaires="Oui")

        prob_h = get_probability(df_homme)
        prob_f = get_probability(df_femme)
        delta = abs(prob_h - prob_f)

        assert delta < self.SEUIL_BIAIS, (
            f"Biais genre (heure sup Oui) détecté : delta={delta:.4f} "
            f"(H={prob_h:.3f}, F={prob_f:.3f})"
        )

    def test_genre_meme_proba_profil_commercial(self):
        """
        Poste commercial (à risque) : seul le genre change.
        """
        df_homme = make_employee_df(
            genre="M",
            poste="Représentant Commercial",
            annee_experience_totale=4,
        )
        df_femme = make_employee_df(
            genre="F",
            poste="Représentant Commercial",
            annee_experience_totale=4,
        )

        prob_h = get_probability(df_homme)
        prob_f = get_probability(df_femme)
        delta = abs(prob_h - prob_f)

        assert delta < self.SEUIL_BIAIS, (
            f"Biais genre (poste à risque) détecté : delta={delta:.4f} "
            f"(H={prob_h:.3f}, F={prob_f:.3f})"
        )

    # ── Tests sur le statut marital ──

    def test_statut_marital_meme_proba_celibataire_vs_marie(self):
        """
        Profil standard : seul le statut marital change.
        Célibataire vs Marié(e) → delta < 0.05.
        """
        df_celibataire = make_employee_df(statut_marital="Celibataire")
        df_marie = make_employee_df(statut_marital="Marié(e)")

        prob_c = get_probability(df_celibataire)
        prob_m = get_probability(df_marie)
        delta = abs(prob_c - prob_m)

        assert delta < self.SEUIL_BIAIS, (
            f"Biais statut marital détecté : delta={delta:.4f} "
            f"(Célibataire={prob_c:.3f}, Marié(e)={prob_m:.3f})"
        )

    def test_statut_marital_meme_proba_celibataire_vs_divorce(self):
        """
        Profil standard : Célibataire vs Divorcé(e) → delta < 0.05.
        """
        df_celibataire = make_employee_df(statut_marital="Celibataire")
        df_divorce = make_employee_df(statut_marital="Divorcé(e)")

        prob_c = get_probability(df_celibataire)
        prob_d = get_probability(df_divorce)
        delta = abs(prob_c - prob_d)

        assert delta < self.SEUIL_BIAIS, (
            f"Biais statut marital détecté : delta={delta:.4f} "
            f"(Célibataire={prob_c:.3f}, Divorcé(e)={prob_d:.3f})"
        )

    def test_statut_marital_meme_proba_profil_heure_sup(self):
        """
        Profil avec heures sup : seul le statut marital change.
        Vérifie qu'il n'y a pas d'interaction amplificatrice.
        """
        df_celibataire = make_employee_df(
            statut_marital="Celibataire",
            heure_supplementaires="Oui",
        )
        df_marie = make_employee_df(
            statut_marital="Marié(e)",
            heure_supplementaires="Oui",
        )

        prob_c = get_probability(df_celibataire)
        prob_m = get_probability(df_marie)
        delta = abs(prob_c - prob_m)

        assert delta < self.SEUIL_BIAIS, (
            f"Biais statut marital (heure sup Oui) détecté : delta={delta:.4f} "
            f"(Célibataire={prob_c:.3f}, Marié(e)={prob_m:.3f})"
        )


# ══════════════════════════════════════════════════════════════
# FAMILLE 2 - IMPACT DES HEURES SUPPLÉMENTAIRES
# ══════════════════════════════════════════════════════════════

class TestImpactHeuresSup:
    """
    Vérifie que le modèle réagit correctement aux heures supplémentaires.

    Fondé sur l'analyse SHAP du P4 :
    - heure_supp_encoded est la variable n°1 du modèle
    - Contribution observée : +0.03 pour les employés qui partent
    - Seuil de 0.02 choisi comme minimum raisonnable issu de cette analyse
    """

    def test_heure_sup_augmente_probabilite(self):
        """
        Un employé avec heures sup doit avoir une probabilité de départ
        plus élevée que le même profil sans heures sup.
        Direction ET magnitude fondées sur les SHAP du P4 (contribution ~+0.03).
        """
        df_avec = make_employee_df(heure_supplementaires="Oui")
        df_sans = make_employee_df(heure_supplementaires="Non")

        prob_avec = get_probability(df_avec)
        prob_sans = get_probability(df_sans)

        # Direction : heure sup doit augmenter la proba
        assert prob_avec > prob_sans, (
            f"Les heures sup devraient augmenter la proba de départ "
            f"(avec={prob_avec:.3f}, sans={prob_sans:.3f})"
        )

        # Magnitude : l'écart doit être significatif (fondé sur SHAP P4)
        assert (prob_avec - prob_sans) > 0.02, (
            f"Impact trop faible : delta={prob_avec - prob_sans:.4f} "
            f"(attendu > 0.02 selon analyse SHAP P4)"
        )


# ══════════════════════════════════════════════════════════════
# FAMILLE 3 - SCÉNARIOS UTILISATEUR (RH)
# ══════════════════════════════════════════════════════════════

class TestScenarioUtilisateur:
    """
    Scénarios complets du point de vue du RH qui utilise l'API.

    On ne teste pas des endpoints isolément (c'est le rôle de test_routes.py),
    on teste des enchaînements d'actions réalistes :
    - Un RH se connecte, filtre, consulte l'historique
    - Un RH cherche un employé spécifique et obtient sa fiche complète
    """

    def test_scenario_login_puis_filtre_heure_sup(self, client, db_session, auth_headers):
        """
        Scénario : le RH veut voir les employés à risque sur un poste donné.

        Étapes :
        1. Le RH est connecté (token dans auth_headers)
        2. Il filtre sur poste=Consultant
        3. Il obtient une liste de prédictions avec tous les champs métier
        """
        insert_employee(db_session, employee_id=1)

        response = client.get(
            "/predict/filter?poste=Consultant",
            headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()

        assert body["total_employees"] >= 1
        assert "predictions" in body
        assert "risk_rate" in body
        assert len(body["predictions"]) > 0

    def test_scenario_login_puis_filtre_puis_historique(self, client, db_session, auth_headers):
        """
        Scénario complet : login → filtre → vérification dans l'historique.

        Étapes :
        1. Le RH est connecté
        2. Il filtre sur poste=Consultant → prédictions loggées automatiquement
        3. Il consulte l'historique → ses prédictions sont bien enregistrées
        """
        insert_employee(db_session, employee_id=1)

        # Étape 2 : filtre
        client.get("/predict/filter?poste=Consultant", headers=auth_headers)

        # Étape 3 : historique → doit contenir la prédiction précédente
        response = client.get("/predictions/history", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["total_predictions"] >= 1

    def test_scenario_fiche_employe_complete(self, client, db_session, auth_headers):
        """
        Scénario : le RH veut la fiche complète d'un employé spécifique.

        Étapes :
        1. Le RH est connecté
        2. Il demande l'employé 1
        3. Il obtient tous les champs : id, prédiction, probabilité, niveau de risque
        """
        insert_employee(db_session, employee_id=1)

        response = client.get("/predict/employee/1", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()

        # Tous les champs métier sont présents
        assert "employee_id" in body
        assert "prediction" in body
        assert "probability" in body
        assert "risk_level" in body

        # Les valeurs sont cohérentes
        assert body["prediction"] in ["Part", "Reste"]
        assert 0.0 <= body["probability"] <= 1.0

    def test_scenario_sans_connexion_acces_refuse(self, client):
        """
        Scénario : un utilisateur non connecté tente d'accéder aux prédictions.

        Étapes :
        1. Pas de token
        2. Il tente de filtrer → accès refusé 401
        """
        response = client.get("/predict/filter?poste=Consultant")
        assert response.status_code == 401