# Utilise une image Python officielle
FROM python:3.10-slim

# Configure le répertoire de travail
WORKDIR /app

# Copie les fichiers nécessaires
COPY requirements.txt requirements.txt
COPY main.py main.py

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Expose le port 8080 pour Cloud Run
EXPOSE 8080

# Définit la commande pour démarrer l'application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]