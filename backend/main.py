from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from backend.api.endpoint__generate_profile import generate_profile_endpoint
from backend.config import configure_logging, load_config
from backend.auth import auth_required
from backend.decorators import check_rate_limit
import firebase_admin
import os

# Configuration du logging
configure_logging()
logger = logging.getLogger(__name__)

# Configuration
config = load_config()

# Initialisation de Firebase Admin seulement si pas en local
if config.ENV != "local":
    try:
        firebase_admin.initialize_app()
        logger.info("Firebase Admin initialisé avec les credentials par défaut")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de Firebase Admin: {str(e)}")
else:
    logger.info("Mode local: pas d'initialisation de Firebase Admin")

# Création de l'application Flask
app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
@auth_required
def health_check():
    """Endpoint de test pour vérifier que le backend fonctionne"""
    user_id = request.user_id  # Injecté par le décorateur auth_required
    return jsonify({
        "status": "ok",
        "message": "Le backend fonctionne correctement",
        "user_id": user_id,
        "env": config.ENV
    }), 200

@app.route('/api/generate-profile', methods=['POST'])
@auth_required
@check_rate_limit
def generate_profile():
    """Génère un profil pour l'utilisateur authentifié"""
    user_id = request.user_id  # Injecté par le décorateur auth_required
    return generate_profile_endpoint(user_id)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
