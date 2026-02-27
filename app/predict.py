import joblib
import pandas as pd
from sqlalchemy.orm import Session
from database.create_db import Employee, Prediction

# 1 - Chargement du modèle une seule fois au démarrage
model = joblib.load("ml_model/model_pipeline.pkl")

# 2 — La fonction d'encodage des variables manuelles :
def encode_employee_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transforme les données lisibles en format attendu par le modèle."""
    df = df.copy()

    # Encodage binaire
    df["heure_supp_encoded"] = df["heure_supplementaires"].map({"Oui": 1, "Non": 0})
    df["genre"] = df["genre"].map({"Homme": 0, "Femme": 1})

    # Encodage ordinal
    df["frequence_deplacement_encoded"] = df["frequence_deplacement"].map({
        "Aucun": 0, "Occasionnel": 1, "Frequent": 2
    })

    # Conversion pourcentage → numérique
    # (si augmentation_num est encore en string "15 %")
    if df["augmentation_num"].dtype == object:
        df["augmentation_num"] = df["augmentation_num"].astype(int)

    return df

# 3 — Le calcul des features engineered (celles créées en P4) :
def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les features métier créées dans le Projet 4."""
    df = df.copy()

    # Junior dans un poste à risque
    df["feat_junior_poste_risque"] = (
        (df["annee_experience_totale"] <= 7) &
        (df["poste"].isin(["Représentant Commercial", "Consultant", "Tech Lead"]))
    ).astype(int)

    # Commercial avec grande distance domicile
    df["feat_commercial_distance"] = (
        (df["poste"].str.contains("Commercial", na=False)) &
        (df["distance_domicile_travail"] > 20)
    ).astype(int)

    # Job hopping (change souvent de job)
    df["job_changing"] = (
        (df["nombre_experiences_precedentes"] >= 4) &
        (df["annee_experience_totale"] <= 7)
    ).astype(int)

    return df