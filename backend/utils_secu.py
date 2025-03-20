import logging
from firebase_admin import auth, firestore
from backend.config import load_config
from datetime import datetime, timezone, UTC

logger = logging.getLogger(__name__)
config = load_config()


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
        stats_ref = db.collection('usage').document(user_id)
        stats = stats_ref.get()

        # Si pas de stats, c'est la première requête, donc on autorise
        if not stats.exists:
            logger.info(f"Première requête pour l'utilisateur {user_id}")
            return True

        stats_dict = stats.to_dict()
        total_tokens = stats_dict.get('total_usage', 0)
        last_request = stats_dict.get('last_request_time')

        if total_tokens >= 1_000_000:
            logger.warning(f"L'utilisateur {user_id} a dépassé 1 million de tokens.")
            return False

        if last_request:
            # Convertir last_request en UTC si ce n'est pas déjà le cas
            if isinstance(last_request, datetime):
                if last_request.tzinfo is None:
                    last_request = last_request.replace(tzinfo=timezone.utc)
                elif last_request.tzinfo != timezone.utc:
                    last_request = last_request.astimezone(timezone.utc)
            else:
                logger.error(f"Format de date invalide pour last_request: {type(last_request)}")
                return False
            
            current_time = datetime.now(UTC)
            time_since_last_request = (current_time - last_request).total_seconds()
            
            if time_since_last_request < 20:
                logger.warning(f"L'utilisateur {user_id} a fait une requête récemment (il y a {time_since_last_request:.2f} secondes).")
                return False

        return True

    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'utilisation des tokens: {str(e)}")
        return False
