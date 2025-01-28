import sys
import logging
from pathlib import Path
import asyncio
import openai
from utils import get_openai_api_key, get_file, save_file, get_prompt, async_openai_call

logger = logging.getLogger(__name__)
logger.propagate = True

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent  # Chemin vers 'backend'
sys.path.append(str(ROOT_DIR))

async def get_head(profil, cv):
    """
    Génère un JSON "weights.json" en analysant une fiche de poste et les expériences professionnelles du candidat.

    :param profil: Nom du profil (sous-dossier dans `data_local`).
    :param cv: Nom du CV (sous-dossier dans `profil/cvs`).
    """
    logger.info(f"Début de la génération du fichier head.json pour le profil {profil} et le CV {cv}")

    # Configurer l'API OpenAI
    try:
        api_key = get_openai_api_key()
        client = openai.OpenAI(api_key=api_key)
        logger.debug("API OpenAI configurée avec succès")
    except Exception as e:
        logger.error("Erreur lors de la configuration de l'API OpenAI", exc_info=True)
        return

    # Configurer les chemins
    profil_source_path = f"{profil}/profil/pers.txt"
    post_source_path = f"{profil}/cvs/{cv}/source_refined.txt"
    output_path = f"{profil}/cvs/{cv}/head.json"
    prompt_name = "prompt_head.txt"
    logger.debug(f"Chemins configurés : profil_source_path={profil_source_path}, post_source_path={post_source_path}, output_path={output_path}")

    # Récupérer les fichiers nécessaires
    try:
        profil_source = get_file(profil_source_path)
        post_source = get_file(post_source_path)

        # Si une liste est retournée, prendre le premier fichier
        if isinstance(profil_source, list):
            profil_source = profil_source[0]
        if isinstance(post_source, list):
            post_source = post_source[0]

        logger.debug(f"Fichiers récupérés avec succès : {profil_source}, {post_source}")

        # Lire les contenus des fichiers sources
        with open(profil_source, "r", encoding="utf-8") as file:
            profil_content = file.read()
        with open(post_source, "r", encoding="utf-8") as file:
            job_description = file.read()

        # Récupérer le contenu du prompt
        system_prompt = get_prompt(prompt_name)
        logger.debug("Contenu des fichiers sources et du prompt chargé avec succès")
    except FileNotFoundError as e:
        logger.error(f"Erreur : Fichier non trouvé - {e}")
        return
    except Exception as e:
        logger.error("Erreur inattendue lors du chargement des fichiers", exc_info=True)
        return

    # Préparer le prompt
    user_prompt = f"""
    Voici les données nécessaires pour votre analyse :\n\n1. **Fiche de poste** :\n
    {job_description}
    \n2. **Profil du candidat** :\n
    {profil_content}
    \nGénérez le JSON final en suivant scrupuleusement les règles indiquées dans vos instructions.
    """
    logger.debug("Prompt préparé avec succès")

    try:
        # Appeler l'API de ChatGPT
        logger.info("Appel à l'API OpenAI pour générer le JSON")
        response = await async_openai_call(
            profil,
            client,
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        logger.info("JSON généré avec succès par l'API OpenAI")

        # Sauvegarder le contenu généré
        save_file(output_path, response)
        logger.info(f"Fichier head.json généré et sauvegardé dans : {output_path}")

    except openai.APIError as e:
        logger.error(f"Erreur API OpenAI : {e}", exc_info=True)
    except Exception as e:
        logger.error("Erreur inattendue lors de l'appel à l'API OpenAI", exc_info=True)


if __name__ == "__main__":
    profil = "Alexis1"
    cv = "augura"
    logger.info("Script lancé directement")
    asyncio.run(get_head(profil, cv))