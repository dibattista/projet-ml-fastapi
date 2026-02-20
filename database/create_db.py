from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Prediction(Base):
    """Création de la table predictions"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer)
    age = Column(Integer)
    heure_supp_encoded = Column(Integer)
    nombre_participation_pee = Column(Integer)
    annees_sous_responsable_actuel = Column(Integer)
    annees_dans_l_entreprise = Column(Integer)
    revenu_mensuel = Column(Integer)
    annee_experience_totale = Column(Integer)
    feat_junior_poste_risque = Column(Integer)
    distance_domicile_travail = Column(Integer)
    satisfaction_employee_environnement = Column(Integer)
    annees_dans_le_poste_actuel = Column(Integer)
    nombre_experiences_precedentes = Column(Integer)
    prediction = Column(Integer)
    probability = Column(Float)
    prediction_date = Column(DateTime, server_default=func.now())

def create_database():
    """Crée la base de données et les tables via SQLAlchemy."""

    engine = create_engine(
        "postgresql+psycopg2://postgres:postgres@localhost/attrition_db"
    )

    Base.metadata.create_all(engine)
    print("Base de données et tables créées avec succès !")


if __name__ == "__main__":
    create_database()