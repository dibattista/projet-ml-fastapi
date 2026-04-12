# Futurisys — API Prédiction d'Attrition

!!! info "Projet P5 — OpenClassrooms AI Engineer"
    POC développé pour **TechNova Partners** dans le cadre du programme AI Engineer.  
    Version actuelle : **v1.6.1**

---

## Présentation

TechNova Partners, une ESN de 1 000+ employés, fait face à un **taux de démission de 16%**.  
Le coût estimé par départ dépasse **6 mois de salaire** (recrutement, onboarding, perte de savoir-faire).

Cette API déploie le modèle **Random Forest** entraîné en P4 pour permettre aux équipes RH de :

| Fonctionnalité | Description |
|----------------|-------------|
| 🔮 **Prédiction par filtre** | Identifier les groupes d'employés à risque |
| 👤 **Prédiction individuelle** | Évaluer le risque de départ d'un employé |
| 📊 **Historique** | Consulter toutes les prédictions passées |
| 🔐 **Sécurité** | Accès protégé par JWT (Bearer Token) |
| 🎮 **Démo no-code** | Interface Gradio pour les équipes RH |

---

## Architecture globale

```
Équipes RH
    │
    ├── Interface Gradio ──────────────────────┐
    │   (barbaradi-futurisys-attrition.hf.space)│
    │                                          │
    └── Appels directs API ────────────────────┤
        (curl, Postman, outils métier)         │
                                               ▼
                                    ┌─────────────────┐
                                    │   FastAPI        │
                                    │   + Auth JWT     │
                                    └────────┬────────┘
                                             │
                          ┌──────────────────┼──────────────────┐
                          ▼                  ▼                  ▼
                   ┌────────────┐   ┌──────────────┐   ┌──────────────┐
                   │ PostgreSQL │   │ Random Forest│   │  Logging     │
                   │  (5 tables)│   │  .pkl        │   │  predictions │
                   └────────────┘   └──────────────┘   └──────────────┘
```

---

## Stack technique

| Couche | Technologie | Version |
|--------|-------------|---------|
| **API** | FastAPI | 0.11x |
| **Langage** | Python | 3.12 |
| **Base de données** | PostgreSQL + SQLAlchemy | 16 |
| **Authentification** | JWT (python-jose + bcrypt) | — |
| **ML** | scikit-learn + joblib | — |
| **Tests** | pytest + pytest-cov | **91%** |
| **CI/CD** | GitHub Actions | — |
| **Démo** | Gradio + HF Spaces | — |
| **Dépendances** | Poetry | — |

---

## Liens rapides

- 🔗 [Dépôt GitHub](https://github.com/dibattista/projet-ml-fastapi)
- 🎮 [Démo Gradio](https://barbaradi-futurisys-attrition.hf.space/demo)
- 📖 [Swagger UI](http://localhost:8000/docs) *(en local)*

!!! warning "Périmètre POC"
    L'API opère sur les **employés existants** stockés en base.  
    Elle filtre, prédit, et logue — elle n'accepte pas de nouvelles saisies d'employés.
