from google.cloud import storage
import logging
from backend.config import load_config
import io
from pdfminer.high_level import extract_text
import requests

config = load_config()
logger = logging.getLogger(__name__)

def get_linkedin_profile_content(linkedin_url: str) -> str:
    """
    Récupère le contenu brut HTML d'un profil LinkedIn à partir de son URL.
    Note: Actuellement désactivé, retourne une chaîne vide.
    Pour une implémentation future, il faudra :
    - Soit utiliser l'API officielle LinkedIn
    - Soit utiliser un service de scraping spécialisé
    - Soit implémenter une solution avec Selenium/Playwright
    
    Args:
        linkedin_url (str): URL du profil LinkedIn
        
    Returns:
        str: Contenu HTML brut de la page LinkedIn (actuellement retourne une chaîne vide)
    """
    # TODO: Implémenter la récupération du contenu LinkedIn
    return ""

def get_concatenated_text_files(user_id: str, linkedin_url: str = None) -> str:
    """
    Récupère et concatène tous les fichiers texte et PDF présents dans le bucket pour un utilisateur donné,
    ainsi que le contenu LinkedIn si disponible.
    
    Args:
        user_id (str): ID de l'utilisateur
        linkedin_url (str, optional): URL du profil LinkedIn
        
    Returns:
        str: Contenu concaténé de tous les fichiers texte, PDF et LinkedIn
    """
    try:
        # Récupérer les fichiers depuis le bucket
        bucket = storage.Client().bucket(config.BUCKET_NAME)
        text_files = []
        
        # Récupérer les fichiers du bucket
        for blob in bucket.list_blobs(prefix=f"{user_id}/sources/"):
            if blob.name.endswith(".txt"):
                content = blob.download_as_bytes().decode("utf-8")
                text_files.append(content)
            elif blob.name.endswith(".pdf"):
                pdf_content = blob.download_as_bytes()
                text = extract_text(io.BytesIO(pdf_content))
                text_files.append(text)
        
        # Récupérer le contenu LinkedIn si l'URL est disponible
        if linkedin_url:
            linkedin_content = get_linkedin_profile_content(linkedin_url)
            if linkedin_content:
                text_files.append(linkedin_content)
        
        if not text_files:
            logger.warning(f"Aucun fichier texte, PDF ou contenu LinkedIn trouvé pour l'utilisateur {user_id}")
            return ""
        
        # Concaténer tous les textes
        text_to_analyze = "\n\n".join(text_files)
        return text_to_analyze

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des fichiers texte, PDF et LinkedIn: {str(e)}", exc_info=True)
        return "" 