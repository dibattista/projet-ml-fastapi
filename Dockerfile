FROM python:3.12-slim

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . .

# Port HF Spaces
EXPOSE 7860

# Lancer FastAPI (avec Gradio monté sur /demo)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
