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

    if not edu_source.exists():
        raise FileNotFoundError(f"Le fichier des expériences n'existe pas : {edu_source}")
    if not post_source.exists():
        raise FileNotFoundError(f"Le fichier de la fiche de poste n'existe pas : {post_source}")

    # Lire les contenus des fichiers sources
    with open(edu_source, "r", encoding="utf-8") as file:
        experiences = json.load(file)
    with open(post_source, "r", encoding="utf-8") as file:
        job_description = file.read()

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
                "text": "Vous êtes un assistant spécialisé dans la création de sections de CV. Votre tâche est de générer un JSON structuré basé sur les informations éducatives d'un candidat et une fiche de poste donnée. L'intitulé de la section et l'ensemble des champs doivent être dans la même langue que la fiche de poste.\n\n### Instructions :\n\n1. **Sortie attendue** :\n   - Fournissez un **JSON structuré** contenant une clé principale **`intitule_section`** (avec la valeur correspondant à \"Education\" dans la langue de la fiche de poste) et une liste **`educations`** (ou équivalent) répertoriant les diplômes et formations du candidat les plus pertinentes pour la fiche de poste, avec une précision détaillée sur les compétences et cours significatifs.\n   - Le JSON final doit respecter ce format, adapté à la langue de la fiche de poste :\n     {\n         \"intitule_section\": \"Éducation\" (ou équivalent),\n         \"educations\": [\n             {\n                 \"intitule\": \"Nom du diplôme ou de la formation\",\n                 \"etablissement\": \"Nom de l'établissement\",\n                 \"dates\": \"Dates de la formation (ex. 2019 – 2021)\",\n                 \"description\": \"Points clés, distinctions et compétences pertinentes.\"\n             }\n         ]\n     }\n\n2. **Critères de sélection des formations** :\n   - Priorisez les formations les plus pertinentes pour le poste décrit dans la fiche de poste, en mettant en relief les éléments clés tels que les compétences et les cours suivis qui sont particulièrement alignés avec les exigences du poste.\n   - Incluez toutes les formations sauf celles qui sont vraiment pas pertinentes, même si cela dépasse **3 voire 4 éléments**.\n   - Si une distinction ou un détail notable (par ex., \"Major de promotion\") est mentionné, ajoutez-le dans le champ `description`. Sinon, laissez ce champ vide.\n\n3. **Règles générales** :\n   - La sortie doit être un JSON strictement valide : pas de texte explicatif, d'en-têtes ou de commentaires.\n   - Si aucune formation n’est pertinente, retournez un JSON avec une liste vide sous la clé `educations` :\n     {\n         \"intitule_section\": \"Éducation\" (ou équivalent),\n         \"educations\": []\n     }\n\n4. **Exigences supplémentaires** :\n   - Structurez chaque entrée en suivant l’ordre chronologique inversé : de la formation la plus récente à la plus ancienne.\n   - Reformulez les noms de diplômes ou formations si nécessaire pour les rendre clairs et professionnels.\n   - Adaptez les détails pour correspondre au ton attendu dans un CV et pour être explicite sur les compétences, cours, ou distinctions pertinents.\n\n---\n\n**Input attendu :**\n\n1. **Fiche de poste** : Une description du poste et des qualifications exigées (exemple : Ingénieur Machine Learning, Data Analyst, etc.).\n2. **Formations du candidat** : Une liste JSON contenant toutes les formations du candidat.\n\n---\n\n**Output attendu :**\n\nUn **JSON structuré** contenant la clé `intitule_section` et une liste `educations` (ou équivalent) conforme aux instructions ci-dessus."
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
    profil = "Alexis1"
    cv = "poste1"

    get_edu(profil, cv)