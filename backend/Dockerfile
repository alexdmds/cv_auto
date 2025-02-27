# Utiliser une image Python officielle
FROM python:3.13-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Variable d'environnement pour le port
ENV PORT=8080

# Commande pour démarrer l'application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app