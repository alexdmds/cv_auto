import openai
import os
from pathlib import Path
import json


def get_edu(profil, cv):
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
    edu_source = profil_path / "edu.json"
    post_source = cv_path / "source_refined.txt"
    edu_output = cv_path / "edu.json"
    current_dir = Path(__file__).parent  # Obtenir le répertoire du script
    prompt_path = current_dir / "prompt_edu.txt"  # Construire le chemin absolu


    if not edu_source.exists():
        raise FileNotFoundError(f"Le fichier des expériences n'existe pas : {edu_source}")
    if not post_source.exists():
        raise FileNotFoundError(f"Le fichier de la fiche de poste n'existe pas : {post_source}")

    # Lire les contenus des fichiers sources
    with open(edu_source, "r", encoding="utf-8") as file:
        experiences = json.load(file)
    with open(post_source, "r", encoding="utf-8") as file:
        job_description = file.read()
    with open(prompt_path, "r", encoding="utf-8") as file:
        system_prompt = file.read()

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

        # Enregistrer le contenu dans le fichier cible
        with open(edu_output, "w", encoding="utf-8") as file:
            file.write(condensed_description)

        print(f"Fiche de poste condensée enregistrée dans : {edu_output}")

    except openai.APIError as e:
        print(f"Erreur API : {e}")
    except openai.BadRequestError as e:
        print(f"Requête invalide : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")



if __name__ == "__main__":
    profil = "Alix1"
    cv = "vancleef"

    get_edu(profil, cv)