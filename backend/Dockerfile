# Utilise une image Python officielle
FROM python:3.13.1-slim

# Configure le répertoire de travail dans le conteneur
WORKDIR /app

# Copie les fichiers nécessaires depuis le répertoire backend/
COPY backend/ .

# Installe les dépendances spécifiées dans requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose le port 8080 pour Cloud Run
EXPOSE 8080

# Définit la commande pour démarrer l'application avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]