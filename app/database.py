import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Charger les variables d'environnement
load_dotenv()

# Construire l'URL de connexion
db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("DB_PASSWORD", "postgres")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "attrition_db")

DATABASE_URL = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Créer le moteur de connexion
engine = create_engine(DATABASE_URL)

# Fabrique de sessions (une session = une conversation avec la DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Fournit une session DB à chaque requête API, puis la ferme."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()