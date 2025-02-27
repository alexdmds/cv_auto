from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List, Dict
import logging
from backend.config import load_config

logger = logging.getLogger(__name__)

# Définir les types pour la clarté
Experiences = List[Dict[str, str]]
Education = List[Dict[str, str]]

class ProfileData(BaseModel):
    experiences: Experiences = Field(description="Liste des expériences professionnelles du candidat")
    education: Education = Field(description="Liste des formations académiques du candidat")

async def generate_structured_profile(text: str) -> Dict:
    """
    Génère un profil structuré à partir d'un texte brut en utilisant LangChain.
    
    Args:
        text (str): Le texte brut contenant les informations du profil
        
    Returns:
        Dict: Dictionnaire structuré contenant les expériences et formations
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
        parser = JsonOutputParser(pydantic_object=ProfileData)

        # Création du prompt
        prompt = PromptTemplate(
            template=(
                """
                Analyse le texte suivant décrivant un profil candidat et génère un JSON structuré.
                Le JSON doit contenir deux clés : "experiences" et "education", avec les champs suivants :
                
                - Pour chaque expérience :
                  - "intitule": Intitulé du poste
                  - "dates": Période d'emploi
                  - "etablissement": Nom de l'entreprise
                  - "lieu": Localisation
                  - "description": L'intégralité des informations disponibles concernant cette expérience, sans résumé ni reformulation.
                
                - Pour chaque formation :
                  - "intitule": Nom du diplôme
                  - "dates": Période de formation
                  - "etablissement": Nom de l'institution
                  - "lieu": Localisation
                  - "description": L'intégralité des informations disponibles sur cette formation, sans résumé ni reformulation.
                
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
        
        logger.info("Génération du profil structuré via LangChain...")
        profile_data = json_chain.invoke({"source": text})
        
        logger.info("Profil structuré généré avec succès")
        return profile_data

    except Exception as e:
        logger.error(f"Erreur lors de la génération du profil structuré: {str(e)}")
        raise


if __name__ == "__main__":
    import asyncio
    
    # Exemple de texte pour tester
    texte_test = """
    Jean Dupont
    Développeur Full Stack avec 5 ans d'expérience
    
    EXPÉRIENCE
    Senior Developer chez TechCorp (2020-2023) - Paris
    - Développement d'applications web avec React et Node.js
    - Lead technique sur 3 projets majeurs
    
    FORMATION
    Master en Informatique - Université de Paris (2018) - Paris
    - Spécialisation en développement web
    - Major de promotion
    """
    
    async def test_generation():
        try:
            profil = await generate_structured_profile(texte_test)
            print("Profil généré avec succès:")
            print(profil)
        except Exception as e:
            print(f"Erreur lors du test: {e}")
    
    # Exécution du test
    asyncio.run(test_generation())
