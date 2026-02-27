import joblib
import pandas as pd
from sqlalchemy.orm import Session
from database.create_db import Employee, Prediction

# 1 - Chargement du modèle une seule fois au démarrage
model = joblib.load("ml_model/model_pipeline.pkl")


# 2 — Encodage des variables manuelles
def encode_employee_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme les données lisibles (DB) en format attendu par le pipeline.
    Reproduit les encodages manuels du notebook P4.
    """
    df = df.copy()

    # Encodage binaire (identique au notebook)
    df["genre_encoded"] = df["genre"].map({"M": 0, "F": 1})
    df["heure_supp_encoded"] = df["heure_supplementaires"].map({"Non": 0, "Oui": 1})

    # Encodage ordinal
    df["frequence_deplacement_encoded"] = df["frequence_deplacement"].map({
        "Aucun": 0, "Occasionnel": 1, "Frequent": 2
    })

    # Conversion pourcentage → numérique
    if "augmentation_salaire_precedente" in df.columns:
        df["augmentation_num"] = (
            df["augmentation_salaire_precedente"]
            .str.replace(" %", "", regex=False)
            .astype(int)
        )

    # Supprimer les colonnes originales (remplacées par les encodées)
    cols_originales = [
        "genre", "heure_supplementaires",
        "frequence_deplacement", "augmentation_salaire_precedente"
    ]
    df = df.drop(columns=[c for c in cols_originales if c in df.columns])

    # Supprimer les colonnes non-features
    cols_non_features = ["id", "id_employee", "a_quitte_l_entreprise"]
    df = df.drop(columns=[c for c in cols_non_features if c in df.columns])

    return df