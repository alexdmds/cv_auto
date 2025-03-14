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
    Endpoint pour tester la génération de CV.
    Charge l'utilisateur avec l'ID 'model', adapte les données, 
    crée un GlobalState et le traite avec generate_cv.
    Sauvegarde ensuite les résultats dans l'utilisateur 'test_user'.
    
    Returns:
        Response: Réponse JSON avec les données du modèle et l'état global
    """
    # Récupérer le paramètre mock depuis la requête ou utiliser la valeur par défaut
    use_mock = request.args.get("mock", str(USE_MOCK)).lower() in ("true", "1", "t")
    
    try:
        logger.info(f"Génération de CV avec mock={use_mock}")
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
            logger.info("État global initial créé avec succès")
            
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
            
            # Ajouter des informations sur l'état global à la réponse
            response_data["global_state_info"] = {
                "initial": {
                    "name": global_state.head.name if hasattr(global_state, 'head') else "N/A",
                    "title": global_state.head.title_refined if hasattr(global_state, 'head') else "N/A",
                    "nb_experiences": len(global_state.experiences) if hasattr(global_state, 'experiences') else 0,
                    "nb_education": len(global_state.education) if hasattr(global_state, 'education') else 0
                },
                "result": {
                    "name": result_state.head.name if hasattr(result_state, 'head') else "N/A",
                    "title": result_state.head.title_refined if hasattr(result_state, 'head') else "N/A",
                    "nb_experiences": len(result_state.experiences) if hasattr(result_state, 'experiences') else 0,
                    "nb_education": len(result_state.education) if hasattr(result_state, 'education') else 0
                }
            }
            
            # Si nous avons des compétences générées, les ajouter à la réponse
            if hasattr(result_state, 'competences') and result_state.competences:
                response_data["competences"] = result_state.competences
            
            # Afficher l'état global résultant
            print("\nÉtat global traité avec succès:")
            print(f"- Nom: {response_data['global_state_info']['result']['name']}")
            print(f"- Titre: {response_data['global_state_info']['result']['title']}")
            print(f"- Expériences: {response_data['global_state_info']['result']['nb_experiences']}")
            print(f"- Éducations: {response_data['global_state_info']['result']['nb_education']}")
            
            if hasattr(result_state, 'competences') and result_state.competences:
                print("\nCompétences générées:")
                for category, skills in result_state.competences.items():
                    print(f"- {category}: {', '.join(skills)}")
            
            # Sauvegarder les résultats dans test_user
            try:
                # Obtenir ou créer l'utilisateur test_user
                test_user = UserModel.get_by_id("test_user")
                if not test_user:
                    logger.info("Création d'un nouvel utilisateur 'test_user'")
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
                
                logger.info(f"CV enregistré avec succès pour l'utilisateur 'test_user'")
                response_data["test_user_info"] = {
                    "id": test_user.id,
                    "cv_name": new_cv['cv_name'],
                    "saved": True
                }
                
                print(f"\nCV enregistré pour l'utilisateur 'test_user'")
                print(f"- Nom du CV: {new_cv['cv_name']}")
                
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde dans test_user: {str(e)}", exc_info=True)
                response_data["test_user_info"] = {
                    "saved": False,
                    "error": str(e)
                }
            
            return jsonify({"success": True, "data": response_data}), 200
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement: {str(e)}", exc_info=True)
            response_data["error"] = str(e)
            return jsonify({"error": "Erreur lors du traitement", "details": str(e), "data": response_data}), 500
            
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
        cv_data_adapted = cv_data_to_global_state_format(cv_data_original)
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
