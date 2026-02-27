from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ─── Réponse pour UNE prédiction ───
class PredictionResult(BaseModel):
    employee_id: int
    prediction: str          # "Part" ou "Reste"
    probability: float       # Probabilité de départ (0 à 1)
    risk_level: str          # "Faible", "Modéré", "Élevé", "Critique"

    class Config:
        from_attributes = True


# ─── Réponse pour prédictions groupées (filtre) ───
class PredictionGroupResponse(BaseModel):
    filter_used: str
    total_employees: int
    total_at_risk: int       # Nombre prédits "Part"
    risk_rate: float         # Pourcentage à risque
    predictions: list[PredictionResult]


# ─── Réponse pour l'historique ───
class PredictionHistory(BaseModel):
    id: int
    employee_id: int
    prediction: str
    probability: float
    risk_level: str
    filter_used: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Réponse historique groupée ───
class HistoryResponse(BaseModel):
    total_predictions: int
    predictions: list[PredictionHistory]