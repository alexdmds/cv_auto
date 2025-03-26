from flask import jsonify, request
import logging
import time
from backend.config import load_config
from dotenv import load_dotenv
from backend.utils.utils_gcs import get_concatenated_text_files
from backend.models import UserDocument, CallDocument, UsageDocument
from ai_module.lg_models import ProfileState
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
    Version synchrone.
    
    Args:
        user_id (str): ID de l'utilisateur
        
    Returns:
        Response: Réponse JSON avec le profil généré
    """
    start_time = time.time()
    try:
        logger.info(f"Génération du profil pour l'utilisateur {user_id}")

        # Définir l'UserDocument à partir de user_id
        user_document = UserDocument.from_firestore_id(user_id)
        if not user_document:
            logger.warning(f"Utilisateur avec l'ID {user_id} non trouvé dans Firestore, génération d'un document vierge")
            user_document = UserDocument(id=user_id)
        
        # Récupérer le texte de manière synchrone
        text_content = get_concatenated_text_files(user_document)
        
        # Créer un objet ProfileState avec le texte brut
        profile_state = ProfileState.from_input_text(text_content)
        
        # Appel synchrone à generate_profile
        profile_state = generate_profile(profile_state)
        
        # Mettre à jour le document utilisateur avec les nouvelles données
        user_document.update_from_profile_state(profile_state)
        
        # Enregistrer l'appel et mettre à jour l'utilisation en parallèle
        CallDocument.create_call(user_id, "generate_profile")
        usage_doc = UsageDocument.get_or_create(user_id)
        usage_doc.increment_usage()
        
        # Sauvegarde synchrone
        user_document.save()
        
        execution_time = time.time() - start_time
        logger.info(f"Profil généré et sauvegardé pour l'utilisateur {user_id} en {execution_time:.2f} secondes")
        return jsonify({"success": True, "execution_time": execution_time}), 200
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Erreur lors de la génération du profil après {execution_time:.2f} secondes: {str(e)}", exc_info=True)
        return jsonify({"error": str(e), "execution_time": execution_time}), 500
