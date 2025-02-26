from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class Experience(BaseModel):
    titre: str = Field(description="Titre du poste")
    entreprise: str = Field(description="Nom de l'entreprise")
    dates: str = Field(description="Période d'emploi")
    description: str = Field(description="Description des responsabilités")

class Formation(BaseModel):
    titre: str = Field(description="Intitulé du diplôme/certification") 
    etablissement: str = Field(description="Nom de l'établissement")
    dates: str = Field(description="Période de formation")

class ProfileStructure(BaseModel):
    informations_personnelles: Dict[str, str] = Field(
        description="Informations personnelles (nom, prénom, email, téléphone, localisation)"
    )
    resume_professionnel: str = Field(description="Résumé du profil professionnel")
    experiences_professionnelles: List[Experience] = Field(description="Liste des expériences professionnelles")
    formation: List[Formation] = Field(description="Liste des formations")
    competences_techniques: List[str] = Field(description="Liste des compétences techniques")
    langues: Dict[str, str] = Field(description="Langues maîtrisées avec niveau")

async def generate_structured_profile(text: str) -> Dict[str, Any]:
    """
    Génère un profil structuré à partir d'un texte brut en utilisant LangChain et GPT-4.
    
    Args:
        text (str): Le texte brut contenant les informations du profil
        
    Returns:
        Dict[str, Any]: Dictionnaire structuré contenant les informations du profil
    """
    try:
        logger.info("Initialisation du parser et du modèle...")
        
        # Configuration du parser de sortie
        parser = PydanticOutputParser(pydantic_object=ProfileStructure)
        
        # Configuration du modèle de chat
        chat = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.2
        )

        # Création du template de prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            Tu es un expert en analyse de CV et profils professionnels.
            Extrais les informations clés du texte fourni et structure-les selon le format demandé.
            Sois précis et exhaustif dans l'extraction des informations.
            
            {format_instructions}
            """),
            ("human", "{text}")
        ])

        # Création du prompt final avec les instructions de format
        formatted_prompt = prompt.format_messages(
            format_instructions=parser.get_format_instructions(),
            text=text
        )

        logger.info("Génération du profil structuré via LangChain...")
        # Obtention et parsing de la réponse
        response = chat.invoke(formatted_prompt)
        profile_dict = parser.parse(response.content)
        
        logger.info("Profil structuré généré avec succès")
        return profile_dict.model_dump()

    except Exception as e:
        logger.error(f"Erreur lors de la génération du profil structuré: {str(e)}")
        raise

