from flask import jsonify, request
import logging
from backend.models import UserDocument, CV, CallDocument, UsageDocument
from ai_module.lg_models import CVGenState
from datetime import datetime
from backend.config import load_config
from backend.utils.utils_gcs import upload_to_firebase_storage
config = load_config()
logger = logging.getLogger(__name__)

# Import conditionnel basé sur la configuration
if config.MOCK_OPENAI:
    from ai_module.mock_inference import generate_cv
    logger.info("Utilisation de l'implémentation MOCK de generate_cv")
else:
    from ai_module.inference import generate_cv
    logger.info("Utilisation de l'implémentation RÉELLE de generate_cv")



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
        # Créer un document d'appel et incrémenter l'usage
        CallDocument.create_call(user_id, "generate_cv")
        usage_doc = UsageDocument.get_or_create(user_id)
        usage_doc.increment_usage()
        
        # Récupérer l'utilisateur
        user_document = UserDocument.from_firestore_id(user_id)
        if not user_document:
            logger.warning(f"Utilisateur '{user_id}' non trouvé")
            return jsonify({"error": f"Utilisateur '{user_id}' introuvable"}), 404
        
        # Vérifier si le CV existe
        existing_cv = next((cv for cv in user_document.cvs if cv.cv_name == cv_name), None)
        if not existing_cv:
            logger.warning(f"CV '{cv_name}' non trouvé pour l'utilisateur '{user_id}'")
            return jsonify({
                "error": "CV introuvable",
                "message": f"Le CV '{cv_name}' n'existe pas pour cet utilisateur"
            }), 404
            
        # Vérifier si le CV a une fiche de poste
        if not existing_cv.job_raw.strip():
            logger.warning(f"CV '{cv_name}' trouvé mais sans fiche de poste")
            return jsonify({
                "error": "Impossible de générer le CV sans fiche de poste",
                "message": "Veuillez fournir une fiche de poste pour ce CV avant de le générer"
            }), 400
        
        # Préparer la réponse de base
        response_data = {
            "user_id": user_document.id,
            "cv_name": cv_name,
            "timestamp": datetime.now().isoformat()
        }

        # Générer le CV
        cv_state = CVGenState.from_user_document(user_document, cv_name)
        result_state = generate_cv(cv_state)
        logger.info("Traitement terminé")
        
        # Mettre à jour le CV existant à partir du CVGenState résultant
        cv_info = user_document.update_cv_from_cv_state(
            cv_name=cv_name,
            cv_state=result_state,
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
                # Utiliser NamedTemporaryFile avec delete=False pour garder le fichier jusqu'à l'upload
                import tempfile
                import os
                
                tmp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
                try:
                    # Générer le PDF directement dans le fichier temporaire
                    generated_path = cv.cv_data.generate_pdf(tmp_file.name, user_id=user_id)
                    logger.info(f"PDF généré temporairement")
                    
                    # Uploader vers Firebase Storage
                    try:
                        storage_url = upload_to_firebase_storage(generated_path, user_id, cv_name)
                        logger.info(f"PDF uploadé vers Firebase Storage : {storage_url}")
                        response_data["pdf_url"] = storage_url
                    except Exception as storage_error:
                        logger.error(f"Erreur lors de l'upload vers Firebase Storage: {str(storage_error)}", exc_info=True)
                        response_data["storage_error"] = str(storage_error)
                finally:
                    # Supprimer le fichier temporaire après l'upload
                    try:
                        os.unlink(tmp_file.name)
                    except Exception as e:
                        logger.warning(f"Erreur lors de la suppression du fichier temporaire: {str(e)}")
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
        
        # Retourner la réponse avec succès
        return jsonify({
            "success": True,
            "data": response_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du CV: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
