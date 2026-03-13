"""
schemas.py — Modèles Pydantic + Validation des données entrantes
Projet P5 - Futurisys API Attrition

Ce fichier définit :
  - Les schémas de RÉPONSE (PredictionResult, PredictionGroupResponse…)
  - Les schémas de FILTRE avec validation stricte des valeurs attendues
    par le modèle ML (FilterParams)
"""

from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, Literal
from datetime import datetime
from fastapi import Query as FastAPIQuery
from pydantic import ConfigDict

# ══════════════════════════════════════════════════════════════
# VALEURS AUTORISÉES (synchronisées avec la base de données)
# ══════════════════════════════════════════════════════════════

POSTES_VALIDES = {
    "Cadre Commercial",
    "Assistant de Direction",
    "Consultant",
    "Tech Lead",
    "Manager",
    "Senior Manager",
    "Représentant Commercial",
    "Directeur Technique",
    "Ressources Humaines"
}

DEPARTEMENTS_VALIDES = {
    "Consulting", "Commercial", "Ressources Humaines"
}

HEURES_SUP_VALIDES = {"Oui", "Non"}


# ══════════════════════════════════════════════════════════════
# SCHÉMA DE FILTRE — Validation des paramètres de requête
# ══════════════════════════════════════════════════════════════

class FilterParams(BaseModel):
    """
    Paramètres de filtre pour GET /predict/filter
    Valide que les valeurs sont conformes aux attentes du modèle ML.
    Au moins un filtre est requis.
    """
    poste: Optional[str] = FastAPIQuery(None)
    departement: Optional[str] = FastAPIQuery(None)
    heure_sup: Optional[str] = FastAPIQuery(None)

    @field_validator("poste")
    @classmethod
    def valider_poste(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in POSTES_VALIDES:
            raise ValueError(
                f"Poste '{v}' invalide. "
                f"Valeurs autorisées : {sorted(POSTES_VALIDES)}"
            )
        return v

    @field_validator("departement")
    @classmethod
    def valider_departement(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in DEPARTEMENTS_VALIDES:
            raise ValueError(
                f"Département '{v}' invalide. "
                f"Valeurs autorisées : {sorted(DEPARTEMENTS_VALIDES)}"
            )
        return v

    @field_validator("heure_sup")
    @classmethod
    def valider_heure_sup(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in HEURES_SUP_VALIDES:
            raise ValueError(
                f"heure_sup '{v}' invalide. "
                f"Valeurs autorisées : {sorted(HEURES_SUP_VALIDES)}"
            )
        return v

    @model_validator(mode="after")
    def au_moins_un_filtre(self) -> "FilterParams":
        """Au moins un filtre doit être fourni pour éviter les requêtes sans contexte."""
        if not any([self.poste, self.departement, self.heure_sup]):
            raise ValueError(
                "Au moins un filtre est requis : poste, departement ou heure_sup."
            )
        return self


# ══════════════════════════════════════════════════════════════
# SCHÉMAS DE RÉPONSE
# ══════════════════════════════════════════════════════════════

class PredictionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    """Résultat pour UN employé."""
    employee_id: int
    prediction: Literal["Part", "Reste"]
    probability: float          # Probabilité de départ (0.0 → 1.0)
    risk_level: str             # "Faible", "Modéré", "Élevé", "Critique"

    @field_validator("probability")
    @classmethod
    def probabilite_valide(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"La probabilité doit être entre 0 et 1, reçu : {v}")
        return round(v, 4)


class PredictionGroupResponse(BaseModel):
    """Réponse pour une prédiction groupée (filtre)."""
    filter_used: str
    total_employees: int
    total_at_risk: int          # Nombre prédits "Part"
    risk_rate: float            # Pourcentage à risque (0.0 → 100.0)
    predictions: list[PredictionResult]


class PredictionHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    """Entrée de l'historique des prédictions."""
    id: int
    employee_id: int
    prediction: str
    probability: float
    risk_level: str
    filter_used: Optional[str] = None
    created_at: datetime



class HistoryResponse(BaseModel):
    """Réponse groupée de l'historique."""
    total_predictions: int
    predictions: list[PredictionHistory]


# ══════════════════════════════════════════════════════════════
# SCHÉMA AUTHENTIFICATION
# ══════════════════════════════════════════════════════════════

class Token(BaseModel):
    """Réponse du endpoint POST /token."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Données décodées depuis le JWT."""
    username: Optional[str] = None