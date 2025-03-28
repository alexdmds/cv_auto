import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent  # Chemin vers 'backend'
sys.path.append(str(ROOT_DIR))

import asyncio
import openai
from backend.utils_old import get_openai_api_key, get_file, save_file, async_openai_call

import logging

logger = logging.getLogger(__name__)
logger.propagate = True

async def refine_job_description(profil, cv):
    """
    Condense une fiche de poste en 500 mots maximum en utilisant l'API de ChatGPT.

    :param profil: Nom du profil (sous-dossier dans `data_local`).
    :param cv: Nom du CV (sous-dossier dans `profil/cvs`).
    """
    logger.info("Lancement de refine_job_description")
    # Configurer l'API OpenAI
    api_key = get_openai_api_key()
    client = openai.OpenAI(api_key=api_key)

    # Configurer les chemins
    source_path = f"{profil}/cvs/{cv}/source_raw.txt"
    output_path = f"{profil}/cvs/{cv}/source_refined.txt"

    # Récupérer le contenu du fichier source
    try:
        source_file = get_file(source_path)
        if isinstance(source_file, list):  # Si une liste est retournée
            source_file = source_file[0]  # Prenez le premier élément

        with open(source_file, "r", encoding="utf-8") as file:
            job_description = file.read()
    except FileNotFoundError as e:
        logger.error(f"Erreur : {e}")
        return

    # Préparer le message pour l'API
    prompt = (
        "Condensez la fiche de poste suivante, dans la même langue, en gardant tous les éléments importants, "
        "dans une limite de 500 mots. Conservez le ton professionnel et les détails essentiels.\n\n"
        f"Fiche de poste :\n{job_description}\n\nCondensé :"
    )

    try:
        # Appeler l'API de ChatGPT
        response = await async_openai_call(
            profil,
            client,
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant expert en rédaction professionnelle."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,  # Limite de tokens pour le condensé
            temperature=0.7,
        )

        # Extraire le contenu généré
        logger.debug(f"response : {response}")
  
        # Sauvegarder le contenu généré
        save_file(output_path, response)
        logger.info(f"Fiche de poste condensée enregistrée dans : {output_path}")

    except openai.APIError as e:
        logger.error(f"Erreur API : {e}")
    except Exception as e:
        logger.error(f"Erreur inattendue : {e}")


if __name__ == "__main__":
    profil = "Alexis1"
    cv = "augura"
    asyncio.run(refine_job_description(profil, cv))