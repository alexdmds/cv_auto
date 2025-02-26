import logging
from firebase_admin import auth
from backend.config import load_config

logger = logging.getLogger(__name__)
config = load_config()

def authenticate_user(auth_header):
    """
    Authentifie un utilisateur à partir du token Bearer.
    
    Args:
        auth_header (str): L'en-tête Authorization de la requête
        
    Returns:
        str: L'ID de l'utilisateur authentifié
        
    Raises:
        ValueError: Si l'authentification échoue
    """
    if not config.CHECK_AUTH:
        # En développement, retourner un ID factice si l'authentification est désactivée
        return "test_user"
        
    if not auth_header or not auth_header.startswith('Bearer '):
        raise ValueError("Token manquant ou invalide")
        
    token = auth_header.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        logger.error(f"Erreur d'authentification: {str(e)}")
        raise ValueError("Token invalide")