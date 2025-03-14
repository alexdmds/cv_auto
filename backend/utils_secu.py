import logging
from firebase_admin import auth, firestore
from backend.config import load_config
from datetime import datetime, timezone

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

def increment_token_usage(user_id: str, token_count: int):
    """
    Incrémente le nombre de tokens utilisés pour un utilisateur dans Firestore.
    
    Args:
        user_id (str): L'ID de l'utilisateur
        token_count (int): Le nombre de tokens à incrémenter
    """
    try:
        db = firestore.Client()
        stats_ref = db.collection('token_stats').document(user_id)
        
        # Obtenir l'horodatage actuel
        current_time = datetime.utcnow()
        
        # Créer une nouvelle entrée dans l'historique
        history_ref = db.collection('token_history').document()
        history_data = {
            'user_id': user_id,
            'token_count': token_count,
            'timestamp': current_time
        }
        history_ref.set(history_data)
        
        # Mettre à jour les statistiques globales
        stats_ref.set({
            'total_tokens': firestore.Increment(token_count),
            'last_request': current_time,
            'user_id': user_id
        }, merge=True)
        
        logger.info(f"Tokens mis à jour pour l'utilisateur {user_id}: {token_count} tokens")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'incrémentation des tokens: {str(e)}")


def check_token_usage(user_id: str) -> bool:
    """
    Vérifie si l'utilisateur n'a pas dépassé 1 million de tokens en usage
    et si sa dernière requête a été faite il y a plus de 20 secondes.

    Args:
        user_id (str): L'ID de l'utilisateur

    Returns:
        bool: True si l'utilisateur peut continuer à utiliser le service, sinon False.
    """
    try:
        db = firestore.Client()
        stats_ref = db.collection('token_stats').document(user_id)
        stats = stats_ref.get()

        # Si pas de stats, c'est la première requête, donc on autorise
        if not stats.exists:
            logger.info(f"Première requête pour l'utilisateur {user_id}")
            return True

        total_tokens = stats.to_dict().get('total_tokens', 0)
        last_request = stats.to_dict().get('last_request')

        if total_tokens >= 1_000_000:
            logger.warning(f"L'utilisateur {user_id} a dépassé 1 million de tokens.")
            return False

        if last_request:
            # Convertir last_request en UTC si ce n'est pas déjà le cas
            if last_request.tzinfo is None:
                last_request = last_request.replace(tzinfo=timezone.utc)
            
            # S'assurer que current_time est en UTC
            current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
            
            time_since_last_request = (current_time - last_request).total_seconds()
            if time_since_last_request < 20:
                logger.warning(f"L'utilisateur {user_id} a fait une requête récemment (il y a {time_since_last_request} secondes).")
                return False

        return True

    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'utilisation des tokens: {str(e)}")
        return False
