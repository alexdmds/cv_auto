import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent  # Chemin vers 'backend'
sys.path.append(str(ROOT_DIR))

import openai
from config import Config
from utils import get_openai_api_key, download_files_from_bucket, upload_to_bucket


def profile_pers(profil):
    config = Config()
    env = config.ENV

    # Configurer l'API OpenAI
    api_key = get_openai_api_key(env, config)
    client = openai.OpenAI(api_key=api_key)

    # Configurer les chemins
    if env == "local":
        profil_path = config.LOCAL_BASE_PATH / profil / "profil"
        source_profil_path = config.LOCAL_BASE_PATH / profil / "sources"
        exp_output = profil_path / "pers.txt"
        prompt_path = config.LOCAL_PROMPT_PATH / "prompt_profile_pers.txt"
    else:
        source_profil_path = config.TEMP_PATH / profil / "sources"
        exp_output = f"{profil}/profil/pers.txt"
        prompt_path = config.LOCAL_PROMPT_PATH / "prompt_profile_pers.txt"
        # Télécharger les fichiers depuis le bucket
        download_files_from_bucket(config.BUCKET_NAME, f"{profil}/sources/", source_profil_path)

    # Lire les contenus des fichiers sources
    with open(prompt_path, "r", encoding="utf-8") as file:
        system_prompt = file.read()

    textes = []
    #On récupère tous les fichiers txt présents dans le dossier source_profil_path
    for txt_file in source_profil_path.glob("*.txt"):
        with open(txt_file, "r", encoding="utf-8") as file:
            job_description = file.read()
            textes.append(job_description)

    # Préparer le prompt en donnant toutes les textes des sources
    user_prompt = f"""
    Voici les données nécessaires pour votre analyse :\n
    {textes}
    """

    try:
        # Appeler l'API de ChatGPT

        response = client.chat.completions.create(
        model="gpt-4o",
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
            "type": "text"
        },
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
        
        # Extraire le contenu généré
        condensed_description = response.choices[0].message.content.strip()


        if env == "local":
            # Sauvegarder localement
            Path(exp_output).parent.mkdir(parents=True, exist_ok=True)
            Path(exp_output).write_text(condensed_description, encoding="utf-8")
        else:
            # Envoyer au bucket
            upload_to_bucket(config.BUCKET_NAME, exp_output, condensed_description)

        print(f"Fiche de poste condensée enregistrée dans : {exp_output}")

    except openai.APIError as e:
        print(f"Erreur API : {e}")
    except openai.BadRequestError as e:
        print(f"Requête invalide : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")



if __name__ == "__main__":
    profil = "j4WSNb5TuQVwVwSpq65N7o06GC52"

    profile_pers(profil)