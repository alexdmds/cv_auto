import logging
from typing import Dict, Any
from ai_module.new_models.lg_models import GlobalState

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
        "head": {
            "name": "Jean Dupont",
            "title": "Développeur Full Stack Senior",
            "mail": "jean.dupont@email.com",
            "phone": "06 12 34 56 78",
            "linkedin_url": "https://linkedin.com/in/jeandupont"
        },
        "experiences": [
            {
                "title": "Développeur Senior",
                "company": "Tech Company",
                "dates": "2020-2023",
                "location": "Paris",
                "full_descriptions": "Développement d'applications web avec React et Node.js. Lead technique sur 3 projets majeurs."
            },
            {
                "title": "Développeur Full Stack",
                "company": "StartupCo",
                "dates": "2018-2020",
                "location": "Lyon",
                "full_descriptions": "Développement full stack avec Python et Vue.js. Mise en place de l'architecture microservices."
            }
        ],
        "educations": [
            {
                "title": "Master Informatique",
                "university": "Université de Paris",
                "dates": "2016-2018",
                "full_description": "Spécialisation en développement web. Major de promotion."
            },
            {
                "title": "Licence Informatique",
                "university": "Université de Lyon",
                "dates": "2013-2016",
                "full_description": "Formation généraliste en informatique. Projet de fin d'études sur le machine learning."
            }
        ],
        "skills": "Python, JavaScript, React, Node.js, Vue.js, Docker, AWS",
        "languages": "Français (natif), Anglais (courant), Espagnol (intermédiaire)",
        "hobbies": "Photographie, randonnée, programmation open source"
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
        "title_raw": "Développeur",
        "title_generated": "Développeur Full Stack Expérimenté",
        "title_refined": "Développeur Full Stack Senior",
        "mail": "jean.dupont@email.com",
        "tel_raw": "0612345678",
        "tel_refined": "06 12 34 56 78"
    }

def generate_cv(state: GlobalState) -> GlobalState:
    """
    Mock de la fonction generate_cv qui retourne un GlobalState modifié avec des valeurs statiques.
    
    Args:
        state (GlobalState): L'état global initial
        
    Returns:
        GlobalState: L'état global modifié avec des valeurs mock
    """
    logger.info("Utilisation du mock generate_cv")
    
    # Vérifier que state.head existe
    if not hasattr(state, 'head'):
        logger.warning("L'état n'a pas d'attribut 'head'")
        return state
    
    # Modification du titre - champ connu pour exister
    state.head.title_refined = "Développeur Full Stack Senior | Expert Python & JavaScript"
    
    # Modification des compétences - champ connu pour exister
    if hasattr(state, 'competences'):
        state.competences = {
            "Développement Web": ["React", "JavaScript", "HTML/CSS", "Node.js"],
            "Backend": ["Python", "Django", "FastAPI", "SQL"],
            "DevOps": ["Docker", "CI/CD", "AWS", "Git"]
        }
    
    # Modification des expériences - utiliser uniquement les champs qui existent déjà
    if hasattr(state, 'experiences'):
        for exp in state.experiences:
            # Modifier uniquement les champs existants
            if hasattr(exp, 'weight'):
                exp.weight = 2.0
            if hasattr(exp, 'summary'):
                exp.summary = "Développement d'applications Web avec technologies modernes"
    
    # Modification des formations - utiliser uniquement les champs qui existent déjà
    if hasattr(state, 'education'):
        for edu in state.education:
            if hasattr(edu, 'weight'):
                edu.weight = 2.0
            if hasattr(edu, 'summary'):
                edu.summary = "Formation en informatique avec spécialisation développement"
    
    # Ne pas essayer d'ajouter de nouveaux attributs comme status ou final_output
    # Ces attributs ne font pas partie du modèle GlobalState
    
    return state

# Fonction mock supplémentaire pour la création d'un CV complet
def create_mock_cv_data() -> Dict[str, Any]:
    """
    Crée des données mock pour un CV au format attendu par Firestore.
    
    Returns:
        Dict[str, Any]: Données CV au format Firestore
    """
    return {
        "cv_name": "CV de test",
        "job_raw": "Développeur Full Stack Senior",
        "cv_data": {
            "name": "Jean Dupont",
            "title": "Développeur Full Stack Senior",
            "mail": "jean.dupont@email.com",
            "phone": "06 12 34 56 78",
            "lang_of_cv": "fr",
            "sections_name": {
                "experience_section_name": "Expérience Professionnelle",
                "education_section_name": "Formation",
                "skills_section_name": "Compétences",
                "languages_section_name": "Langues",
                "Hobbies_section": "Centres d'intérêt"
            },
            "experiences": [
                {
                    "title": "Développeur Senior",
                    "company": "Tech Company",
                    "dates": "2020-2023",
                    "location": "Paris",
                    "bullets": [
                        "Développement d'applications web avec React et Node.js",
                        "Lead technique sur 3 projets majeurs",
                        "Mise en place d'une architecture microservices"
                    ]
                },
                {
                    "title": "Développeur Full Stack",
                    "company": "StartupCo",
                    "dates": "2018-2020",
                    "location": "Lyon",
                    "bullets": [
                        "Développement full stack avec Python et Vue.js",
                        "Mise en place de l'architecture microservices",
                        "Optimisation des performances de l'application principale"
                    ]
                }
            ],
            "educations": [
                {
                    "title": "Master Informatique",
                    "university": "Université de Paris",
                    "dates": "2016-2018",
                    "location": "Paris",
                    "description": "Spécialisation en développement web. Major de promotion."
                },
                {
                    "title": "Licence Informatique",
                    "university": "Université de Lyon",
                    "dates": "2013-2016",
                    "location": "Lyon",
                    "description": "Formation généraliste en informatique. Projet de fin d'études sur le machine learning."
                }
            ],
            "skills": [
                {
                    "category_name": "Développement Web",
                    "skills": "React, JavaScript, HTML/CSS, Node.js"
                },
                {
                    "category_name": "Backend",
                    "skills": "Python, Django, FastAPI, SQL"
                },
                {
                    "category_name": "DevOps",
                    "skills": "Docker, CI/CD, AWS, Git"
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
                },
                {
                    "language": "Espagnol",
                    "level": "Intermédiaire (B1)"
                }
            ],
            "hobbies": "Photographie, randonnée, programmation open source"
        }
    }
