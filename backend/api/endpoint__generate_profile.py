from flask import jsonify, request
from google.cloud import storage
import logging
from backend.config import load_config
from dotenv import load_dotenv
import os
import asyncio
from backend.utils import authenticate_user
from firebase_admin import firestore

load_dotenv()

logger = logging.getLogger(__name__)

# Import conditionnel basé sur la configuration
config = load_config()
if config.MOCK_OPENAI:
    from ai_module.mock_inference import generate_profile, generate_head
else:
    from ai_module.inference import generate_profile, generate_head

async def generate_profile_endpoint(user_id: str):
    """
    Endpoint pour générer un profil structuré à partir des fichiers texte du bucket.
    
    Args:
        user_id (str): ID de l'utilisateur
        
    Returns:
        Response: Réponse JSON avec le profil généré
    """
    try:
        logger.info(f"Génération du profil pour l'utilisateur {user_id}")
        
        # Récupérer les fichiers depuis le bucket
        bucket = storage.Client().bucket(config.BUCKET_NAME)
        text_files = []
        
        for blob in bucket.list_blobs(prefix=f"{user_id}/sources/"):
            if blob.name.endswith(".txt"):
                content = blob.download_as_string().decode("utf-8")
                text_files.append(content)
        
        if not text_files:
            logger.warning(f"Aucun fichier texte trouvé pour l'utilisateur {user_id}")
            return jsonify({"error": "No text files found"}), 404

        # Concaténer tous les textes
        text_to_analyze = "\n\n".join(text_files)
        
        # Passer l'user_id aux fonctions de génération
        profile = await generate_profile(text_to_analyze, user_id)
        head = await generate_head(text_to_analyze, user_id)

        # Structurer les données selon le format demandé
        cv_data = {
            'head': {
                'name': head.get('name', ''),
                'phone': head.get('phone', ''),
                'email': head.get('email', ''),
                'general_title': head.get('general_title', '')
            },
            'experiences': {
                'experiences': profile.get('experiences', [])
            },
            'education': {
                'educations': profile.get('education', [])
            },
            'skills': {
                'description': head.get('skills', '')
            },
            'hobbies': {
                'description': head.get('hobbies', '')
            }
        }

        # Sauvegarder dans Firestore
        db = firestore.Client()
        doc_ref = db.collection('users').document(user_id)
        doc_ref.set({
            'cv_data': cv_data
        }, merge=True)
        
        logger.info(f"Profil et en-tête générés et sauvegardés pour l'utilisateur {user_id}")
        return jsonify({
            "success": True, 
            "cv_data": cv_data
        }), 200

    except Exception as e:
        logger.error(f"Erreur lors de la génération du profil: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
