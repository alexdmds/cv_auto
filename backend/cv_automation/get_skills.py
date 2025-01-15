import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent  # Chemin vers 'backend'
sys.path.append(str(ROOT_DIR))

import openai
from utils import get_openai_api_key, get_file, save_file, get_prompt


def get_skills(profil, cv):
    """
    Génère un JSON "skills.json" en analysant une fiche de poste et les expériences personnelles du candidat.

    :param profil: Nom du profil (sous-dossier dans `data_local`).
    :param cv: Nom du CV (sous-dossier dans `profil/cvs`).
    """

    # Configurer l'API OpenAI
    api_key = get_openai_api_key()
    client = openai.OpenAI(api_key=api_key)

    # Configurer les chemins
    profil_source_path = f"{profil}/profil/pers.txt"
    post_source_path = f"{profil}/cvs/{cv}/source_refined.txt"
    output_path = f"{profil}/cvs/{cv}/skills.json"
    prompt_name = "prompt_skills.txt"

    # Récupérer les fichiers nécessaires
    try:
        profil_source = get_file(profil_source_path)
        post_source = get_file(post_source_path)

        # Si une liste est retournée, prenez le premier fichier
        if isinstance(profil_source, list):
            profil_source = profil_source[0]
        if isinstance(post_source, list):
            post_source = post_source[0]

        # Lire les contenus des fichiers sources
        with open(profil_source, "r", encoding="utf-8") as file:
            profil_content = file.read()
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
    \n2. **Profil du candidat** :\n
    {profil_content}
    \nGénérez le JSON final en suivant scrupuleusement les règles indiquées dans vos instructions.
    """

    try:
        # Appeler l'API de ChatGPT
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_object"
            },
            temperature=0.38,
            max_completion_tokens=400,
            top_p=0.6,
            frequency_penalty=0,
            presence_penalty=0,
        )

        # Extraire le contenu généré
        condensed_description = response.choices[0].message.content.strip()

        # Sauvegarder le contenu généré
        save_file(output_path, condensed_description)
        print(f"Fichier skills.json généré et sauvegardé dans : {output_path}")

    except openai.APIError as e:
        print(f"Erreur API : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")


if __name__ == "__main__":
    profil = "j4WSNb5TuQVwVwSpq65N7o06GC52"
    cv = "cv1"
    get_skills(profil, cv)