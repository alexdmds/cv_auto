import openai
import os
from pathlib import Path


def refine_job_description(profil, cv):
    """
    Condense une fiche de poste en 500 mots maximum en utilisant l'API de ChatGPT.

    :param profil: Nom du profil (sous-dossier dans `data_local`).
    :param cv: Nom du CV (sous-dossier dans `profil/cvs`).
    """
    # Récupérer la clé API depuis les variables d'environnement
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("La clé API OpenAI n'est pas définie dans les variables d'environnement.")

    # Configurer l'API OpenAI avec un client
    client = openai.OpenAI(api_key=api_key)

    # Définir les chemins des fichiers
    base_path = Path(f"data_local/{profil}/cvs/{cv}")
    source_file = base_path / "source_raw.txt"
    refined_file = base_path / "source_refined.txt"

    if not source_file.exists():
        raise FileNotFoundError(f"Le fichier source n'existe pas : {source_file}")

    # Lire le contenu du fichier source
    with open(source_file, "r", encoding="utf-8") as file:
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

        # Enregistrer le contenu dans le fichier cible
        with open(refined_file, "w", encoding="utf-8") as file:
            file.write(condensed_description)

        print(f"Fiche de poste condensée enregistrée dans : {refined_file}")

    except openai.APIError as e:
        print(f"Erreur API : {e}")
    except openai.BadRequestError as e:
        print(f"Requête invalide : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")


if __name__ == "__main__":
    profil = "Alix1"
    cv = "vancleef"

    refine_job_description(profil, cv)