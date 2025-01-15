import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent  # Chemin vers 'backend'
sys.path.append(str(ROOT_DIR))

import openai
from config import Config
from backend.utils_old import get_openai_api_key, upload_to_bucket


def refine_job_description(profil, cv):
    """
    Condense une fiche de poste en 500 mots maximum en utilisant l'API de ChatGPT.

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
        cv_path = config.LOCAL_BASE_PATH / profil / "cvs" / cv
    else:
        cv_path = config.TEMP_PATH / profil / "cvs" / cv

    post_source = cv_path / "source_raw.txt"

    if not post_source.exists():
        raise FileNotFoundError(f"Le fichier de la fiche de poste n'existe pas : {post_source}")

    # Lire le contenu du fichier source
    with open(post_source, "r", encoding="utf-8") as file:
        job_description = file.read()

    # Préparer le message pour l'API
    prompt = (
        "Condensez la fiche de poste suivante, dans la même langue, en gardant tous les éléments importants, "
        "dans une limite de 500 mots. Conservez le ton professionnel et les détails essentiels.\n\n"
        f"Fiche de poste :\n{job_description}\n\nCondensé :"
    )

    try:
        # Appeler l'API de ChatGPT
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant expert en rédaction professionnelle."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,  # Limite de tokens pour le condensé
            temperature=0.7
        )

        # Extraire le contenu généré
        condensed_description = response.choices[0].message.content.strip()
        
        exp_output = cv_path / "source_refined.txt"
        if env == "local":
            # Sauvegarder localement
            Path(exp_output).parent.mkdir(parents=True, exist_ok=True)
            Path(exp_output).write_text(condensed_description, encoding="utf-8")
        else:
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
    cv = "cv1"

    refine_job_description(profil, cv)