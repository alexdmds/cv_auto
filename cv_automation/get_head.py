import openai
import os
from pathlib import Path
import json


def get_head(profil, cv):
    """
    Génère un JSON "weights.json" en analysant une fiche de poste et les expériences professionnelles du candidat.

    :param profil: Nom du profil (sous-dossier dans `data_local`).
    :param cv: Nom du CV (sous-dossier dans `profil/cvs`).
    """
    # Récupérer la clé API depuis les variables d'environnement
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("La clé API OpenAI n'est pas définie dans les variables d'environnement.")
    
    # Configurer l'API OpenAI avec un client
    client = openai.OpenAI(api_key=api_key)

    openai.api_key = api_key

    # Définir les chemins des fichiers
    profil_path = Path(f"data_local/{profil}/profil")
    cv_path = Path(f"data_local/{profil}/cvs/{cv}")
    profil_source = profil_path / "pers.txt"
    post_source = cv_path / "source_refined.txt"
    head_output = cv_path / "head.json"
    current_dir = Path(__file__).parent  # Obtenir le répertoire du script
    prompt_path = current_dir / "prompt_head.txt"  # Construire le chemin absolu


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

        # Enregistrer le contenu dans le fichier cible
        with open(head_output, "w", encoding="utf-8") as file:
            file.write(condensed_description)

        print(f"Fiche de poste condensée enregistrée dans : {head_output}")

    except openai.APIError as e:
        print(f"Erreur API : {e}")
    except openai.BadRequestError as e:
        print(f"Requête invalide : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")



if __name__ == "__main__":
    profil = "Alix1"
    cv = "vancleef"

    get_head(profil, cv)