from flask import jsonify, request
import logging
from backend.models import UserModel
from ai_module.new_models.lg_models import GlobalState
from backend.utils.adapters import cv_data_to_global_state_format
import os
import datetime

# Import conditionnel selon l'environnement
USE_MOCK = os.environ.get("USE_MOCK", "True").lower() in ("true", "1", "t")
if USE_MOCK:
    from ai_module.mock_inference import generate_cv as generate_cv_impl
    logger = logging.getLogger(__name__)
    logger.info("Utilisation de l'implémentation MOCK de generate_cv")
else:
    from ai_module.inference import generate_cv as generate_cv_impl
    logger = logging.getLogger(__name__)
    logger.info("Utilisation de l'implémentation RÉELLE de generate_cv")

def generate_cv_endpoint():
    """
    Endpoint pour générer un CV optimisé.
    
    Paramètres de requête:
        - user: ID de l'utilisateur (par défaut: 'test_user')
        - cv_name: Nom du CV à générer (par défaut: 'cv_test')
        - mock: Override l'utilisation du mock (optionnel)
    
    Returns:
        Response: Réponse JSON avec les détails et le statut de la génération
    """
    # Récupérer les paramètres de la requête
    user_id = request.args.get("user", "test_user")
    cv_name = request.args.get("cv_name", "cv_test")
    use_mock = request.args.get("mock", str(USE_MOCK)).lower() in ("true", "1", "t")
    
    logger.info(f"Génération de CV pour user={user_id}, cv_name={cv_name}, mock={use_mock}")
    
    try:
        # Récupérer l'utilisateur
        user = UserModel.get_by_id(user_id)
        if not user:
            logger.warning(f"Utilisateur '{user_id}' non trouvé")
            return jsonify({"error": f"Utilisateur '{user_id}' introuvable"}), 404
        
        # Préparer la réponse de base
        response_data = {
            "user_id": user.id,
            "cv_name": cv_name,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Créer le GlobalState directement à partir de l'utilisateur et du nom du CV
        global_state = cv_data_to_global_state_format(user, cv_name)
        
        if not global_state:
            logger.warning(f"CV '{cv_name}' non trouvé ou sans données pour l'utilisateur '{user_id}'")
            return jsonify({"error": f"CV '{cv_name}' introuvable ou sans données pour l'utilisateur '{user_id}'"}), 404
        
        logger.info("État global initial créé avec succès")
        
        # Trouver le CV original pour référence
        target_cv = None
        for cv in user.cvs:
            if cv.get("cv_name") == cv_name:
                target_cv = cv
                break
        
        cv_data_original = target_cv['cv_data']
        
        # Appeler la fonction generate_cv (mock ou réelle selon la configuration)
        if use_mock:
            from ai_module.mock_inference import generate_cv as generate_cv_mock
            logger.info("Application du traitement MOCK")
            result_state = generate_cv_mock(global_state)
        else:
            from ai_module.inference import generate_cv as generate_cv_real
            logger.info("Application du traitement RÉEL")
            result_state = generate_cv_real(global_state)
        
        logger.info("Traitement terminé")
        
        # Créer un nouveau CV à partir du GlobalState résultant
        cv_info = user.create_cv_from_global_state(
            result_state=result_state,
            original_cv_name=cv_name,
            original_cv_data=cv_data_original
        )
        
        # Ajouter les informations du CV à la réponse
        response_data["new_cv"] = cv_info
        
        logger.info(f"CV optimisé '{cv_info['name']}' créé avec succès pour l'utilisateur '{user_id}'")
        
        return jsonify({"success": True, "data": response_data}), 200
    
    except Exception as e:
        logger.error(f"Erreur lors de la génération du CV: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Test manuel de la fonction
    try:
        # Configuration du logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Initialiser Firebase si nécessaire
        UserModel.initialize_firebase()
        
        # Indiquer si on utilise le mock ou l'implémentation réelle
        print(f"Mode d'exécution: {'MOCK' if USE_MOCK else 'RÉEL'}")
        
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
        cv_data_adapted = cv_data_to_global_state_format(model_user, cv_name)
        print(f"Structure de cv_data adapté: {list(cv_data_adapted.keys())}")
        
        # Essayer de créer un GlobalState
        try:
            global_state = GlobalState.from_json(cv_data_adapted)
            print("\nGlobalState créé avec succès!")
            
            # Afficher des informations sur l'état global initial
            if hasattr(global_state, 'head'):
                print(f"- Nom: {global_state.head.name}")
                print(f"- Titre: {global_state.head.title_refined}")
            if hasattr(global_state, 'experiences'):
                print(f"- Nombre d'expériences: {len(global_state.experiences)}")
            if hasattr(global_state, 'education'):
                print(f"- Nombre d'éducations: {len(global_state.education)}")
            
            # Appliquer le traitement
            print("\nApplication du traitement...")
            if USE_MOCK:
                from ai_module.mock_inference import generate_cv
                print("Utilisation du MOCK")
            else:
                from ai_module.inference import generate_cv
                print("Utilisation de l'implémentation RÉELLE")
                
            result_state = generate_cv(global_state)
            
            # Afficher le résultat
            print("\nTraitement terminé avec succès!")
            
            if hasattr(result_state, 'competences'):
                print("\nCompétences générées:")
                for category, skills in result_state.competences.items():
                    print(f"- {category}: {', '.join(skills)}")
            
            # Sauvegarder dans test_user
            try:
                # Obtenir ou créer l'utilisateur test_user
                test_user = UserModel.get_by_id("test_user")
                if not test_user:
                    print("Création d'un nouvel utilisateur 'test_user'")
                    test_user = UserModel(id="test_user", name="Test User")
                
                # Créer un nouveau CV avec les données traitées
                new_cv = {
                    'cv_name': f"CV généré le {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    'job_raw': getattr(result_state, 'job_raw', '') or getattr(global_state, 'job_raw', ''),
                    'creation_date': datetime.datetime.now().isoformat(),
                    'cv_data': {
                        'name': result_state.head.name,
                        'title': result_state.head.title_refined,
                        'mail': result_state.head.mail,
                        'phone': result_state.head.tel_refined,
                        'lang_of_cv': cv_data_original.get('lang_of_cv', 'fr'),
                        'sections_name': cv_data_original.get('sections_name', {
                            'experience_section_name': 'Expérience Professionnelle',
                            'education_section_name': 'Formation',
                            'skills_section_name': 'Compétences',
                            'languages_section_name': 'Langues',
                            'hobbies_section_name': 'Centres d\'intérêt'
                        }),
                        'experiences': [],
                        'educations': [],
                        'skills': [],
                        'languages': [],
                        'hobbies': ''
                    }
                }
                
                # Ajouter les expériences
                if hasattr(result_state, 'experiences'):
                    for exp in result_state.experiences:
                        experience = {
                            'title': exp.title_refined,
                            'company': exp.company_refined,
                            'dates': exp.dates_refined,
                            'location': exp.location_refined,
                            'bullets': exp.bullets if hasattr(exp, 'bullets') and exp.bullets else []
                        }
                        new_cv['cv_data']['experiences'].append(experience)
                
                # Ajouter les formations
                if hasattr(result_state, 'education'):
                    new_cv['cv_data']['educations'] = []
                    for edu in result_state.education:
                        education = {
                            'title': edu.degree_refined,
                            'university': edu.institution_refined,
                            'dates': edu.dates_refined,
                            'location': edu.location_refined,
                            'description': edu.description_refined
                        }
                        new_cv['cv_data']['educations'].append(education)
                
                # Ajouter les compétences
                if hasattr(result_state, 'competences') and result_state.competences:
                    new_cv['cv_data']['skills'] = []
                    for category, skills in result_state.competences.items():
                        skill_category = {
                            'category_name': category,
                            'skills': ', '.join(skills) if isinstance(skills, list) else skills
                        }
                        new_cv['cv_data']['skills'].append(skill_category)
                
                # Ajouter les langues
                if hasattr(result_state, 'langues'):
                    new_cv['cv_data']['languages'] = []
                    for langue in result_state.langues:
                        # Gérer à la fois les objets Pydantic et les dictionnaires
                        try:
                            # Si c'est un objet Pydantic
                            if hasattr(langue, 'language') and hasattr(langue, 'level'):
                                language = {
                                    'language': getattr(langue, 'language', ''),
                                    'level': getattr(langue, 'level', '')
                                }
                            # Si c'est un dictionnaire
                            elif isinstance(langue, dict):
                                language = {
                                    'language': langue.get('language', ''),
                                    'level': langue.get('level', '')
                                }
                            # Pour tout autre type, créer un dictionnaire vide
                            else:
                                logger.warning(f"Type de langue non reconnu: {type(langue)}")
                                language = {
                                    'language': str(langue),
                                    'level': ''
                                }
                            new_cv['cv_data']['languages'].append(language)
                        except Exception as lang_err:
                            logger.error(f"Erreur lors du traitement d'une langue: {lang_err}")
                            # Continuer avec la langue suivante
                            continue
                
                # Ajouter les hobbies
                if hasattr(result_state, 'hobbies_refined'):
                    new_cv['cv_data']['hobbies'] = result_state.hobbies_refined
                
                # Ajouter le CV à l'utilisateur test_user
                if not hasattr(test_user, 'cvs'):
                    test_user.cvs = []
                
                test_user.cvs.append(new_cv)
                
                # Sauvegarder l'utilisateur
                test_user.save()
                
                print(f"\nCV enregistré pour l'utilisateur 'test_user'")
                print(f"- Nom du CV: {new_cv['cv_name']}")
                
            except Exception as e:
                print(f"Erreur lors de la sauvegarde dans test_user: {e}")
            
        except Exception as e:
            print(f"Erreur lors du traitement: {e}")
            
    except Exception as e:
        print(f"Erreur de test: {e}")
