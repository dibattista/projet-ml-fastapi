"""
test_features.py - Tests unitaires des features engineerées
Projet P5 - Futurisys API Attrition

On teste les fonctions de app/features.py :
- creer_features() → calcule les flags métier (0 ou 1)

Ces features ont été créées dans le P4 pour aider le modèle à mieux prédire.
Pas de DB, pas de token, pas de modèle → uniquement creer_features().

Deux familles :
1. TestJobChangingFeature    → flag job_changing (profil instable)
2. TestJuniorPosteRisque     → flag feat_junior_poste_risque (junior à risque)
"""

import pytest
import pandas as pd

from app.features import creer_features, FEATURES_CONFIG


# ══════════════════════════════════════════════════════════════
# HELPER PARTAGÉ
# ══════════════════════════════════════════════════════════════

def make_employee_df(**kwargs):
    """
    Construit un DataFrame minimal valide (1 employé).
    Reproduit la structure attendue par creer_features().
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


# ══════════════════════════════════════════════════════════════
# FAMILLE 1 - job_changing
# ══════════════════════════════════════════════════════════════

class TestJobChangingFeature:
    """
    Vérifie que creer_features() calcule correctement le flag job_changing.

    Règle métier (features.py) :
        job_changing = 1  si  nombre_experiences_precedentes >= 4
                              ET annee_experience_totale <= 6
        job_changing = 0  sinon

    Hypothèse P4 : profil instable = beaucoup d'expériences en peu de temps.
    """

    def test_flag_actif(self):
        """
        Les 2 conditions sont remplies → job_changing = 1.
        nb_exp=5 (>= 4) ET annee_exp=4 (<= 6)
        """
        df = make_employee_df(
            nombre_experiences_precedentes=5,
            annee_experience_totale=4,
        )
        df_feat, _ = creer_features(df, FEATURES_CONFIG)
        assert df_feat["job_changing"].iloc[0] == 1

    def test_flag_inactif_annee_exp_trop_elevee(self):
        """
        annee_experience_totale > 6 → job_changing = 0.
        nb_exp=5 (>= 4) MAIS annee_exp=10 (> 6)
        """
        df = make_employee_df(
            nombre_experiences_precedentes=5,
            annee_experience_totale=10,
        )
        df_feat, _ = creer_features(df, FEATURES_CONFIG)
        assert df_feat["job_changing"].iloc[0] == 0

    def test_flag_inactif_nb_exp_insuffisant(self):
        """
        nombre_experiences_precedentes < 4 → job_changing = 0.
        nb_exp=2 (< 4) même si annee_exp=4 (<= 6)
        """
        df = make_employee_df(
            nombre_experiences_precedentes=2,
            annee_experience_totale=4,
        )
        df_feat, _ = creer_features(df, FEATURES_CONFIG)
        assert df_feat["job_changing"].iloc[0] == 0

    def test_seuil_exact_inclusif(self):
        """
        Seuil exact : nb_exp=4 ET annee_exp=6 → flag = 1.
        Valide que >= et <= sont bien inclusifs (pas > et <).
        """
        df = make_employee_df(
            nombre_experiences_precedentes=4,
            annee_experience_totale=6,
        )
        df_feat, _ = creer_features(df, FEATURES_CONFIG)
        assert df_feat["job_changing"].iloc[0] == 1


# ══════════════════════════════════════════════════════════════
# FAMILLE 2 - feat_junior_poste_risque
# ══════════════════════════════════════════════════════════════

class TestJuniorPosteRisque:
    """
    Vérifie que creer_features() calcule correctement le flag feat_junior_poste_risque.

    Règle métier (features.py) :
        feat_junior_poste_risque = 1  si  poste in postes_risque
                                          ET annee_experience_totale <= 7
        postes_risque = ['Représentant Commercial', 'Cadre Commercial', 'Consultant']

    Hypothèse P4 : les juniors dans des postes à forte pression partent plus.
    """

    def test_flag_actif_consultant_junior(self):
        """
        Consultant + annee_exp <= 7 → flag = 1.
        """
        df = make_employee_df(
            poste="Consultant",
            annee_experience_totale=5,
        )
        df_feat, _ = creer_features(df, FEATURES_CONFIG)
        assert df_feat["feat_junior_poste_risque"].iloc[0] == 1

    def test_flag_actif_representant_junior(self):
        """
        Représentant Commercial + annee_exp <= 7 → flag = 1.
        """
        df = make_employee_df(
            poste="Représentant Commercial",
            annee_experience_totale=3,
        )
        df_feat, _ = creer_features(df, FEATURES_CONFIG)
        assert df_feat["feat_junior_poste_risque"].iloc[0] == 1

    def test_flag_inactif_poste_risque_senior(self):
        """
        Consultant MAIS annee_exp > 7 → flag = 0.
        Le poste est à risque mais le profil n'est plus junior.
        """
        df = make_employee_df(
            poste="Consultant",
            annee_experience_totale=12,
        )
        df_feat, _ = creer_features(df, FEATURES_CONFIG)
        assert df_feat["feat_junior_poste_risque"].iloc[0] == 0

    def test_flag_inactif_poste_non_risque_junior(self):
        """
        Poste hors liste + annee_exp <= 7 → flag = 0.
        Profil junior mais dans un poste non identifié comme à risque.
        """
        df = make_employee_df(
            poste="Technicien",
            annee_experience_totale=4,
        )
        df_feat, _ = creer_features(df, FEATURES_CONFIG)
        assert df_feat["feat_junior_poste_risque"].iloc[0] == 0

    def test_seuil_exact_7_ans_inclusif(self):
        """
        Seuil exact : annee_exp=7 → flag = 1.
        Valide que <= est bien inclusif (pas <).
        """
        df = make_employee_df(
            poste="Consultant",
            annee_experience_totale=7,
        )
        df_feat, _ = creer_features(df, FEATURES_CONFIG)
        assert df_feat["feat_junior_poste_risque"].iloc[0] == 1