from flask import Flask
from flask_cors import CORS
import logging
from backend.api.endpoint__generate_profile import generate_profile_endpoint
from backend.config import configure_logging

# Configuration du logging
configure_logging()
logger = logging.getLogger(__name__)

# Création de l'application Flask
app = Flask(__name__)
CORS(app)

@app.route('/api/generate-profile/<user_id>', methods=['POST'])
def generate_profile(user_id):
    """
    Route pour générer un profil à partir des fichiers texte.
    
    Args:
        user_id (str): ID de l'utilisateur
        
    Returns:
        Response: Réponse JSON avec le profil généré ou une erreur
    """
    return generate_profile_endpoint(user_id)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
