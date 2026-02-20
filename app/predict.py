import joblib
import pandas as pd
from sqlalchemy.orm import Session
from database.create_db import Prediction  # le modèle SQLAlchemy de ta table predictions

# Chargement du modèle une seule fois au démarrage
model = joblib.load("ml_model/model_pipeline.pkl")

def run_prediction(features: dict, db: Session):
    # On récupère et retire l'employee_id (pas une feature du modèle)
    employee_id = features.pop("employee_id")

    # Création du DataFrame pour le modèle
    df = pd.DataFrame([features])

    # Prédiction
    pred = int(model.predict(df)[0])
    proba = float(model.predict_proba(df)[0][1])

    # Sauvegarde en base de données
    record = Prediction(
        employee_id=employee_id,
        prediction=pred,
        probability=proba,
        heure_supp_encoded=features["heure_supp_encoded"],
        nombre_participation_pee=features["nombre_participation_pee"],
        age=features["age"],
        annees_sous_responsable_actuel=features["annees_sous_responsable_actuel"],
        annees_dans_l_entreprise=features["annees_dans_l_entreprise"],
        revenu_mensuel=features["revenu_mensuel"],
        annee_experience_totale=features["annee_experience_totale"],
        feat_junior_poste_risque=features["feat_junior_poste_risque"],
        distance_domicile_travail=features["distance_domicile_travail"],
        satisfaction_employee_environnement=features["satisfaction_employee_environnement"],
        annees_dans_le_poste_actuel=features["annees_dans_le_poste_actuel"],
        nombre_experiences_precedentes=features["nombre_experiences_precedentes"]
    )
    db.add(record)
    db.commit()

    return pred, proba