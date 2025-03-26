from flask import jsonify, request
import logging
from backend.models import UserDocument, CV
from ai_module.lg_models import CVGenState
from datetime import datetime
from backend.config import load_config
from pathlib import Path
import firebase_admin
from firebase_admin import storage
config = load_config()
logger = logging.getLogger(__name__)

# Import conditionnel basé sur la configuration
if config.MOCK_OPENAI:
    from ai_module.mock_inference import generate_cv
    logger.info("Utilisation de l'implémentation MOCK de generate_cv")
else:
    from ai_module.inference import generate_cv
    logger.info("Utilisation de l'implémentation RÉELLE de generate_cv")


def upload_to_firebase_storage(file_path: str, user_id: str, cv_name: str) -> str:
    """
    Upload un fichier vers Firebase Storage.
    
    Args:
        file_path (str): Chemin local du fichier à uploader
        user_id (str): ID de l'utilisateur
        cv_name (str): Nom du CV
        
    Returns:
        str: URL publique du fichier uploadé
    """
    bucket = storage.bucket(config.BUCKET_NAME)
    storage_path = f"{user_id}/cvs/{cv_name}.pdf"
    blob = bucket.blob(storage_path)
    
    blob.upload_from_filename(file_path)
    blob.make_public()  # Rendre le fichier accessible publiquement
    
    return blob.public_url


def generate_cv_endpoint(user_id: str, cv_name: str):
    """
    Génère un CV pour l'utilisateur authentifié
    
    Args:
        user_id (str): ID de l'utilisateur
        cv_name (str): Nom du CV à générer
        
    Returns:
        Response: Réponse HTTP avec les informations sur le CV généré
    """
    logger.info(f"Génération de CV pour user={user_id}, cv_name={cv_name}")
    
    try:
        # Récupérer l'utilisateur
        user = UserDocument.from_firestore_id(user_id)
        if not user:
            logger.warning(f"Utilisateur '{user_id}' non trouvé")
            return jsonify({"error": f"Utilisateur '{user_id}' introuvable"}), 404
        
        # Préparer la réponse de base
        response_data = {
            "user_id": user.id,
            "cv_name": cv_name,
            "timestamp": datetime.now().isoformat()
        }
        
        user_document = UserDocument.from_firestore_id(user_id)

        # Vérifier si le CV existe déjà
        cv_exists = any(cv.cv_name == cv_name for cv in user_document.cvs)
        if not cv_exists:
            # Créer un nouveau CV avec le nom spécifié
            new_cv = CV(cv_name=cv_name)
            user_document.cvs.append(new_cv)
            logger.info(f"Nouveau CV '{cv_name}' créé pour l'utilisateur '{user_id}'")

        cv_state = CVGenState.from_user_document(user_document, cv_name)
        
        result_state = generate_cv(cv_state)
        
        logger.info("Traitement terminé")
        
        # Mettre à jour le CV existant à partir du GlobalState résultant
        cv_info = user_document.update_cv_from_global_state(
            cv_name=cv_name,
            result_state=result_state,
            save_to_firestore=False  # Ne pas sauvegarder immédiatement
        )
        
        if not cv_info:
            logger.error(f"CV '{cv_name}' non trouvé pour mise à jour")
            return jsonify({"error": f"CV '{cv_name}' non trouvé pour mise à jour"}), 404
        
        # Générer le PDF et l'uploader directement vers Firebase Storage
        try:
            # Trouver le CV dans la liste des CVs
            cv = next((cv for cv in user_document.cvs if cv.cv_name == cv_name), None)
            if cv:
                # Utiliser NamedTemporaryFile pour gérer automatiquement la suppression du fichier temporaire
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=True) as tmp_file:
                    # Générer le PDF directement dans le fichier temporaire
                    generated_path = cv.cv_data.generate_pdf(tmp_file.name)
                    logger.info(f"PDF généré temporairement")
                    
                    # Uploader vers Firebase Storage
                    try:
                        storage_url = upload_to_firebase_storage(generated_path, user_id, cv_name)
                        logger.info(f"PDF uploadé vers Firebase Storage : {storage_url}")
                        response_data["pdf_url"] = storage_url
                    except Exception as storage_error:
                        logger.error(f"Erreur lors de l'upload vers Firebase Storage: {str(storage_error)}", exc_info=True)
                        response_data["storage_error"] = str(storage_error)
            else:
                logger.warning(f"CV '{cv_name}' non trouvé pour la génération du PDF")
        except Exception as e:
            logger.error(f"Erreur lors de la génération du PDF: {str(e)}", exc_info=True)
            response_data["pdf_error"] = str(e)
        
        # Sauvegarder explicitement l'utilisateur dans Firestore
        logger.info(f"Sauvegarde de l'utilisateur '{user_id}' avec le CV mis à jour dans Firestore")
        user_document.save()
        
        # Ajouter les informations du CV à la réponse
        response_data["updated_cv"] = cv_info
        response_data["firestore_updated"] = True
        
        logger.info(f"CV '{cv_name}' mis à jour avec succès pour l'utilisateur '{user_id}'")
        
        return jsonify({"success": True, "data": response_data}), 200
    
    except Exception as e:
        logger.error(f"Erreur lors de la génération du CV: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
