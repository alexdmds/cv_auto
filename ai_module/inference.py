from openai import OpenAI
from ai_module.models.generate_profile import generate_structured_profile
import logging

logger = logging.getLogger(__name__)

async def generate_profile(text: str):
    """
    Génère un profil structuré à partir d'un texte brut.
    
    Args:
        text (str): Le texte brut contenant les informations du profil
        
    Returns:
        dict: Le profil structuré sous forme de dictionnaire
    """
    try:
        logger.info("Début de la génération du profil...")
        profile = await generate_structured_profile(text)
        logger.info("Profil généré avec succès")
        return profile
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du profil: {str(e)}")
        raise
