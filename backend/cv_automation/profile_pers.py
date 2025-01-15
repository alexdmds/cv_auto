import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent  # Chemin vers 'backend'
sys.path.append(str(ROOT_DIR))

import openai
from utils import get_openai_api_key, get_file, save_file, get_prompt

def profile_pers(profil):
    """
    Analyse les fichiers texte pour un profil donné et génère un fichier texte avec les résultats.
    """

    # Configurer l'API OpenAI
    api_key = get_openai_api_key()
    client = openai.OpenAI(api_key=api_key)

    # Configurer les chemins
    source_profil_path = f"{profil}/sources/*.txt"
    exp_output = f"{profil}/profil/pers.txt"
    prompt_name = "prompt_profile_pers.txt"

    # Récupérer les fichiers texte depuis le chemin source
    try:
        source_files = get_file(source_profil_path)
        if not isinstance(source_files, list):  # Si un seul fichier est retourné
            source_files = [source_files]

        # Lire le contenu des fichiers texte
        textes = []
        for txt_file in source_files:
            with open(txt_file, "r", encoding="utf-8") as file:
                textes.append(file.read())

        # Récupérer le contenu du prompt
        system_prompt = get_prompt(prompt_name)

    except FileNotFoundError as e:
        print(f"Erreur : {e}")
        return

    # Préparer le prompt
    user_prompt = f"""
    Voici les données nécessaires pour votre analyse :\n
    {textes}
    """

    try:
        # Appeler l'API de ChatGPT
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        # Extraire le contenu généré
        condensed_description = response.choices[0].message.content.strip()

        # Sauvegarder le fichier texte
        save_file(exp_output, condensed_description)
        print(f"Fichier texte généré et sauvegardé dans : {exp_output}")

    except openai.APIError as e:
        print(f"Erreur API : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")


if __name__ == "__main__":
    profil = "j4WSNb5TuQVwVwSpq65N7o06GC52"
    profile_pers(profil)