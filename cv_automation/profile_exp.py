import openai
import os
from pathlib import Path
import json

def save_text_to_file(exp_output, text):
    # Créer le chemin si nécessaire
    file_path = Path(exp_output)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Enregistrer le contenu dans le fichier cible
    file_path.write_text(text, encoding="utf-8")



def profile_exp(profil):
    # Récupérer la clé API depuis les variables d'environnement
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("La clé API OpenAI n'est pas définie dans les variables d'environnement.")
    
    # Configurer l'API OpenAI avec un client
    client = openai.OpenAI(api_key=api_key)

    openai.api_key = api_key

    # Définir les chemins des fichiers
    profil_path = Path(f"data_local/{profil}/profil")
    source_profil_path = Path(f"data_local/{profil}/sources")
    current_dir = Path(__file__).parent  # Obtenir le répertoire du script
    prompt_path = current_dir / "prompt_profile_exp.txt"  # Construire le chemin absolu
    exp_output = profil_path / "exp.json"

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
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )

        # Extraire le contenu généré
        condensed_description = response.choices[0].message.content.strip()


        save_text_to_file(exp_output, condensed_description)

        print(f"Fiche de poste condensée enregistrée dans : {exp_output}")

    except openai.APIError as e:
        print(f"Erreur API : {e}")
    except openai.BadRequestError as e:
        print(f"Requête invalide : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")



if __name__ == "__main__":
    profil = "Alix1"

    profile_exp(profil)