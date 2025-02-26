from flask import jsonify, request
from google.cloud import storage
import logging
from backend.config import load_config
from dotenv import load_dotenv
import os
import asyncio
from backend.utils import authenticate_user

load_dotenv()

logger = logging.getLogger(__name__)

# Import conditionnel basé sur la configuration
config = load_config()
if config.MOCK_OPENAI:
    from ai_module.mock_inference import generate_profile
else:
    from ai_module.inference import generate_profile

def generate_profile_endpoint(user_id: str):
    """
    Endpoint pour générer un profil structuré à partir des fichiers texte du bucket.
    
    Args:
        user_id (str): ID de l'utilisateur
        
    Returns:
        Response: Réponse JSON avec succès ou erreur
    """
    try:
        # Authentification de l'utilisateur uniquement en prod
        if config.CHECK_AUTH:
            auth_header = request.headers.get('Authorization')
            try:
                authenticated_user_id = authenticate_user(auth_header)
                if authenticated_user_id != user_id:
                    logger.warning(f"Tentative d'accès non autorisé: {authenticated_user_id} essaie d'accéder aux données de {user_id}")
                    return jsonify({"error": "Unauthorized access"}), 403
            except ValueError as e:
                logger.error(f"Erreur d'authentification: {str(e)}")
                return jsonify({"error": "Authentication failed"}), 401

        # Initialiser le client Storage
        storage_client = storage.Client()
        bucket = storage_client.bucket(config.BUCKET_NAME)

        # Récupérer les fichiers texte
        text_files = []
        for blob in bucket.list_blobs(prefix=f"{user_id}/sources/"):
            if blob.name.endswith(".txt"):
                content = blob.download_as_string().decode("utf-8")
                text_files.append(content)

        if not text_files:
            logger.warning(f"Aucun fichier texte trouvé pour l'utilisateur {user_id}")
            return jsonify({"error": "No text files found"}), 404

        # Concaténer tous les textes
        combined_text = "\n\n".join(text_files)
        
        # Générer le profil structuré en utilisant asyncio pour exécuter la fonction asynchrone
        profile = asyncio.run(generate_profile(combined_text))

        # Sauvegarder dans Firestore
        from backend.firestore.firebase_init import db
        db.reference(f'users/{user_id}/profile').set(profile)
        
        logger.info(f"Profil généré et sauvegardé pour l'utilisateur {user_id}")
        return jsonify({"success": True, "profile": profile}), 200

    except Exception as e:
        logger.error(f"Erreur lors de la génération du profil: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
