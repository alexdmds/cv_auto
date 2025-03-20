from flask import jsonify, request
import logging
from backend.models import UserDocument
from ai_module.lg_models import CVGenState
from datetime import datetime
from backend.config import load_config
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
    Endpoint pour générer un CV optimisé.
    
    Paramètres de requête:
        - user: ID de l'utilisateur (par défaut: 'test_user')
        - cv_name: Nom du CV à générer (par défaut: 'cv_test')
        - mock: Override l'utilisation du mock (optionnel)
    
    Returns:
        Response: Réponse JSON avec les détails et le statut de la génération
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
        
        # Créer le GlobalState directement à partir de l'utilisateur et du nom du CV
        global_state = GlobalState.from_user_document(user, cv_name)
        
        if not global_state:
            logger.warning(f"CV '{cv_name}' non trouvé ou sans données pour l'utilisateur '{user_id}'")
            return jsonify({"error": f"CV '{cv_name}' introuvable ou sans données pour l'utilisateur '{user_id}'"}), 404
        
        logger.info("État global initial créé avec succès")
        
        result_state = generate_cv(global_state)
        
        logger.info("Traitement terminé")
        
        # Mettre à jour le CV existant à partir du GlobalState résultant
        cv_info = user.update_cv_from_global_state(
            cv_name=cv_name,
            result_state=result_state,
            save_to_firestore=False  # Ne pas sauvegarder immédiatement
        )
        
        if not cv_info:
            logger.error(f"CV '{cv_name}' non trouvé pour mise à jour")
            return jsonify({"error": f"CV '{cv_name}' non trouvé pour mise à jour"}), 404
        
        # Sauvegarder explicitement l'utilisateur dans Firestore
        logger.info(f"Sauvegarde de l'utilisateur '{user_id}' avec le CV mis à jour dans Firestore")
        user.save()
        
        # Ajouter les informations du CV à la réponse
        response_data["updated_cv"] = cv_info
        response_data["firestore_updated"] = True
        
        logger.info(f"CV '{cv_name}' mis à jour avec succès pour l'utilisateur '{user_id}'")
        
        return jsonify({"success": True, "data": response_data}), 200
    
    except Exception as e:
        logger.error(f"Erreur lors de la génération du CV: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
