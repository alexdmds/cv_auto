from google.cloud import storage
from flask import jsonify
import logging
from backend.config import load_config

config = load_config()
logger = logging.getLogger(__name__)

def get_concatenated_text_files(user_id: str) -> str:
    """
    Récupère et concatène tous les fichiers texte présents dans le bucket pour un utilisateur donné.
    
    Args:
        user_id (str): ID de l'utilisateur
        
    Returns:
        str: Contenu concaténé de tous les fichiers texte
    """
    try:
        # Récupérer les fichiers depuis le bucket
        bucket = storage.Client().bucket(config.BUCKET_NAME)
        text_files = []
        
        for blob in bucket.list_blobs(prefix=f"{user_id}/sources/"):
            if blob.name.endswith(".txt"):
                content = blob.download_as_string().decode("utf-8")
                text_files.append(content)
        
        if not text_files:
            logger.warning(f"Aucun fichier texte trouvé pour l'utilisateur {user_id}")
            return ""
        
        # Concaténer tous les textes
        text_to_analyze = "\n\n".join(text_files)
        return text_to_analyze

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des fichiers texte: {str(e)}", exc_info=True)
        return ""
