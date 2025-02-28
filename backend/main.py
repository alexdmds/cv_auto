from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from backend.api.endpoint__generate_profile import generate_profile_endpoint
from backend.config import configure_logging
from backend.auth import auth_required

# Configuration du logging
configure_logging()
logger = logging.getLogger(__name__)

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
        "user_id": user_id
    }), 200

@app.route('/api/generate-profile', methods=['POST'])
@auth_required
def generate_profile():
    """Génère un profil pour l'utilisateur authentifié"""
    user_id = request.user_id  # Injecté par le décorateur auth_required
    return generate_profile_endpoint(user_id)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
