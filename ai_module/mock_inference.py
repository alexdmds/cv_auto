import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def generate_profile(text: str) -> Dict[str, Any]:
    """
    Mock de la fonction generate_profile qui retourne un profil structuré statique.
    
    Args:
        text (str): Le texte brut (non utilisé dans le mock)
        
    Returns:
        Dict[str, Any]: Un profil structuré statique pour les tests
    """
    logger.info("Utilisation du mock generate_profile")
    
    return {
        "experiences": [
            {
                "intitule": "Développeur Senior",
                "dates": "2020-2023",
                "etablissement": "Tech Company",
                "lieu": "Paris",
                "description": "Développement d'applications web avec React et Node.js. Lead technique sur 3 projets majeurs."
            },
            {
                "intitule": "Développeur Full Stack",
                "dates": "2018-2020",
                "etablissement": "StartupCo",
                "lieu": "Lyon",
                "description": "Développement full stack avec Python et Vue.js. Mise en place de l'architecture microservices."
            }
        ],
        "education": [
            {
                "intitule": "Master Informatique",
                "dates": "2016-2018",
                "etablissement": "Université de Paris",
                "lieu": "Paris",
                "description": "Spécialisation en développement web. Major de promotion."
            },
            {
                "intitule": "Licence Informatique",
                "dates": "2013-2016",
                "etablissement": "Université de Lyon",
                "lieu": "Lyon",
                "description": "Formation généraliste en informatique. Projet de fin d'études sur le machine learning."
            }
        ]
    }

async def generate_head(text: str) -> Dict[str, Any]:
    """
    Mock de la fonction generate_head qui retourne un en-tête structuré statique.
    
    Args:
        text (str): Le texte brut (non utilisé dans le mock)
        
    Returns:
        Dict[str, Any]: Un en-tête structuré statique pour les tests
    """
    logger.info("Utilisation du mock generate_head")
    
    return {
        "name": "Jean Dupont",
        "phone": "06 12 34 56 78",
        "email": "jean.dupont@email.com",
        "general_title": "Développeur Full Stack Senior avec 5 ans d'expérience",
        "skills": "Expert en Python, JavaScript, React et Node.js. Maîtrise des architectures microservices et du DevOps.",
        "hobbies": "Passionné de photographie et de randonnée. Contributeur open source actif.",
        "langues": "Français (langue maternelle), Anglais (courant), Espagnol (intermédiaire)"
    }
