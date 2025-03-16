from flask import jsonify, request
from google.cloud import storage
import logging
from backend.config import load_config
from dotenv import load_dotenv
import os
import asyncio
from firebase_admin import firestore
from backend.utils_secu import increment_token_usage

load_dotenv()
logger = logging.getLogger(__name__)
config = load_config()

# Import conditionnel basé sur la configuration
if config.MOCK_OPENAI:
    from ai_module.mock_inference import generate_profile, generate_head
else:
    from ai_module.inference import generate_profile, generate_head

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
        
        # Récupérer les fichiers depuis le bucket
        bucket = storage.Client().bucket(config.BUCKET_NAME)
        text_files = []
        
        for blob in bucket.list_blobs(prefix=f"{user_id}/sources/"):
            if blob.name.endswith(".txt"):
                content = blob.download_as_string().decode("utf-8")
                text_files.append(content)
        
        if not text_files:
            logger.warning(f"Aucun fichier texte trouvé pour l'utilisateur {user_id}")
            return jsonify({"error": "No text files found"}), 404

        # Concaténer tous les textes
        text_to_analyze = "\n\n".join(text_files)
        
        # Générer le profil et l'en-tête
        profile = asyncio.run(generate_profile(text_to_analyze))
        head = asyncio.run(generate_head(text_to_analyze))

        # Calculer le nombre total de tokens
        input_text = text_to_analyze
        output_text = str(profile) + str(head)
        total_tokens = len(input_text.split()) + len(output_text.split())
        
        # Incrémenter l'utilisation des tokens
        increment_token_usage(user_id, total_tokens)
        logger.info(f"Tokens utilisés pour {user_id}: {total_tokens}")

        # Structurer les données selon le format demandé
        cv_data = {
            'head': {
                'name': head.get('name', ''),
                'phone': head.get('phone', ''),
                'email': head.get('email', ''),
                'general_title': head.get('general_title', '')
            },
            'experiences': {
                'experiences': profile.get('experiences', [])
            },
            'education': {
                'educations': profile.get('education', [])
            },
            'skills': {
                'description': head.get('skills', '')
            },
            'hobbies': {
                'description': head.get('hobbies', '')
            },
            'languages': {
                'description': head.get('langues', '')
            }
        }

        # Sauvegarder dans Firestore
        db = firestore.Client()
        doc_ref = db.collection('users').document(user_id)
        doc_ref.set({
            'cv_data': cv_data
        }, merge=True)
        
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
