from flask import jsonify, request
from google.cloud import storage
import logging
from backend.config import load_config
from dotenv import load_dotenv
import os
import asyncio
from firebase_admin import firestore
from ai_module.lg_models import ProfileState
from backend.utils.utils_gcs import get_concatenated_text_files

load_dotenv()
logger = logging.getLogger(__name__)
config = load_config()

# Import conditionnel basé sur la configuration
if config.MOCK_OPENAI:
    from ai_module.mock_inference import generate_profile
else:
    from ai_module.inference import generate_profile

def generate_profile_endpoint(user_id: str):
    """
    Endpoint pour générer un profil structuré.
    
    Args:
        user_id (str): ID de l'utilisateur
        
    Returns:
        Response: Réponse JSON avec le profil généré
    """
    try:
        logger.info(f"Génération du profil pour l'utilisateur {user_id}")
        
        text_to_analyze = get_concatenated_text_files(user_id)
        
        profile_state = ProfileState(input_text=text_to_analyze)

        result_state = generate_profile(profile_state)

        logger.info(f"Profil et en-tête générés et sauvegardés pour l'utilisateur {user_id}")
        return jsonify({
            "success": True, 
            "cv_data": cv_data
        }), 200

    except Exception as e:
        logger.error(f"Erreur lors de la génération du profil: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import asyncio
    
    # Exemple de texte pour tester
    texte_test = """
    Jean-Michel Dupont
    Architecte Solutions & Lead Developer
    Email: jm.dupont@email.com | Tel: 06 12 34 56 78
    LinkedIn: linkedin.com/in/jmdupont

    Expert en architecture logicielle et développement full-stack avec 12 ans d'expérience 
    dans la conception et le déploiement de solutions cloud à grande échelle. 
    Passionné par l'innovation technologique et le leadership technique.

    Compétences: 
    - Backend: Python, Java, Node.js, GraphQL, REST APIs
    - Frontend: React, Vue.js, TypeScript, HTML5/CSS3
    - Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD, Terraform
    - Base de données: PostgreSQL, MongoDB, Redis
    - Management: Gestion d'équipe, Méthodologies Agiles, Formation technique

    Langues:
    - Français (Langue maternelle)
    - Anglais (Bilingue, TOEIC 985/990)
    - Allemand (Niveau C1, séjour de 2 ans à Berlin)
    - Espagnol (Niveau B2)

    Centres d'intérêt: 
    - Photographie (exposition amateur 2022)
    - Musique (guitariste dans un groupe de jazz)
    - Course à pied (semi-marathon de Paris 2023)
    - Contribution open source (maintainer sur 3 projets Python)
    """
    
    async def test_generation():
        try:
            profil = await generate_profile(texte_test)
            head = await generate_head(texte_test)
            print("Profil généré avec succès:")
            print(profil)
            print("En-tête généré avec succès:")
            print(head)
        except Exception as e:
            print(f"Erreur lors du test: {e}")
    
    # Exécution du test
    asyncio.run(test_generation())
