import openai
import os
from pathlib import Path
import json


def get_weights(profil, cv):
    """
    Génère un JSON "weights.json" en analysant une fiche de poste et les expériences professionnelles du candidat.

    :param profil: Nom du profil (sous-dossier dans `data_local`).
    :param cv: Nom du CV (sous-dossier dans `profil/cvs`).
    """
    # Récupérer la clé API depuis les variables d'environnement
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("La clé API OpenAI n'est pas définie dans les variables d'environnement.")

    openai.api_key = api_key

    # Définir les chemins des fichiers
    profil_path = Path(f"data_local/{profil}/profil")
    cv_path = Path(f"data_local/{profil}/cvs/{cv}")
    exp_source = profil_path / "exp.json"
    post_source = cv_path / "source_refined.txt"
    weights_file = cv_path / "weights.json"

    if not exp_source.exists():
        raise FileNotFoundError(f"Le fichier des expériences n'existe pas : {exp_source}")
    if not post_source.exists():
        raise FileNotFoundError(f"Le fichier de la fiche de poste n'existe pas : {post_source}")

    # Lire les contenus des fichiers sources
    with open(exp_source, "r", encoding="utf-8") as file:
        experiences = json.load(file)
    with open(post_source, "r", encoding="utf-8") as file:
        job_description = file.read()

    # Préparer le schéma JSON attendu
    json_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "exp_choisie": {"type": "string", "description": "L'order de l'expérience choisie."},
                "place": {"type": "integer", "description": "La position dans le CV."},
                "weight": {"type": "integer", "description": "L'importance de l'expérience."}
            },
            "required": ["exp_choisie", "place", "weight"],
            "additionalProperties": False
        }
    }

    # Préparer le prompt
    prompt = f"""
    Analysez les expériences professionnelles d'un candidat en fonction de la fiche de poste ci-dessous et produisez un JSON respectant le schéma défini.

    ### Fiche de poste :
    {job_description}

    ### Expériences professionnelles (JSON) :
    {json.dumps(experiences, indent=4)}

    ### Schéma JSON attendu :
    {json.dumps(json_schema, indent=4)}

    Analysez et générez la sortie strictement conforme au schéma.
    """

    try:
        # Appeler l'API OpenAI avec le schéma JSON
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant expert en analyse de CV."},
                {"role": "user", "content": prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": json_schema
            },
            max_tokens=2000,
            temperature=0.7
        )

        # Extraire le contenu structuré
        weights = response.choices[0].message.parsed

        # Enregistrer le contenu dans le fichier cible
        with open(weights_file, "w", encoding="utf-8") as file:
            json.dump(weights, file, indent=4)

        print(f"JSON des poids enregistré avec succès dans : {weights_file}")

    except openai.error.APIError as e:
        print(f"Erreur API : {e}")
    except openai.error.InvalidRequestError as e:
        print(f"Requête invalide : {e}")
    except openai.error.AuthenticationError as e:
        print(f"Erreur d'authentification : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")


if __name__ == "__main__":
    profil = "Alexis1"
    cv = "poste1"

    get_weights(profil, cv)