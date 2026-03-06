"""
P5 - Créer un utilisateur de test pour l'API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.auth import get_password_hash
from database.create_db import User

def create_test_user():
    db = SessionLocal()
    user = User(
        username="admin",
        hashed_password=get_password_hash("futurisys2024"),
        is_active=True
    )
    db.add(user)
    db.commit()
    print("Utilisateur créé : admin / futurisys2024")
    db.close()

if __name__ == "__main__":
    create_test_user()