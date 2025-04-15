import logging
import time
import os
from backend.config import load_config
from dotenv import load_dotenv
from backend.models import ProfileDocument, CVDocument
from ai_module.lg_models import CVGenState
from flask import jsonify
from backend.utils.utils_gcs import upload_to_firebase_storage

load_dotenv()
logger = logging.getLogger(__name__)
config = load_config()

# Import conditionnel basé sur la configuration
if config.MOCK_OPENAI:
    from ai_module.mock_inference import generate_cv
else:
    from ai_module.inference import generate_cv

def generate_cv_endpoint(user_id: str, cv_id: str):
    """
    Endpoint pour générer un CV structuré.
    Version 2 de l'API utilisant ProfileDocument et CVDocument.
    
    Args:
        user_id (str): ID de l'utilisateur
        cv_id (str): ID du document CV dans Firestore
        
    Returns:
        Response: Réponse JSON avec le CV généré
    """
    start_time = time.time()
    try:
        logger.info(f"Génération du CV {cv_id} pour l'utilisateur {user_id}")

        # Récupérer le profil existant
        profile_document = ProfileDocument.from_firestore_id(user_id)
        if not profile_document:
            logger.warning(f"Profil avec l'ID {user_id} non trouvé dans Firestore")
            return jsonify({"error": "Profil non trouvé"}), 404
        
        # Récupérer le job_raw à partir du cv dans la collection cvs
        cv_document = CVDocument.from_firestore_id(cv_id)
        if not cv_document:
            logger.warning(f"CV avec l'ID {cv_id} non trouvé dans Firestore")
            return jsonify({"error": "CV non trouvé"}), 404
            
        job_raw = cv_document.job_raw if hasattr(cv_document, 'job_raw') else ""
        
        # Créer un objet CVGenState à partir du profil et du job_raw
        cv_state = CVGenState.from_profile_document(profile_document, cv_document.cv_name, job_raw)
        
        # Appel synchrone à generate_cv
        cv_state = generate_cv(cv_state)
        
        # Mettre à jour le CVDocument
        cv_document.update_from_cv_state(cv_state)
        
        # Sauvegarde synchrone
        cv_document.save()
        
        # Générer le PDF
        output_dir = os.path.join("temp", user_id, "cvs")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{cv_document.cv_name}.pdf")
        
        # Générer le PDF
        cv_document.cv_data.generate_pdf(output_path, user_id=user_id)
        
        # Upload du PDF vers GCS
        cv_url = upload_to_firebase_storage(output_path, user_id, cv_id)
        
        # Mettre à jour l'URL du CV dans le document
        cv_document.cv_url = cv_url
        cv_document.save()
        
        execution_time = time.time() - start_time
        logger.info(f"CV généré et sauvegardé pour l'utilisateur {user_id} en {execution_time:.2f} secondes")
        return jsonify({"success": True, "execution_time": execution_time, "cv_url": cv_url}), 200
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Erreur lors de la génération du CV après {execution_time:.2f} secondes: {str(e)}", exc_info=True)
        return jsonify({"error": str(e), "execution_time": execution_time}), 500
