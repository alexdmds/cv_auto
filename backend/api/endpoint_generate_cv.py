from flask import jsonify
import logging
from backend.models import UserModel
from ai_module.new_models.lg_models import GlobalState
from backend.utils.adapters import cv_data_to_global_state_format

logger = logging.getLogger(__name__)

def generate_cv_endpoint():
    """
    Endpoint pour tester la génération de CV.
    Charge l'utilisateur avec l'ID 'model', adapte les données et crée un GlobalState.
    
    Returns:
        Response: Réponse JSON avec les données du modèle et l'état global
    """
    try:
        logger.info("Chargement de l'utilisateur avec ID 'model'")
        
        # Récupérer l'utilisateur modèle
        model_user = UserModel.get_by_id("model")
        
        if not model_user:
            logger.warning("Aucune donnée trouvée pour l'utilisateur 'model'")
            return jsonify({"error": "Aucune donnée trouvée pour l'utilisateur"}), 404

        # Préparer les données à renvoyer
        response_data = {
            "user_id": model_user.id,
            "user_name": getattr(model_user, 'name', 'N/A'),
            "has_cvs": hasattr(model_user, "cvs") and model_user.cvs
        }
        
        # Afficher des informations sur le modèle
        print(f"Utilisateur 'model' récupéré:")
        print(f"- ID: {model_user.id}")
        print(f"- Nom: {getattr(model_user, 'name', 'N/A')}")
        
        # Vérifier si l'utilisateur a des CVs
        if not response_data["has_cvs"]:
            logger.warning("L'utilisateur 'model' n'a pas de CVs")
            return jsonify({"warning": "L'utilisateur n'a pas de CVs", "data": response_data}), 200
        
        # Obtenir le premier CV
        first_cv = model_user.cvs[0]
        cv_name = first_cv.get('cv_name', 'Sans nom')
        print(f"\nUtilisation du CV: {cv_name}")
        
        # Vérifier si le CV contient cv_data
        if 'cv_data' not in first_cv:
            logger.warning(f"Le CV '{cv_name}' ne contient pas de champ cv_data")
            return jsonify({"warning": "Le CV ne contient pas de données cv_data", "data": response_data}), 200
        
        # Extraire les données du CV et les adapter au format GlobalState
        cv_data_original = first_cv['cv_data']
        print(f"Structure de cv_data original: {list(cv_data_original.keys())}")
        
        # Adapter les données au format GlobalState
        cv_data_adapted = cv_data_to_global_state_format(cv_data_original)
        print(f"Structure de cv_data adapté: {list(cv_data_adapted.keys())}")
        
        try:
            # Créer le GlobalState avec les données adaptées
            global_state = GlobalState.from_json(cv_data_adapted)
            logger.info("État global créé avec succès")
            
            # Ajouter des informations sur l'état global à la réponse
            response_data["global_state_info"] = {
                "name": global_state.head.name if hasattr(global_state, 'head') else "N/A",
                "title": global_state.head.title_refined if hasattr(global_state, 'head') else "N/A",
                "nb_experiences": len(global_state.experiences) if hasattr(global_state, 'experiences') else 0,
                "nb_education": len(global_state.education) if hasattr(global_state, 'education') else 0
            }
            
            # Afficher l'état global
            print("\nÉtat global créé avec succès:")
            print(f"- Nom: {response_data['global_state_info']['name']}")
            print(f"- Titre: {response_data['global_state_info']['title']}")
            print(f"- Expériences: {response_data['global_state_info']['nb_experiences']}")
            print(f"- Éducations: {response_data['global_state_info']['nb_education']}")
            
            return jsonify({"success": True, "data": response_data}), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du GlobalState: {str(e)}", exc_info=True)
            response_data["conversion_error"] = str(e)
            return jsonify({"error": "Erreur lors de la création du GlobalState", "details": str(e), "data": response_data}), 500
            
    except Exception as e:
        logger.error(f"Erreur lors de la génération du CV: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Test manuel de la fonction
    try:
        # Initialiser Firebase si nécessaire
        UserModel.initialize_firebase()
        
        # Récupérer l'utilisateur modèle
        model_user = UserModel.get_by_id("model")
        
        if not model_user:
            print("Aucune donnée trouvée pour l'utilisateur 'model'")
            exit(1)
            
        print(f"Utilisateur 'model' trouvé - ID: {model_user.id}")
        
        # Vérifier si l'utilisateur a des CVs
        if not hasattr(model_user, "cvs") or not model_user.cvs:
            print("L'utilisateur 'model' n'a pas de CVs")
            exit(1)
            
        # Afficher les informations sur les CVs
        print(f"Nombre de CVs: {len(model_user.cvs)}")
        
        # Obtenir le premier CV
        first_cv = model_user.cvs[0]
        cv_name = first_cv.get('cv_name', 'Sans nom')
        print(f"Utilisation du CV: {cv_name}")
        
        # Vérifier si le CV contient cv_data
        if 'cv_data' not in first_cv:
            print(f"Le CV '{cv_name}' ne contient pas de champ cv_data")
            print(f"Clés disponibles: {list(first_cv.keys())}")
            exit(1)
            
        # Extraire et adapter les données
        cv_data_original = first_cv['cv_data']
        print(f"Structure de cv_data original: {list(cv_data_original.keys())}")
        
        # Adapter les données au format GlobalState
        cv_data_adapted = cv_data_to_global_state_format(cv_data_original)
        print(f"Structure de cv_data adapté: {list(cv_data_adapted.keys())}")
        
        # Essayer de créer un GlobalState
        try:
            global_state = GlobalState.from_json(cv_data_adapted)
            print("\nGlobalState créé avec succès!")
            if hasattr(global_state, 'head'):
                print(f"- Nom: {global_state.head.name}")
                print(f"- Titre: {global_state.head.title_refined}")
            if hasattr(global_state, 'experiences'):
                print(f"- Nombre d'expériences: {len(global_state.experiences)}")
            if hasattr(global_state, 'education'):
                print(f"- Nombre d'éducations: {len(global_state.education)}")
        except Exception as e:
            print(f"Erreur lors de la création du GlobalState: {e}")
            
    except Exception as e:
        print(f"Erreur de test: {e}")
