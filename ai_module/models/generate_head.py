from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import logging
from backend.config import load_config

logger = logging.getLogger(__name__)

class HeadData(BaseModel):
    name: str = Field(description="Nom complet du candidat")
    phone: str = Field(description="Numéro de téléphone du candidat")
    email: str = Field(description="Adresse email du candidat")
    general_title: str = Field(description="Titre et description générale du profil")
    skills: str = Field(description="Description détaillée des compétences techniques et professionnelles")
    langues: str = Field(description="Description détaillée des langues parlées et niveaux")
    hobbies: str = Field(description="Description détaillée des centres d'intérêt")

async def generate_structured_head(text: str) -> dict:
    """
    Génère un en-tête structuré à partir d'un texte brut en utilisant LangChain.
    
    Args:
        text (str): Le texte brut contenant les informations de l'en-tête
        
    Returns:
        dict: Dictionnaire structuré contenant les informations de l'en-tête
    """
    try:
        config = load_config()
        logger.info("Initialisation du parser et du modèle...")

        # Initialisation du modèle LLM
        llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0,
            openai_api_key=config.OPENAI_API_KEY
        )

        # Définir le parser JSON
        parser = JsonOutputParser(pydantic_object=HeadData)

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
        
        logger.info("Génération de l'en-tête structuré via LangChain...")
        head_data = json_chain.invoke({"source": text})
        
        logger.info("En-tête structuré généré avec succès")
        return head_data

    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'en-tête structuré: {str(e)}")
        raise

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
    
    # Exécution du test et affichage du résultat
    resultat = asyncio.run(generate_structured_head(texte_test))
    print("\nRésultat du test :")
    print("------------------")
    print(f"Nom: {resultat['name']}")
    print(f"Téléphone: {resultat['phone']}")
    print(f"Email: {resultat['email']}")
    print(f"Titre général: {resultat['general_title']}")
    print(f"Compétences: {resultat['skills']}")
    print(f"Langues: {resultat['langues']}")
    print(f"Centres d'intérêt: {resultat['hobbies']}")
