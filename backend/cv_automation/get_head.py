import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent  # Chemin vers 'backend'
sys.path.append(str(ROOT_DIR))

import openai
from config import Config
from backend.utils_old import get_openai_api_key, upload_to_bucket


def get_head(profil, cv):
    """
    Génère un JSON "weights.json" en analysant une fiche de poste et les expériences professionnelles du candidat.

    :param profil: Nom du profil (sous-dossier dans `data_local`).
    :param cv: Nom du CV (sous-dossier dans `profil/cvs`).
    """

    config = Config()
    env = config.ENV

    # Configurer l'API OpenAI
    api_key = get_openai_api_key(env, config)
    client = openai.OpenAI(api_key=api_key)

    # Configurer les chemins
    if env == "local":
        profil_path = config.LOCAL_BASE_PATH / profil / "profil"
        cv_path = config.LOCAL_BASE_PATH / profil / "cvs" / cv
        prompt_path = config.LOCAL_PROMPT_PATH / "prompt_head.txt"
    else:
        prompt_path = config.LOCAL_PROMPT_PATH / "prompt_head.txt"
        profil_path = config.TEMP_PATH / profil / "profil"
        cv_path = config.TEMP_PATH / profil / "cvs" / cv

    profil_source = profil_path / "pers.txt"
    post_source = cv_path / "source_refined.txt"

    if not profil_source.exists():
        raise FileNotFoundError(f"Le fichier des expériences n'existe pas : {profil_source}")
    if not post_source.exists():
        raise FileNotFoundError(f"Le fichier de la fiche de poste n'existe pas : {post_source}")
    

    # Lire les contenus des fichiers sources
    with open(profil_source, "r", encoding="utf-8") as file:
        profil = file.read()
    with open(post_source, "r", encoding="utf-8") as file:
        job_description = file.read()
    with open(prompt_path, "r", encoding="utf-8") as file:
        system_prompt = file.read()

    # Préparer le prompt
    user_prompt = f"""
    Voici les données nécessaires pour votre analyse :\n\n1. **Fiche de poste** :\n
    {job_description}
    \n2. **Profil du candidat** :\n
    {profil}
    \nGénérez le JSON final en suivant scrupuleusement les règles indiquées dans vos instructions.
    """

    try:
        # Appeler l'API de ChatGPT
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": system_prompt
                }
            ]
            },
                                    {
            "role": "user",
            "content": [
                {
                "text": user_prompt,
                "type": "text"
                }
            ]
            }
        ],
        response_format={
            "type": "json_object"
        },
        temperature=0.2,
        max_completion_tokens=200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )

        # Extraire le contenu généré
        condensed_description = response.choices[0].message.content.strip()
        
        exp_output = cv_path / "head.json"
        if env == "local":
            # Sauvegarder localement
            Path(exp_output).parent.mkdir(parents=True, exist_ok=True)
            Path(exp_output).write_text(condensed_description, encoding="utf-8")
        else:
            upload_to_bucket(config.BUCKET_NAME, exp_output, condensed_description)

        print(f"head du cv généré à : {exp_output}")

    except openai.APIError as e:
        print(f"Erreur API : {e}")
    except openai.BadRequestError as e:
        print(f"Requête invalide : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")



if __name__ == "__main__":
    profil = "j4WSNb5TuQVwVwSpq65N7o06GC52"
    cv = "cv1"

    get_head(profil, cv)