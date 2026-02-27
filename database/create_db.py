"""
P5 - Création des tables de la base de données.
4 tables : sirh, evaluation, sondage, predictions
"""
import os
from sqlalchemy import (
    create_engine, Column, Integer, Float,
    String, DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


# ============================================
# Table 1 : sirh (données RH - table principale)
# ============================================
class Sirh(Base):
    __tablename__ = "sirh"

    id_employee = Column(Integer, primary_key=True)
    age = Column(Integer, nullable=False)
    genre = Column(String(10), nullable=False)
    revenu_mensuel = Column(Integer, nullable=False)
    statut_marital = Column(String(20), nullable=False)
    departement = Column(String(30), nullable=False)
    poste = Column(String(40), nullable=False)
    nombre_experiences_precedentes = Column(Integer, nullable=False)
    nombre_heures_travailless = Column(Integer, nullable=False)
    annee_experience_totale = Column(Integer, nullable=False)
    annees_dans_l_entreprise = Column(Integer, nullable=False)
    annees_dans_le_poste_actuel = Column(Integer, nullable=False)


# ============================================
# Table 2 : evaluation (notes et satisfaction)
# ============================================
class Evaluation(Base):
    __tablename__ = "evaluation"

    eval_number = Column(Integer, primary_key=True)
    satisfaction_employee_environnement = Column(Integer, nullable=False)
    note_evaluation_precedente = Column(Integer, nullable=False)
    niveau_hierarchique_poste = Column(Integer, nullable=False)
    satisfaction_employee_nature_travail = Column(Integer, nullable=False)
    satisfaction_employee_equipe = Column(Integer, nullable=False)
    satisfaction_employee_equilibre_pro_perso = Column(Integer, nullable=False)
    note_evaluation_actuelle = Column(Integer, nullable=False)
    heure_supplementaires = Column(String(5), nullable=False)
    augementation_salaire_precedente = Column(String(10), nullable=False)


# ============================================
# Table 3 : sondage (bien-être et contexte)
# ============================================
class Sondage(Base):
    __tablename__ = "sondage"

    code_sondage = Column(Integer, primary_key=True)
    a_quitte_l_entreprise = Column(String(5), nullable=False)
    nombre_participation_pee = Column(Integer, nullable=False)
    nb_formations_suivies = Column(Integer, nullable=False)
    nombre_employee_sous_responsabilite = Column(Integer, nullable=False)
    distance_domicile_travail = Column(Integer, nullable=False)
    niveau_education = Column(Integer, nullable=False)
    domaine_etude = Column(String(40), nullable=False)
    ayant_enfants = Column(String(5), nullable=False)
    frequence_deplacement = Column(String(20), nullable=False)
    annees_depuis_la_derniere_promotion = Column(Integer, nullable=False)
    annes_sous_responsable_actuel = Column(Integer, nullable=False)


# ============================================
# Table 4 : predictions (logs API)
# ============================================
class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        Integer,
        ForeignKey("sirh.id_employee"),
        nullable=False
    )
    prediction = Column(String(10), nullable=False)
    probability = Column(Float, nullable=False)
    risk_level = Column(String(10), nullable=False)
    filter_used = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())  # pylint: disable=not-callable


def create_database():
    """Crée la base de données et les tables."""
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "attrition_db")

    database_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    engine = create_engine(database_url)

    # Supprime les anciennes tables
    Base.metadata.drop_all(engine)

    # Crée les nouvelles tables
    Base.metadata.create_all(engine)
    print("Tables 'sirh', 'evaluation', 'sondage' et 'predictions' créées avec succès !")


if __name__ == "__main__":
    create_database()