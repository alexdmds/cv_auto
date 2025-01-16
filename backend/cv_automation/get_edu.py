import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent  # Chemin vers 'backend'
sys.path.append(str(ROOT_DIR))

import openai
from utils import get_openai_api_key, get_file, save_file, get_prompt, add_tokens_to_users
import json


def get_edu(profil, cv):
    """
    Génère un JSON "weights.json" en analysant une fiche de poste et les expériences professionnelles du candidat.

    :param profil: Nom du profil (sous-dossier dans `data_local`).
    :param cv: Nom du CV (sous-dossier dans `profil/cvs`).
    """

    # Configurer l'API OpenAI
    api_key = get_openai_api_key()
    client = openai.OpenAI(api_key=api_key)

    # Configurer les chemins
    edu_source_path = f"{profil}/profil/edu.json"
    post_source_path = f"{profil}/cvs/{cv}/source_refined.txt"
    output_path = f"{profil}/cvs/{cv}/edu.json"
    prompt_name = "prompt_edu.txt"

    # Récupérer les fichiers nécessaires
    try:
        edu_source = get_file(edu_source_path)
        post_source = get_file(post_source_path)

        # Si une liste est retournée, prenez le premier fichier
        if isinstance(edu_source, list):
            edu_source = edu_source[0]
        if isinstance(post_source, list):
            post_source = post_source[0]

        # Lire les contenus des fichiers sources
        with open(edu_source, "r", encoding="utf-8") as file:
            experiences = json.load(file)
        with open(post_source, "r", encoding="utf-8") as file:
            job_description = file.read()

        # Récupérer le contenu du prompt
        system_prompt = get_prompt(prompt_name)

    except FileNotFoundError as e:
        print(f"Erreur : {e}")
        return

    # Préparer le prompt
    user_prompt = f"""
    Voici les données nécessaires pour votre analyse :\n\n1. **Fiche de poste** :\n
    {job_description}
    \n2. **Formation du candidat** (au format JSON) :\n
    {json.dumps(experiences, indent=4)}
    \nGénérez le JSON final en suivant scrupuleusement les règles indiquées dans vos instructions.
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
                "type": "json_object"
            },
            temperature=0.21,
            max_completion_tokens=2048,
            top_p=0.3,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Extraire le contenu généré
        condensed_description = response.choices[0].message.content.strip()
        txt_input = user_prompt + system_prompt
        txt_output = condensed_description
        txt_total = txt_input + txt_output

        add_tokens_to_users(profil, txt_total)
        # Sauvegarder le contenu généré
        save_file(output_path, condensed_description)
        print(f"Fichier edu.json généré et sauvegardé dans : {output_path}")

    except openai.APIError as e:
        print(f"Erreur API : {e}")
    except openai.BadRequestError as e:
        print(f"Requête invalide : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")


if __name__ == "__main__":
    profil = "j4WSNb5TuQVwVwSpq65N7o06GC52"
    cv = "cv1"
    get_edu(profil, cv)