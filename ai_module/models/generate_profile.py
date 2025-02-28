from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List, Dict
import logging
from backend.config import load_config

logger = logging.getLogger(__name__)

class Experience(BaseModel):
    intitule: str = Field(description="Intitulé du poste")
    dates: str = Field(description="Période d'emploi")
    etablissement: str = Field(description="Nom de l'entreprise")
    lieu: str = Field(description="Localisation")
    description: str = Field(description="Description détaillée de l'expérience")

class Education(BaseModel):
    intitule: str = Field(description="Nom du diplôme")
    dates: str = Field(description="Période de formation")
    etablissement: str = Field(description="Nom de l'institution")
    lieu: str = Field(description="Localisation")
    description: str = Field(description="Description détaillée de la formation")

class ProfileData(BaseModel):
    experiences: List[Experience] = Field(description="Liste des expériences professionnelles")
    education: List[Education] = Field(description="Liste des formations académiques")

async def generate_profile(text: str) -> Dict:
    """
    Génère un profil structuré à partir d'un texte brut.
    """
    try:
        config = load_config()
        logger.info("Initialisation du parser et du modèle...")

        llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0,
            openai_api_key=config.OPENAI_API_KEY
        )

        parser = JsonOutputParser(pydantic_object=ProfileData)

        prompt = PromptTemplate(
            template="""
            Analyse le texte suivant et extrais les expériences professionnelles et formations.
            Génère un JSON structuré avec :
            
            - Pour chaque expérience :
              - "intitule": Intitulé du poste
              - "dates": Période d'emploi
              - "etablissement": Nom de l'entreprise
              - "lieu": Localisation
              - "description": Description détaillée de l'expérience
            
            - Pour chaque formation :
              - "intitule": Nom du diplôme
              - "dates": Période de formation
              - "etablissement": Nom de l'institution
              - "lieu": Localisation
              - "description": Description détaillée de la formation
            
            {format_instructions}
            
            Texte source :
            {source}
            """,
            input_variables=["source"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        json_chain = prompt | llm | parser
        
        logger.info("Génération du profil structuré...")
        profile_data = json_chain.invoke({"source": text})
        
        logger.info("Profil structuré généré avec succès")
        return profile_data

    except Exception as e:
        logger.error(f"Erreur lors de la génération du profil: {str(e)}")
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
            profil = await generate_profile(texte_test)
            print("Profil généré avec succès:")
            print(profil)
        except Exception as e:
            print(f"Erreur lors du test: {e}")
    
    # Exécution du test
    asyncio.run(test_generation())
