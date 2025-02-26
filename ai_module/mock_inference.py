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
        "informations_personnelles": {
            "nom": "Dupont",
            "prenom": "Jean",
            "email": "jean.dupont@email.com",
            "telephone": "0612345678",
            "localisation": "Paris, France"
        },
        "resume_professionnel": "Développeur fullstack avec 5 ans d'expérience",
        "experiences_professionnelles": [
            {
                "titre": "Développeur Senior",
                "entreprise": "Tech Company",
                "dates": "2020-2023",
                "description": "Développement d'applications web"
            }
        ],
        "formation": [
            {
                "titre": "Master Informatique",
                "etablissement": "Université de Paris",
                "dates": "2015-2020"
            }
        ],
        "competences_techniques": [
            "Python",
            "JavaScript",
            "React",
            "Docker"
        ],
        "langues": {
            "Français": "Natif",
            "Anglais": "Courant"
        }
    }
