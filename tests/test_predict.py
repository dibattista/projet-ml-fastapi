"""
test_predict.py - Tests des fonctions ML (encodage + prédiction)
Projet P5 - Futurisys API Attrition

On teste les fonctions Python pures de app/predict.py :
- encode_employee_data() → transforme les données DB en features ML
- predict_employees()    → retourne les prédictions avec probabilités

Pas besoin de DB ni de token ici → on construit des DataFrames à la main.
"""

import pytest
import pandas as pd
import numpy as np

from app.predict import encode_employee_data, predict_employees


# ══════════════════════════════════════════════════════════════
# DONNÉES DE TEST RÉUTILISABLES
# ══════════════════════════════════════════════════════════════

def make_employee_df(**kwargs):
    """
    Construit un DataFrame minimal valide (1 employé).
    Reproduit la structure de la jointure sirh + evaluation + sondage.
    kwargs permet de surcharger des valeurs pour tester des cas spécifiques.

    Exemple :
        make_employee_df(genre="F", heure_supplementaires="Oui")
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

        # ── CLÉS DE JOINTURE (présentes dans le SELECT *) ──
        "eval_number": 1,
        "code_sondage": 1,
    }
    data.update(kwargs)  # Surcharge les valeurs si besoin
    return pd.DataFrame([data])


# ══════════════════════════════════════════════════════════════
# 1. TESTS DE encode_employee_data()
# ══════════════════════════════════════════════════════════════

class TestEncodeEmployeeData:
    """Tests de la fonction d'encodage des données employés."""

    def test_encodage_genre_homme(self):
        """Genre M → genre_encoded = 0"""
        df = make_employee_df(genre="M")
        result = encode_employee_data(df)
        assert result["genre_encoded"].iloc[0] == 0

    def test_encodage_genre_femme(self):
        """Genre F → genre_encoded = 1"""
        df = make_employee_df(genre="F")
        result = encode_employee_data(df)
        assert result["genre_encoded"].iloc[0] == 1

    def test_encodage_heure_sup_non(self):
        """Heures sup Non → heure_supp_encoded = 0"""
        df = make_employee_df(heure_supplementaires="Non")
        result = encode_employee_data(df)
        assert result["heure_supp_encoded"].iloc[0] == 0

    def test_encodage_heure_sup_oui(self):
        """Heures sup Oui → heure_supp_encoded = 1"""
        df = make_employee_df(heure_supplementaires="Oui")
        result = encode_employee_data(df)
        assert result["heure_supp_encoded"].iloc[0] == 1

    def test_encodage_deplacement_aucun(self):
        """Déplacement Aucun → frequence_deplacement_encoded = 0"""
        df = make_employee_df(frequence_deplacement="Aucun")
        result = encode_employee_data(df)
        assert result["frequence_deplacement_encoded"].iloc[0] == 0

    def test_encodage_deplacement_occasionnel(self):
        """Déplacement Occasionnel → frequence_deplacement_encoded = 1"""
        df = make_employee_df(frequence_deplacement="Occasionnel")
        result = encode_employee_data(df)
        assert result["frequence_deplacement_encoded"].iloc[0] == 1

    def test_encodage_deplacement_frequent(self):
        """Déplacement Frequent → frequence_deplacement_encoded = 2"""
        df = make_employee_df(frequence_deplacement="Frequent")
        result = encode_employee_data(df)
        assert result["frequence_deplacement_encoded"].iloc[0] == 2

    def test_conversion_augmentation_salaire(self):
        """'15 %' → augmentation_num = 15"""
        df = make_employee_df(augementation_salaire_precedente="15 %")
        result = encode_employee_data(df)
        assert result["augmentation_num"].iloc[0] == 15

    def test_colonnes_originales_supprimees(self):
        """
        Les colonnes texte originales doivent être supprimées
        après encodage (remplacées par les colonnes _encoded).
        """
        df = make_employee_df()
        result = encode_employee_data(df)

        # Ces colonnes ne doivent plus exister
        cols_supprimees = [
            "genre",
            "heure_supplementaires",
            "frequence_deplacement",
            "augementation_salaire_precedente",
            "a_quitte_l_entreprise",   # variable cible, pas une feature
            "departement",             # multicolinéarité avec poste
            "ayant_enfants",           # valeur unique
            "eval_number",             # clé de jointure en doublon
            "code_sondage",            # clé de jointure en doublon
        ]
        for col in cols_supprimees:
            assert col not in result.columns, f"'{col}' aurait dû être supprimée"

    def test_colonnes_encodees_presentes(self):
        """Les nouvelles colonnes encodées doivent être présentes."""
        df = make_employee_df()
        result = encode_employee_data(df)

        cols_attendues = [
            "genre_encoded",
            "heure_supp_encoded",
            "frequence_deplacement_encoded",
            "augmentation_num",
        ]
        for col in cols_attendues:
            assert col in result.columns, f"'{col}' manquante après encodage"

    def test_encodage_plusieurs_employes(self):
        """L'encodage doit fonctionner sur plusieurs lignes."""
        df = pd.concat([
            make_employee_df(id_employee=1, genre="M"),
            make_employee_df(id_employee=2, genre="F"),
        ], ignore_index=True)

        result = encode_employee_data(df)
        assert len(result) == 2
        assert result["genre_encoded"].iloc[0] == 0
        assert result["genre_encoded"].iloc[1] == 1


# ══════════════════════════════════════════════════════════════
# 2. TESTS DE predict_employees()
# ══════════════════════════════════════════════════════════════

class TestPredictEmployees:
    """
    Tests de la fonction de prédiction.
    On encode d'abord les données puis on prédit.
    """

    def get_encoded_df(self, **kwargs):
        """Helper : encode un employé prêt pour la prédiction."""
        df = make_employee_df(**kwargs)
        return encode_employee_data(df)

    def test_retourne_colonnes_attendues(self):
        """Le résultat doit contenir les 4 colonnes de sortie."""
        df_encoded = self.get_encoded_df()
        result = predict_employees(df_encoded)

        colonnes_attendues = ["employee_id", "prediction", "probability", "risk_level"]
        for col in colonnes_attendues:
            assert col in result.columns, f"Colonne '{col}' manquante"

    def test_prediction_valeur_valide(self):
        """La prédiction doit être 'Part' ou 'Reste' uniquement."""
        df_encoded = self.get_encoded_df()
        result = predict_employees(df_encoded)

        valeurs_valides = {"Part", "Reste"}
        for pred in result["prediction"]:
            assert pred in valeurs_valides, f"Valeur inattendue : {pred}"

    def test_probabilite_entre_0_et_1(self):
        """La probabilité doit être entre 0 et 1."""
        df_encoded = self.get_encoded_df()
        result = predict_employees(df_encoded)

        for prob in result["probability"]:
            assert 0.0 <= prob <= 1.0, f"Probabilité hors bornes : {prob}"

    def test_risk_level_valide(self):
        """Le niveau de risque doit être dans les 4 catégories définies."""
        df_encoded = self.get_encoded_df()
        result = predict_employees(df_encoded)

        niveaux_valides = {"Faible", "Modéré", "Élevé", "Critique"}
        for niveau in result["risk_level"]:
            assert str(niveau) in niveaux_valides, f"Niveau inattendu : {niveau}"

    def test_employee_id_conserve(self):
        """L'id_employee doit être conservé dans le résultat."""
        df_encoded = self.get_encoded_df(id_employee=42)
        result = predict_employees(df_encoded)

        assert result["employee_id"].iloc[0] == 42

    def test_prediction_plusieurs_employes(self):
        """La prédiction doit fonctionner sur plusieurs employés."""
        df1 = make_employee_df(id_employee=1)
        df2 = make_employee_df(id_employee=2)
        df = pd.concat([df1, df2], ignore_index=True)
        df_encoded = encode_employee_data(df)

        result = predict_employees(df_encoded)
        assert len(result) == 2