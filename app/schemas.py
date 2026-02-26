from pydantic import BaseModel

class EmployeeFeatures(BaseModel):
    """Données reçues par l'API (envoyées par l'utilisateur)"""
    employee_id: int
    heure_supp_encoded: int
    nombre_participation_pee: int
    age: int
    annees_sous_responsable_actuel: int
    annees_dans_l_entreprise: int
    revenu_mensuel: int
    annee_experience_totale: int
    feat_junior_poste_risque: int
    distance_domicile_travail: int
    satisfaction_employee_environnement: int
    annees_dans_le_poste_actuel: int
    nombre_experiences_precedentes: int

class PredictionResponse(BaseModel):
    """Données retournées par l'API après prédiction"""
    prediction: int        # Résultat : 0 = employé stable, 1 = risque de départ
    probability: float     # Probabilité de départ (entre 0 et 1)
    message: str           # Message lisible expliquant le résultat