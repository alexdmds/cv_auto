from google.cloud import storage
from flask import jsonify
import logging
from backend.config import load_config
import io
from pdfminer.high_level import extract_text
import requests
from backend.models import UserDocument

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
    # Code gardé en commentaire pour implémentation future
    """
    try:
        # Headers pour simuler un navigateur web
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Effectuer la requête
        response = requests.get(linkedin_url, headers=headers, timeout=10)
        
        # Vérifier le statut de la réponse
        if response.status_code == 200:
            return response.text
        else:
            logger.warning(f"Échec de la récupération du profil LinkedIn. Status code: {response.status_code}")
            return ""
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du contenu LinkedIn: {str(e)}", exc_info=True)
        return ""
    """
    
    logger.info(f"Récupération du contenu LinkedIn désactivée pour l'URL: {linkedin_url}")
    return ""

def get_concatenated_text_files(user_document: UserDocument) -> str:
    """
    Récupère et concatène tous les fichiers texte et PDF présents dans le bucket pour un utilisateur donné,
    ainsi que le contenu LinkedIn si disponible.
    
    Args:
        user_document (UserDocument): Document utilisateur contenant l'ID et les informations du profil
        
    Returns:
        str: Contenu concaténé de tous les fichiers texte, PDF et LinkedIn
    """
    try:
        # Récupérer les fichiers depuis le bucket
        bucket = storage.Client().bucket(config.BUCKET_NAME)
        text_files = []
        
        # Récupérer les fichiers du bucket
        for blob in bucket.list_blobs(prefix=f"{user_document.id}/sources/"):
            if blob.name.endswith(".txt"):
                content = blob.download_as_bytes().decode("utf-8")
                text_files.append(content)
            elif blob.name.endswith(".pdf"):
                pdf_content = blob.download_as_bytes()
                text = extract_text(io.BytesIO(pdf_content))
                text_files.append(text)
        
        # Récupérer le contenu LinkedIn si l'URL est disponible
        if user_document.profile and user_document.profile.head and user_document.profile.head.linkedin_url:
            linkedin_content = get_linkedin_profile_content(user_document.profile.head.linkedin_url)
            if linkedin_content:
                text_files.append(linkedin_content)
        
        if not text_files:
            logger.warning(f"Aucun fichier texte, PDF ou contenu LinkedIn trouvé pour l'utilisateur {user_document.id}")
            return ""
        
        # Concaténer tous les textes
        text_to_analyze = "\n\n".join(text_files)
        return text_to_analyze

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des fichiers texte, PDF et LinkedIn: {str(e)}", exc_info=True)
        return ""
