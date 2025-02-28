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
    skills: str = Field(description="Description détaillée des compétences")
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
                Pour chaque champ, fournis une description détaillée et exhaustive au format texte.
                
                Le JSON doit contenir les champs suivants :
                - "name": Le nom complet du candidat
                - "phone": Le numéro de téléphone complet
                - "email": L'adresse email complète
                - "general_title": Une description détaillée du titre professionnel et du profil général
                - "skills": Une description narrative et détaillée de toutes les compétences
                - "hobbies": Une description narrative et détaillée de tous les centres d'intérêt
                
                Assure-toi que chaque champ contient une description exhaustive en texte libre,
                pas seulement des listes ou des valeurs courtes.
                
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
    Jean Dupont
    Développeur Full Stack Senior
    Email: jean.dupont@email.com | Tel: 06 12 34 56 78
    
    Expert en développement web avec 10 ans d'expérience dans la création 
    d'applications complexes et innovantes.
    
    Compétences: Python, JavaScript, React, DevOps, Gestion d'équipe
    
    Centres d'intérêt: Photographie, Randonnée, Musique
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
    print(f"Centres d'intérêt: {resultat['hobbies']}")
