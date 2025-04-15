from functools import wraps
from flask import jsonify, request
from backend.utils_secu import check_token_usage
from backend.config import load_config
import logging

logger = logging.getLogger(__name__)
config = load_config()

def check_rate_limit(f):
    """Décorateur pour vérifier les limites d'utilisation des tokens"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not config.CHECK_RATE_LIMIT:
            return f(*args, **kwargs)
        
        # Récupérer user_id depuis request (injecté par auth_required)
        user_id = request.user_id
        
        logger.info(f"Vérification des limites pour l'utilisateur {user_id}")
        if not check_token_usage(user_id):
            return jsonify({
                "error": "Rate limit exceeded",
                "message": "Veuillez attendre 20 secondes entre chaque requête ou vérifiez votre limite de tokens"
            }), 429
            
        return f(*args, **kwargs)
    return decorated_function 