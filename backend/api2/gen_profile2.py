import logging
import time
from backend.config import load_config
from dotenv import load_dotenv
from backend.utils.utils_gcs2 import get_concatenated_text_files
from backend.models import ProfileDocument, CallDocument, UsageDocument
from ai_module.lg_models import ProfileState
from flask import jsonify

load_dotenv()
logger = logging.getLogger(__name__)
config = load_config()

# Import conditionnel basé sur la configuration
if config.MOCK_OPENAI:
    from ai_module.mock_inference import generate_profile
else:
    from ai_module.inference import generate_profile

def generate_profile_endpoint(user_id: str):
    """
    Endpoint pour générer un profil structuré.
    Version 2 de l'API utilisant ProfileDocument.
    
    Args:
        user_id (str): ID de l'utilisateur
        
    Returns:
        Response: Réponse JSON avec le profil généré
    """
    start_time = time.time()
    try:
        logger.info(f"Génération du profil pour l'utilisateur {user_id}")

        # Enregistrer l'appel et mettre à jour l'utilisation en parallèle
        CallDocument.create_call(user_id, "generate_profile_v2")
        usage_doc = UsageDocument.get_or_create(user_id)
        usage_doc.increment_usage()

        # Récupérer le profil existant pour l'URL LinkedIn si disponible
        profile_document = ProfileDocument.from_firestore_id(user_id)
        linkedin_url = profile_document.head.linkedin_url if profile_document else None
        
        # Récupérer le texte de manière synchrone
        text_content = get_concatenated_text_files(user_id, linkedin_url)
        
        # Créer un objet ProfileState avec le texte brut
        profile_state = ProfileState.from_input_text(text_content)
        
        # Appel synchrone à generate_profile
        profile_state = generate_profile(profile_state)
        
        # Créer ou mettre à jour le ProfileDocument
        profile_document = ProfileDocument.from_profile_state(profile_state, user_id)
        
        # Sauvegarde synchrone
        profile_document.save()
        
        execution_time = time.time() - start_time
        logger.info(f"Profil généré et sauvegardé pour l'utilisateur {user_id} en {execution_time:.2f} secondes")
        return jsonify({"success": True, "execution_time": execution_time}), 200
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Erreur lors de la génération du profil après {execution_time:.2f} secondes: {str(e)}", exc_info=True)
        return jsonify({"error": str(e), "execution_time": execution_time}), 500