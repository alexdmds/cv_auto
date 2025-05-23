import logging
from typing import Dict, Any
from ai_module.lg_models import ProfileState, CVGenState, GeneralInfo, GlobalExperience, GlobalEducation, CVExperience, CVEducation, CVLanguage

logger = logging.getLogger(__name__)


def generate_profile(profile_state: ProfileState) -> ProfileState:
    """
    Mock de la fonction generate_profile qui extrait des informations structurées à partir d'un texte brut.
    
    Args:
        profile_state (ProfileState): L'état contenant le texte brut à analyser
        
    Returns:
        ProfileState: L'état mis à jour avec des informations extraites fictives
    """
    logger.info("Utilisation du mock generate_profile")
    
    # Vérifier que l'entrée est du bon type
    if isinstance(profile_state, str):
        logger.info("Conversion du texte en ProfileState")
        text_content = profile_state
        profile_state = ProfileState()
        profile_state.input_text = text_content

    # Création des informations d'en-tête fictives
    head = GeneralInfo(
        name="Jean Dupont",
        phone="06 12 34 56 78",
        email="jean.dupont@email.com",
        general_title="Développeur Full Stack Senior avec 8 ans d'expérience",
        skills="Python, JavaScript, React, Node.js, Docker, AWS, Git, SQL, MongoDB, REST API, Django, FastAPI",
        langues="Français (natif), Anglais (courant), Espagnol (intermédiaire)",
        hobbies="Randonnée, photographie, contribution open source, échecs"
    )
    
    # Création d'expériences professionnelles fictives
    experiences = [
        GlobalExperience(
            intitule="Développeur Full Stack Senior",
            dates="2020 - Présent",
            etablissement="TechSolutions SA",
            lieu="Paris",
            description="Développement d'applications web en utilisant React, Node.js et Python. "
                        "Mise en place d'une architecture microservices avec Docker et Kubernetes. "
                        "Optimisation des performances et de la scalabilité des applications existantes."
        ),
        GlobalExperience(
            intitule="Développeur Backend",
            dates="2017 - 2020",
            etablissement="DataCorp",
            lieu="Lyon",
            description="Conception et développement d'API RESTful avec Django et FastAPI. "
                        "Gestion de bases de données SQL et NoSQL. "
                        "Intégration continue et déploiement automatisé (CI/CD)."
        )
    ]
    
    # Création de formations académiques fictives
    education = [
        GlobalEducation(
            intitule="Master en Informatique",
            dates="2015 - 2017",
            etablissement="Université de Paris",
            lieu="Paris",
            description="Spécialisation en développement web et systèmes distribués. "
                        "Projet de fin d'études : Développement d'une plateforme de gestion de données. "
                        "Mention Très Bien."
        ),
        GlobalEducation(
            intitule="Licence en Informatique",
            dates="2012 - 2015",
            etablissement="Université de Lyon",
            lieu="Lyon",
            description="Formation générale en informatique avec spécialisation en programmation. "
                        "Projets en Java, Python et bases de données."
        )
    ]
    
    # Mise à jour de l'état
    profile_state.head = head
    profile_state.experiences = experiences
    profile_state.education = education
    
    # On conserve le texte d'entrée s'il existe
    if profile_state.input_text:
        logger.info(f"Texte d'entrée conservé (longueur: {len(profile_state.input_text)} caractères)")
    
    logger.info(f"Mock profile généré avec {len(experiences)} expériences et {len(education)} formations")
    
    return profile_state


def generate_cv(state: CVGenState) -> CVGenState:
    """
    Mock de la fonction generate_cv qui retourne un CVGenState modifié avec des valeurs statiques.
    
    Args:
        state (CVGenState): L'état global initial
        
    Returns:
        CVGenState: L'état global modifié avec des valeurs mock
    """
    logger.info("Utilisation du mock generate_cv")
    
    # Vérifier que state.head existe
    if not hasattr(state, 'head'):
        logger.warning("L'état n'a pas d'attribut 'head'")
        return state
    
    # Modification des informations d'en-tête
    state.head.title_refined = "Développeur Full Stack Senior | Expert Python & JavaScript"
    state.head.mail = "jean.dupont@email.com"
    state.head.tel_refined = "+33 6 12 34 56 78"

    state.job_refined = "Résumé de la fiche de poste : Développeur Full Stack Senior | Expert Python & JavaScript"
    state.language_cv = "fr"
    
    # Modification des compétences - champ connu pour exister
    if hasattr(state, 'competences'):
        state.competences = {
            "Développement Web": ["React", "JavaScript", "HTML/CSS", "Node.js"],
            "Backend": ["Python", "Django", "FastAPI", "SQL"],
            "DevOps": ["Docker", "CI/CD", "AWS", "Git"]
        }
    
    # Ajout des langues
    if hasattr(state, 'langues'):
        state.langues = [
            CVLanguage(language="Français", level="Natif"),
            CVLanguage(language="Anglais", level="Courant"),
            CVLanguage(language="Espagnol", level="Intermédiaire")
        ]
    
    # Création des expériences
    if hasattr(state, 'experiences'):
        state.experiences = [
            CVExperience(
                title_raw="Développeur Full Stack Senior",
                title_refined="Développeur Full Stack Senior",
                company_raw="TechSolutions SA",
                company_refined="TechSolutions SA",
                dates_raw="2020 - Présent",
                dates_refined="2020 - Présent",
                location_raw="Paris",
                location_refined="Paris",
                description_raw="Développement d'applications web en utilisant React, Node.js et Python.",
                description_refined="Développement d'applications web en utilisant React, Node.js et Python.",
                bullets=[
                    "Développement d'applications web modernes avec React et Node.js",
                    "Mise en place d'une architecture microservices avec Docker",
                    "Optimisation des performances et de la scalabilité"
                ],
                weight=2.0,
                summary="Développement d'applications Web avec technologies modernes",
                order=1,
                nb_bullets=3
            ),
            CVExperience(
                title_raw="Développeur Backend",
                title_refined="Développeur Backend",
                company_raw="DataCorp",
                company_refined="DataCorp",
                dates_raw="2017 - 2020",
                dates_refined="2017 - 2020",
                location_raw="Lyon",
                location_refined="Lyon",
                description_raw="Conception et développement d'API RESTful avec Django et FastAPI.",
                description_refined="Conception et développement d'API RESTful avec Django et FastAPI.",
                bullets=[
                    "Conception et développement d'API RESTful",
                    "Gestion de bases de données SQL et NoSQL",
                    "Intégration continue et déploiement automatisé"
                ],
                weight=2.0,
                summary="Développement backend avec Django et FastAPI",
                order=2,
                nb_bullets=3
            )
        ]
    
    # Création des formations
    if hasattr(state, 'education'):
        state.education = [
            CVEducation(
                degree_raw="Master en Informatique",
                degree_refined="Master en Informatique",
                institution_raw="Université de Paris",
                institution_refined="Université de Paris",
                dates_raw="2015 - 2017",
                dates_refined="2015 - 2017",
                location_raw="Paris",
                location_refined="Paris",
                description_raw="Spécialisation en développement web et systèmes distribués.",
                description_generated="Spécialisation en développement web et systèmes distribués.",
                description_refined="Spécialisation en développement web et systèmes distribués.",
                weight=2.0,
                summary="Formation en informatique avec spécialisation développement",
                order=1,
                nb_mots=12
            ),
            CVEducation(
                degree_raw="Licence en Informatique",
                degree_refined="Licence en Informatique",
                institution_raw="Université de Lyon",
                institution_refined="Université de Lyon",
                dates_raw="2012 - 2015",
                dates_refined="2012 - 2015",
                location_raw="Lyon",
                location_refined="Lyon",
                description_raw="Formation générale en informatique avec spécialisation en programmation.",
                description_generated="Formation générale en informatique avec spécialisation en programmation.",
                description_refined="Formation générale en informatique avec spécialisation en programmation.",
                weight=2.0,
                summary="Formation en informatique générale",
                order=2,
                nb_mots=10
            )
        ]
    
    return state