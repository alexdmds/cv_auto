from flask import request, jsonify
from functools import wraps
from firebase_admin import auth
import logging
from backend.config import load_config

logger = logging.getLogger(__name__)
config = load_config()

def auth_required(f):
    """Décorateur pour vérifier l'authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not config.CHECK_AUTH:
            # En développement, utiliser un ID factice
            request.user_id = "test_user"
            return f(*args, **kwargs)
            
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Token manquant ou invalide"}), 401
            
        token = auth_header.split('Bearer ')[1]
        try:
            decoded_token = auth.verify_id_token(token)
            request.user_id = decoded_token['uid']
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Erreur d'authentification: {str(e)}")
            return jsonify({"error": "Token invalide"}), 401
            
    return decorated_function 