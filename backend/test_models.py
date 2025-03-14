import datetime
import logging
import uuid
from pprint import pprint
from typing import Dict, List

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import direct des modèles
from backend.models import UserModel, CallModel, UsageModel, CvData, ProfileData

def test_user_model():
    """Teste les opérations CRUD sur UserModel avec la nouvelle structure"""
    
    # Générer un ID de test unique pour éviter les conflits
    test_id = f"test_user_{uuid.uuid4().hex[:8]}"
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    logger.info(f"Test du UserModel avec ID: {test_id}")
    
    # 1. Création d'un utilisateur avec la nouvelle structure
    profile_data = {
        "head": {
            "name": "Utilisateur Test",
            "title": "Développeur Full Stack",
            "mail": test_email,
            "phone": "+33612345678",
            "linkedin_url": "https://linkedin.com/in/test-user"
        },
        "educations": [
            {
                "title": "Master Informatique",
                "full_description": "Spécialisation en développement web et mobile",
                "dates": "2015-2017",
                "university": "Université de Paris"
            }
        ],
        "experiences": [
            {
                "title": "Développeur Full Stack",
                "company": "Tech Company",
                "dates": "2018-2023",
                "location": "Paris, France",
                "full_descriptions": "Développement d'applications web et mobiles"
            }
        ],
        "skills": "Python, JavaScript, React, Node.js",
        "languages": "Français (natif), Anglais (courant)",
        "hobbies": "Randonnée, photographie, lecture"
    }
    
    cv_data = {
        "cv_name": "CV Test",
        "job_raw": "Développeur Full Stack Senior",
        "name": "Utilisateur Test",
        "title": "Développeur Full Stack Senior",
        "mail": test_email,
        "phone": "+33612345678",
        "lang_of_cv": "fr",
        "educations": [
            {
                "title": "Master Informatique",
                "description": "Spécialisation en développement web",
                "dates": "2015-2017",
                "university": "Université de Paris",
                "location": "Paris, France"
            }
        ],
        "experiences": [
            {
                "title": "Développeur Full Stack",
                "company": "Tech Company",
                "dates": "2018-2023",
                "location": "Paris, France",
                "bullets": ["Développement d'applications web avec React/Node.js", 
                           "Mise en place d'une CI/CD avec GitHub Actions"]
            }
        ],
        "skills": [
            {
                "category_name": "Langages de programmation",
                "skills": "Python, JavaScript, TypeScript"
            },
            {
                "category_name": "Frameworks",
                "skills": "React, Node.js, Express"
            }
        ],
        "languages": [
            {
                "language": "Français",
                "level": "Natif"
            },
            {
                "language": "Anglais",
                "level": "Courant (TOEIC 950)"
            }
        ],
        "hobbies": "Randonnée, photographie, lecture"
    }
    
    user = UserModel(
        email=test_email,
        name="Utilisateur Test",
        created_at=datetime.datetime.now(),
        profile=profile_data,
        cvs=[cv_data]
    )
    
    # 2. Sauvegarde de l'utilisateur
    user_id = user.save(test_id)
    logger.info(f"Utilisateur créé avec ID: {user_id}")
    
    # 3. Récupération de l'utilisateur par ID
    retrieved_user = UserModel.get_by_id(test_id)
    logger.info("Utilisateur récupéré par ID")
    logger.info(f"Nom: {retrieved_user.name}")
    logger.info(f"Email: {retrieved_user.email}")
    logger.info(f"Nombre de CVs: {len(retrieved_user.cvs)}")
    
    # 4. Test de get_user_data
    logger.info("Test de get_user_data:")
    user_data = UserModel.get_user_data(test_id)
    logger.info(f"Clés disponibles dans les données: {list(user_data.keys())}")
    
    # 5. Mise à jour du profil
    logger.info("Test de mise à jour du profil:")
    new_profile = retrieved_user.profile.copy()
    new_profile["head"]["title"] = "Développeur Full Stack Senior"
    retrieved_user.update_profile(new_profile)
    
    # 6. Ajout d'un nouveau CV
    logger.info("Test d'ajout d'un nouveau CV:")
    new_cv = {
        "cv_name": "CV Test 2",
        "job_raw": "Architecte Logiciel",
        "name": "Utilisateur Test",
        "title": "Architecte Logiciel"
    }
    cv_index = retrieved_user.add_cv(new_cv)
    logger.info(f"Nouveau CV ajouté à l'index: {cv_index}")
    
    # 7. Vérification des mises à jour
    updated_user = UserModel.get_by_id(test_id)
    logger.info(f"Nouveau titre dans le profil: {updated_user.profile['head']['title']}")
    logger.info(f"Nombre de CVs après ajout: {len(updated_user.cvs)}")
    logger.info(f"Nom du nouveau CV: {updated_user.cvs[1]['cv_name']}")
    
    return test_id, user

def test_call_model(user_id):
    """Teste les opérations CRUD sur CallModel avec la nouvelle structure"""
    
    logger.info(f"Test du CallModel pour l'utilisateur: {user_id}")
    
    # 1. Création d'un appel avec la nouvelle structure
    call = CallModel(
        user_id=user_id,
        endpoint="generate_profile",
        call_time=datetime.datetime.now(),
        usage_count=5,
        metadata={"source": "test_script"}
    )
    
    # 2. Sauvegarde de l'appel
    call_id = call.save()
    logger.info(f"Appel créé avec ID: {call_id}")
    
    # 3. Récupération de l'appel par ID
    retrieved_call = CallModel.get_by_id(call_id)
    logger.info("Appel récupéré par ID:")
    logger.info(f"Endpoint: {retrieved_call.endpoint}")
    logger.info(f"Usage count: {retrieved_call.usage_count}")
    
    # 4. Récupération des appels de l'utilisateur
    user_calls = CallModel.get_by_user_id(user_id)
    logger.info(f"Nombre d'appels pour l'utilisateur: {len(user_calls)}")
    
    return call_id, call

def test_usage_model(user_id):
    """Teste les opérations CRUD sur UsageModel avec la nouvelle structure"""
    
    logger.info(f"Test du UsageModel pour l'utilisateur: {user_id}")
    
    # 1. Création d'un usage avec la nouvelle structure
    usage = UsageModel(
        user_id=user_id,
        last_request_time=datetime.datetime.now(),
        total_usage=5
    )
    
    # 2. Sauvegarde de l'usage
    usage_id = usage.save()
    logger.info(f"Usage créé avec ID: {usage_id}")
    
    # 3. Récupération de l'usage par ID
    retrieved_usage = UsageModel.get_by_id(usage_id)
    logger.info("Usage récupéré par ID:")
    logger.info(f"Total usage: {retrieved_usage.total_usage}")
    
    # 4. Récupération de l'usage de l'utilisateur
    user_usage = UsageModel.get_by_user_id(user_id)
    if user_usage:
        logger.info(f"Usage récupéré par user_id: {user_usage.total_usage}")
    
    # 5. Incrémentation de l'usage
    if user_usage:
        user_usage.increment_usage(10)
        logger.info("Usage incrémenté de 10")
        
        # Vérification de l'incrémentation
        updated_usage = UsageModel.get_by_id(usage_id)
        logger.info(f"Usage après incrémentation: {updated_usage.total_usage}")
    
    return usage_id, usage

def cleanup(user_id, call_id, usage_id):
    """Nettoie les données de test"""
    
    logger.info("Nettoyage des données de test...")
    
    # Supprimer l'usage
    usage = UsageModel.get_by_id(usage_id)
    if usage:
        usage.delete()
        logger.info(f"Usage {usage_id} supprimé")
    
    # Supprimer l'appel
    call = CallModel.get_by_id(call_id)
    if call:
        call.delete()
        logger.info(f"Appel {call_id} supprimé")
    
    # Supprimer l'utilisateur
    user = UserModel.get_by_id(user_id)
    if user:
        user.delete()
        logger.info(f"Utilisateur {user_id} supprimé")

def test_model_user_schema():
    """Teste spécifiquement l'accès à l'utilisateur 'model' et vérifie sa structure"""
    logger.info("Test de l'accès à l'utilisateur 'model'...")
    
    # Récupérer les données brutes
    raw_data = UserModel.get_user_data("model")
    if not raw_data:
        logger.warning("Aucune donnée trouvée pour l'utilisateur 'model'")
        return
    
    logger.info(f"Clés disponibles dans les données: {list(raw_data.keys())}")
    
    # Tester l'accès aux différentes structures
    if 'cvs' in raw_data:
        logger.info(f"Nombre de CVs dans 'model': {len(raw_data['cvs'])}")
        for i, cv in enumerate(raw_data['cvs']):
            logger.info(f"CV #{i+1} - Nom: {cv.get('cv_name', 'N/A')}")
    
    if 'profile' in raw_data:
        logger.info("Données de profil trouvées")
        profile = raw_data['profile']
        head = profile.get('head', {})
        logger.info(f"Nom dans le profil: {head.get('name', 'N/A')}")
        logger.info(f"Nombre d'expériences: {len(profile.get('experiences', []))}")
    
    if 'cv_data' in raw_data:
        logger.info("Données cv_data trouvées (format legacy)")
    
    # Tester l'instanciation avec UserModel
    model_user = UserModel.get_by_id("model")
    if model_user:
        logger.info(f"UserModel 'model' récupéré - ID: {model_user.id}")
    
    return model_user if model_user else None

def main():
    """Fonction principale exécutant tous les tests"""
    
    logger.info("Démarrage des tests de models.py avec la nouvelle structure")
    
    try:
        # Test spécifique sur l'utilisateur 'model'
        test_model_user_schema()
        
        # Tests généraux des modèles
        user_id, user = test_user_model()
        call_id, call = test_call_model(user_id)
        usage_id, usage = test_usage_model(user_id)
        
        # Nettoyage
        cleanup(user_id, call_id, usage_id)
        
        logger.info("Tests terminés avec succès")
        
    except Exception as e:
        logger.error(f"Erreur pendant les tests: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main()) 