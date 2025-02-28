from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Dict
import logging
from backend.config import load_config
from backend.utils.tokens import increment_token_count
import tiktoken

logger = logging.getLogger(__name__)

class HeadData(BaseModel):
    name: str = Field(description="Nom complet")
    phone: str = Field(description="Numéro de téléphone")
    email: str = Field(description="Adresse email")
    general_title: str = Field(description="Titre professionnel général")
    skills: str = Field(description="Résumé des compétences principales")
    hobbies: str = Field(description="Centres d'intérêt et loisirs")

def count_tokens(text: str) -> int:
    """Compte le nombre de tokens dans un texte"""
    encoding = tiktoken.get_encoding("cl100k_base")  # encoding pour gpt-3.5-turbo
    return len(encoding.encode(text))

async def generate_head(text: str, user_id: str) -> Dict:
    """
    Génère l'en-tête du CV à partir d'un texte brut.
    """
    try:
        config = load_config()
        logger.info("Initialisation du parser et du modèle...")

        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=config.OPENAI_API_KEY
        )

        parser = JsonOutputParser(pydantic_object=HeadData)

        prompt_template = """
        Analyse le texte suivant et extrais les informations d'en-tête du CV.
        Génère un JSON structuré avec :
        
        - "name": Nom complet de la personne
        - "phone": Numéro de téléphone
        - "email": Adresse email
        - "general_title": Titre professionnel principal
        - "skills": Résumé des compétences clés (format texte)
        - "hobbies": Centres d'intérêt et loisirs (format texte)
        
        {format_instructions}
        
        Texte source :
        {source}
        """

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["source"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # Compter les tokens d'entrée
        input_text = prompt_template.format(
            source=text,
            format_instructions=parser.get_format_instructions()
        )
        input_tokens = count_tokens(input_text)

        # Générer l'en-tête
        json_chain = prompt | llm | parser
        response = await json_chain.ainvoke({"source": text})
        
        # Compter les tokens de sortie
        output_tokens = count_tokens(str(response))
        
        # Mettre à jour les compteurs
        await increment_token_count(
            user_id=user_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        
        logger.info(f"Tokens utilisés - Entrée: {input_tokens}, Sortie: {output_tokens}")
        return response

    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'en-tête: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    
    # Exemple de texte pour tester
    texte_test = """
    Jean Dupont
    Développeur Full Stack Senior
    Email: jean.dupont@email.com
    Tél: 06 12 34 56 78
    
    Expert en Python, JavaScript et DevOps
    10 ans d'expérience en développement web
    
    Passionné de nouvelles technologies, photographie et randonnée
    """
    
    async def test_generation():
        try:
            head = await generate_head(texte_test, "test_user")
            print("En-tête généré avec succès:")
            print(head)
        except Exception as e:
            print(f"Erreur lors du test: {e}")
    
    # Exécution du test
    asyncio.run(test_generation())
