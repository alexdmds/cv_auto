import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent  # Chemin vers 'backend'
sys.path.append(str(ROOT_DIR))

import openai
from utils import get_openai_api_key, get_file, save_file, get_prompt, get_files_in_directory, add_tokens_to_users

def profile_exp(profil):
    """
    Analyse les fichiers texte pour un profil donné et génère un fichier JSON avec les résultats.
    """

    # Configurer l'API OpenAI
    api_key = get_openai_api_key()
    client = openai.OpenAI(api_key=api_key)

    # Configurer les chemins
    source_profil_path = f"{profil}/sources"
    exp_output = f"{profil}/profil/exp.json"
    prompt_name = "prompt_profile_exp.txt"

    # Récupérer les fichiers texte depuis le dossier source
    try:
        source_files = get_files_in_directory(source_profil_path)

        print(f"Nombre de fichiers trouvés dans {source_profil_path} : {len(source_files)}")

        # Lire le contenu des fichiers texte
        textes = []
        for file_path in source_files:
            if file_path.suffix == ".txt":  # Traiter uniquement les fichiers .txt
                file_content = get_file(str(file_path))
                with open(file_content, "r", encoding="utf-8") as file:
                    textes.append(file.read())

        if not textes:
            raise FileNotFoundError("Aucun fichier texte valide trouvé pour l'analyse.")

        system_prompt = get_prompt(prompt_name)

    except FileNotFoundError as e:
        print(f"Erreur : {e}")
        return

    # Préparer le prompt
    user_prompt = f"""
    Voici les données nécessaires pour votre analyse :\n
    {textes}
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
            temperature=1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        # Extraire le contenu généré
        condensed_description = response.choices[0].message.content.strip()

        txt_input = user_prompt + system_prompt
        txt_output = condensed_description
        txt_total = txt_input + txt_output

        add_tokens_to_users(profil, txt_total)

        # Sauvegarder le fichier JSON
        save_file(exp_output, condensed_description)
        print(f"Fichier JSON généré et sauvegardé dans : {exp_output}")

    except openai.APIError as e:
        print(f"Erreur API : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")


if __name__ == "__main__":
    profil = "j4WSNb5TuQVwVwSpq65N7o06GC52"
    profile_exp(profil)