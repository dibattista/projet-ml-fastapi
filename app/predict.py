import joblib
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text

# 1 - Chargement du modèle une seule fois au démarrage
model = joblib.load("ml_model/model_pipeline.pkl")


# 2 — Jointure des 3 tables sources
def get_employee_dataframe(db: Session, filters: dict = None, employee_id: int = None) -> pd.DataFrame:
    """
    Lit sirh + evaluation + sondage, fait la jointure,
    et retourne un DataFrame prêt pour l'encodage.
    """
    query = """
        SELECT s.*, e.*, so.*
        FROM sirh s
        JOIN evaluation e ON s.id_employee = e.eval_number
        JOIN sondage so ON s.id_employee = so.code_sondage
    """

    params = {}

    # Filtre par employé unique
    if employee_id is not None:
        query += " WHERE s.id_employee = :employee_id"
        params["employee_id"] = employee_id

    # Filtres dynamiques (ex: poste=Consultant)
    elif filters:
        conditions = []
        for key, value in filters.items():
            conditions.append(f"s.{key} = :{key}")
            params[key] = value
        query += " WHERE " + " AND ".join(conditions)

    result = db.execute(text(query), params)
    columns = result.keys()
    rows = result.fetchall()

    return pd.DataFrame(rows, columns=columns)


# 3 — Encodage des variables manuelles
def encode_employee_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme les données lisibles (DB) en format attendu par le pipeline.
    Reproduit les encodages manuels du notebook P4.
    """
    df = df.copy()

    # Encodage binaire
    df["genre_encoded"] = df["genre"].map({"M": 0, "F": 1})
    df["heure_supp_encoded"] = df["heure_supplementaires"].map({"Non": 0, "Oui": 1})

    # Encodage ordinal
    df["frequence_deplacement_encoded"] = df["frequence_deplacement"].map({
        "Aucun": 0, "Occasionnel": 1, "Frequent": 2
    })

    # Conversion pourcentage → numérique
    if "augementation_salaire_precedente" in df.columns:
        df["augmentation_num"] = (
            df["augementation_salaire_precedente"]
            .str.replace(" %", "", regex=False)
            .astype(int)
        )

    # Supprimer les colonnes originales (remplacées par les encodées)
    cols_a_supprimer = [
        "genre", "heure_supplementaires",
        "frequence_deplacement", "augementation_salaire_precedente",
        # Clés de jointure en doublon
        "eval_number", "code_sondage",
        # Colonnes non-features
        "a_quitte_l_entreprise",
        "departement",      # multicolinéarité avec poste (P4)
        "ayant_enfants",    # valeur unique (P4)
    ]
    df = df.drop(columns=[c for c in cols_a_supprimer if c in df.columns])

    return df


# 4 — Prédiction
def predict_employees(df_encoded: pd.DataFrame) -> pd.DataFrame:
    """
    Fait la prédiction sur les employés encodés.
    Retourne le DataFrame avec prediction + probability.
    """
    # Sauvegarder id_employee avant de le retirer pour le modèle
    ids = df_encoded["id_employee"].values
    df_model = df_encoded.drop(columns=["id_employee"])

    # Prédiction + probabilité
    predictions = model.predict(df_model)
    probabilities = model.predict_proba(df_model)[:, 1]  # proba de "Part"

    # Construire le résultat
    results = pd.DataFrame({
        "employee_id": ids,
        "prediction": ["Part" if p == 1 else "Reste" for p in predictions],
        "probability": probabilities,
        "risk_level": pd.cut(
            probabilities,
            bins=[0, 0.3, 0.5, 0.7, 1.0],
            labels=["Faible", "Modéré", "Élevé", "Critique"]
        )
    })

    return results


# 5 — Logger dans la table predictions
def log_predictions(db: Session, results: pd.DataFrame, filter_used: str = None):
    """Enregistre les prédictions dans la table predictions."""
    for _, row in results.iterrows():
        db.execute(
            text("""
                INSERT INTO predictions (employee_id, prediction, probability, risk_level, filter_used)
                VALUES (:employee_id, :prediction, :probability, :risk_level, :filter_used)
            """),
            {
                "employee_id": int(row["employee_id"]),
                "prediction": row["prediction"],
                "probability": float(row["probability"]),
                "risk_level": str(row["risk_level"]),
                "filter_used": filter_used
            }
        )
    db.commit()