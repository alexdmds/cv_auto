from flask import jsonify, request
import logging
from backend.config import load_config
from dotenv import load_dotenv
from backend.utils.utils_gcs import get_concatenated_text_files
from backend.models import UserDocument
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
        result_state = generate_profile(profile_state)
        
        # Création du document utilisateur
        user_document = UserDocument.from_profile_state(result_state, user_id)
        
        # Sauvegarde synchrone
        user_document.save()
        
        logger.info(f"Profil généré et sauvegardé pour l'utilisateur {user_id}")
        return jsonify({"success": True}), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du profil: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
