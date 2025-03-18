from langgraph.graph import StateGraph, START, END
from ai_module.lg_models import ProfileState, GeneralInfo, GlobalExperience, GlobalEducation, GlobalExperienceList, GlobalEducationList
from ai_module.llm_config import get_llm
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
import logging
from typing import List

logger = logging.getLogger(__name__)

def generate_structured_head_node(state: ProfileState) -> dict:
    """
    Nœud LangGraph pour générer un en-tête structuré à partir d'un texte brut.
    
    Args:
        state (ProfileState): État contenant le texte brut sous la clé 'input_text'
        
    Returns:
        dict: État mis à jour avec les informations d'en-tête
    """
    try:
        logger.info("Initialisation du parser et du modèle...")

        # Utilisation de get_llm() comme dans parallel_tasks.py
        llm = get_llm()

        # Définir le parser JSON
        parser = JsonOutputParser(pydantic_object=GeneralInfo)

        # Création du prompt
        prompt = PromptTemplate(
            template=(
                """
                Analyse le texte suivant décrivant un profil candidat et génère un JSON structuré.
                Pour chaque champ, fournis une description concise mais exhaustive, sans phrases complètes.
                
                Le JSON doit contenir les champs suivants :
                - "name": Nom complet uniquement
                - "phone": Numéro de téléphone uniquement
                - "email": Adresse email uniquement
                - "general_title": Titre professionnel et profil général en quelques mots clés
                - "skills": Liste exhaustive des compétences techniques et professionnelles, séparées par des virgules
                - "langues": Liste des langues avec niveau et détails pertinents (certifications, séjours, etc.)
                - "hobbies": Liste des centres d'intérêt avec détails pertinents, séparés par des virgules"
                
                {format_instructions}
                
                Texte source :
                {source}
                """
            ),
            input_variables=["source"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        # Création et exécution de la chaîne
        json_chain = prompt | llm | parser
        
        logger.info("Génération de l'en-tête structuré...")
        result = json_chain.invoke({"source": state.input_text})
        
        # Vérifier le type du résultat
        logger.info(f"Type du résultat: {type(result)}")
        
        # S'assurer que nous retournons un objet HeadData
        if isinstance(result, GeneralInfo):
            # Si c'est déjà un HeadData, on l'utilise directement
            head_data = result
        else:
            # Si c'est un dictionnaire, on crée une nouvelle instance HeadData
            try:
                # Créer un nouvel objet
                head_data = GeneralInfo(**result)
                logger.info("Création de GeneralInfo à partir du dictionnaire réussie")
            except Exception as e:
                logger.error(f"Erreur lors de la création de GeneralInfo: {str(e)}")
                # Fallback: créer un HeadData manuellement
                head_data = GeneralInfo()
                # Remplir les champs manuellement si le dictionnaire contient ces clés
                if isinstance(result, dict):
                    if "name" in result:
                        head_data.name = result["name"]
                    if "phone" in result:
                        head_data.phone = result["phone"]
                    if "email" in result:
                        head_data.email = result["email"]
                    if "general_title" in result:
                        head_data.general_title = result["general_title"]
                    if "skills" in result:
                        head_data.skills = result["skills"]
                    if "langues" in result:
                        head_data.langues = result["langues"]
                    if "hobbies" in result:
                        head_data.hobbies = result["hobbies"]
        
        logger.info("En-tête structuré généré avec succès")
        
        # Format de retour similaire à parallel_tasks.py, mise à jour de l'état
        return {"head": head_data}

    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'en-tête structuré: {str(e)}")
        raise

def generate_exp_node(state: ProfileState) -> dict:
    """
    Nœud LangGraph pour générer les expériences professionnelles structurées à partir d'un texte brut.
    
    Args:
        state (ProfileState): État contenant le texte brut sous la clé 'input_text'
        
    Returns:
        dict: État mis à jour avec les informations d'expérience
    """
    try:
        logger.info("Initialisation du parser et du modèle pour les expériences...")

        # Utilisation de get_llm()
        llm = get_llm()

        # Définir le parser JSON
        parser = JsonOutputParser(pydantic_object=GlobalExperienceList)

        # Création du prompt
        prompt = PromptTemplate(
            template="""
            Analyse méticuleusement le texte suivant et extrais toutes les informations concernant les expériences professionnelles.
            Génère un JSON structuré en incluant absolument tous les détails présents dans le texte source, sans omettre aucune information :
            
            Pour chaque expérience :
            - "intitule": Intitulé exact et complet du poste
            - "dates": Période d'emploi précise
            - "etablissement": Nom complet de l'entreprise
            - "lieu": Localisation détaillée
            - "description": Description EXHAUSTIVE de l'expérience, incluant :
              * Toutes les responsabilités mentionnées
              * Tous les projets cités
              * Toutes les technologies utilisées
              * Tous les accomplissements
              * Tout autre détail présent dans le texte source
            
            IMPORTANT : Ne fais aucune synthèse ou résumé. Inclus absolument tous les détails mentionnés dans le texte source.
            
            {format_instructions}
            
            Texte source :
            {source}
            """,
            input_variables=["source"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # Création et exécution de la chaîne
        json_chain = prompt | llm | parser
        
        logger.info("Génération des expériences structurées...")
        result = json_chain.invoke({"source": state.input_text})
        
        # Vérifier le type du résultat
        logger.info(f"Type du résultat des expériences: {type(result)}")
        
        # Traitement du résultat
        experiences_list = []
        
        if isinstance(result, GlobalExperienceList):
            # Si le résultat est une instance de GlobalExperienceList
            experiences_list = result.experiences
        elif isinstance(result, dict) and 'experiences' in result:
            # Si c'est un dictionnaire avec une clé 'experiences'
            for exp_dict in result['experiences']:
                try:
                    exp = GlobalExperience(**exp_dict)
                    experiences_list.append(exp)
                except Exception as e:
                    logger.error(f"Erreur lors de la création d'une expérience: {str(e)}")
        
        logger.info(f"Nombre d'expériences extraites: {len(experiences_list)}")
        
        # Format de retour, mise à jour de l'état
        return {"experiences": experiences_list}

    except Exception as e:
        logger.error(f"Erreur lors de la génération des expériences: {str(e)}")
        raise

def generate_edu_node(state: ProfileState) -> dict:
    """
    Nœud LangGraph pour générer les formations éducatives structurées à partir d'un texte brut.
    
    Args:
        state (ProfileState): État contenant le texte brut sous la clé 'input_text'
        
    Returns:
        dict: État mis à jour avec les informations d'éducation
    """
    try:
        logger.info("Initialisation du parser et du modèle pour les formations...")

        # Utilisation de get_llm()
        llm = get_llm()

        # Définir le parser JSON
        parser = JsonOutputParser(pydantic_object=GlobalEducationList)

        # Création du prompt
        prompt = PromptTemplate(
            template="""
            Analyse méticuleusement le texte suivant et extrais toutes les informations concernant les formations académiques.
            Génère un JSON structuré en incluant absolument tous les détails présents dans le texte source, sans omettre aucune information :
            
            Pour chaque formation :
            - "intitule": Nom complet et exact du diplôme
            - "dates": Période précise de formation
            - "etablissement": Nom complet de l'institution
            - "lieu": Localisation détaillée
            - "description": Description EXHAUSTIVE de la formation, incluant :
              * Toutes les spécialisations
              * Tous les résultats académiques
              * Tous les projets réalisés
              * Toutes les compétences acquises
              * Tout autre détail présent dans le texte source
            
            IMPORTANT : Ne fais aucune synthèse ou résumé. Inclus absolument tous les détails mentionnés dans le texte source.
            
            {format_instructions}
            
            Texte source :
            {source}
            """,
            input_variables=["source"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # Création et exécution de la chaîne
        json_chain = prompt | llm | parser
        
        logger.info("Génération des formations structurées...")
        result = json_chain.invoke({"source": state.input_text})
        
        # Vérifier le type du résultat
        logger.info(f"Type du résultat des formations: {type(result)}")
        
        # Traitement du résultat
        education_list = []
        
        if isinstance(result, GlobalEducationList):
            # Si le résultat est une instance de GlobalEducationList
            education_list = result.education
        elif isinstance(result, dict) and 'education' in result:
            # Si c'est un dictionnaire avec une clé 'education'
            for edu_dict in result['education']:
                try:
                    edu = GlobalEducation(**edu_dict)
                    education_list.append(edu)
                except Exception as e:
                    logger.error(f"Erreur lors de la création d'une formation: {str(e)}")
        
        logger.info(f"Nombre de formations extraites: {len(education_list)}")
        
        # Format de retour, mise à jour de l'état
        return {"education": education_list}

    except Exception as e:
        logger.error(f"Erreur lors de la génération des formations: {str(e)}")
        raise

def create_profile_graph() -> StateGraph:
    """
    Crée et configure le graphe d'états pour la génération de profil complet.
    
    Returns:
        StateGraph: Le graphe prêt à être compilé et exécuté
    """
    # Construction du graphe
    graph = StateGraph(ProfileState)
    
    # Ajout des nœuds
    graph.add_node("extract_head", generate_structured_head_node)
    graph.add_node("extract_experiences", generate_exp_node)
    graph.add_node("extract_education", generate_edu_node)
    
    # Configuration des transitions parallèles
    graph.add_edge(START, "extract_head")
    graph.add_edge(START, "extract_experiences")
    graph.add_edge(START, "extract_education")
    
    # Tous les nœuds mènent à la fin
    graph.add_edge("extract_head", END)
    graph.add_edge("extract_experiences", END)
    graph.add_edge("extract_education", END)
    
    # Compilation
    return graph

if __name__ == "__main__":
    # Exemple d'utilisation
    import asyncio
    
    async def test_profile_chain():
        # Texte de test
        texte_test = """
        Jean-Michel Dupont
        Architecte Solutions & Lead Developer
        Email: jm.dupont@email.com | Tel: 06 12 34 56 78
        LinkedIn: linkedin.com/in/jmdupont

        Expert en architecture logicielle et développement full-stack avec 12 ans d'expérience 
        dans la conception et le déploiement de solutions cloud à grande échelle. 
        Passionné par l'innovation technologique et le leadership technique.

        EXPÉRIENCE PROFESSIONNELLE
        
        Lead Developer & Architecte Solutions | TechSolutions SA | Paris | 2018-Présent
        - Direction technique d'une équipe de 8 développeurs sur des projets cloud à haute disponibilité
        - Conception et implémentation d'architectures microservices avec Kubernetes et Docker
        - Migration de systèmes monolithiques vers des solutions cloud natives (AWS, GCP)
        - Développement d'APIs RESTful et GraphQL pour services critiques
        - Mise en place de pipelines CI/CD avec GitLab et Jenkins
        
        Senior Backend Developer | DataCorp | Lyon | 2015-2018
        - Développement de services backend en Python et Node.js
        - Optimisation de requêtes SQL complexes sur bases de données à fort volume
        - Implémentation de systèmes de traitement de données en temps réel avec Apache Kafka
        - Participation à la migration vers une architecture orientée services
        
        FORMATION
        
        Master en Ingénierie Informatique | École Polytechnique | Paris | 2013-2015
        - Spécialisation en architecture des systèmes distribués
        - Projet de fin d'études: Implémentation d'un système de réplication de données tolérant aux pannes
        - Mention Très Bien, Major de promotion
        
        Licence en Informatique | Université Claude Bernard | Lyon | 2010-2013
        - Option développement logiciel et bases de données
        - Projets pratiques en Java, C++ et SQL
        - Stage de fin d'études chez StartupTech: Développement d'une application web en Django

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
        
        # Création et compilation du graphe
        graph = create_profile_graph().compile()
        
        # Initialiser l'état
        initial_state = ProfileState(input_text=texte_test)
        
        # Exécuter le graphe
        result = await graph.ainvoke(initial_state)
        
        # Debug: afficher le type et le contenu du résultat
        print(f"\nType du résultat: {type(result)}")
        print(f"Clés disponibles: {result.keys() if hasattr(result, 'keys') else 'Pas de méthode keys()'}")
        
        # Afficher les résultats en tenant compte de la structure réelle
        print("\nPROFIL EXTRAIT :")
        print("================")
        
        # Pour les graphes parallèles, les résultats sont dans un dictionnaire spécial
        # avec les clés correspondant aux mises à jour effectuées par chaque nœud
        
        print("\nEN-TÊTE :")
        if 'head' in result:
            head = result['head']
            print(f"Nom: {head.name}")
            print(f"Email: {head.email}")
            print(f"Téléphone: {head.phone}")
            print(f"Titre: {head.general_title}")
            print(f"Compétences: {head.skills}")
            print(f"Langues: {head.langues}")
            print(f"Centres d'intérêt: {head.hobbies}")
        else:
            print("Aucune donnée d'en-tête trouvée")
        
        print("\nEXPÉRIENCES :")
        if 'experiences' in result and result['experiences']:
            for i, exp in enumerate(result['experiences'], 1):
                print(f"\n{i}. {exp.intitule} | {exp.etablissement} | {exp.lieu} | {exp.dates}")
                print(f"   {exp.description}")
        else:
            print("Aucune expérience trouvée")
        
        print("\nFORMATION :")
        if 'education' in result and result['education']:
            for i, edu in enumerate(result['education'], 1):
                print(f"\n{i}. {edu.intitule} | {edu.etablissement} | {edu.lieu} | {edu.dates}")
                print(f"   {edu.description}")
        else:
            print("Aucune formation trouvée")
    
    # Exécution du test
    asyncio.run(test_profile_chain())
