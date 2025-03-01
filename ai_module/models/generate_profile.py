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
            Analyse méticuleusement le texte suivant et extrais toutes les informations concernant les expériences professionnelles et formations.
            Génère un JSON structuré en incluant absolument tous les détails présents dans le texte source, sans omettre aucune information :
            
            - Pour chaque expérience :
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
            
            - Pour chaque formation :
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
