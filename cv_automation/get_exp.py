import openai
import os
from pathlib import Path
import json


def get_exp(profil, cv):
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
    exp_source = profil_path / "exp.json"
    post_source = cv_path / "source_refined.txt"
    exp_output = cv_path / "exp.json"

    if not exp_source.exists():
        raise FileNotFoundError(f"Le fichier des expériences n'existe pas : {exp_source}")
    if not post_source.exists():
        raise FileNotFoundError(f"Le fichier de la fiche de poste n'existe pas : {post_source}")

    # Lire les contenus des fichiers sources
    with open(exp_source, "r", encoding="utf-8") as file:
        experiences = json.load(file)
    with open(post_source, "r", encoding="utf-8") as file:
        job_description = file.read()

    # Préparer le prompt
    user_prompt = f"""
    Voici les données nécessaires pour votre analyse :\n\n1. **Fiche de poste** :\n
    {job_description}
    \n2. **Expériences professionnelles du candidat** (au format JSON) :\n
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
                "text": "You are an expert assistant specialized in crafting professional CVs. Your task is to transform a job description and a candidate’s work experiences JSON into a structured **JSON** optimized for the \"Professional Experience\" section of a CV. The tone should be very professional, focusing on achievements, successes, and factual skills, aligning with the job description's requirements. Ensure that the output is in the same language as the job description.\n\n### Instructions:\n\n1. **Expected Output**:\n   - Provide a structured JSON with the following keys:\n     - `\"intitule_section\"`: Set to the translation of \"Professional Experience\" in the language of the job description.\n     - `\"experiences\"`: A list of CV-optimized experiences. Each experience includes:\n       - `post`: Job title.\n       - `company`: Company name.\n       - `location`: Job location.\n       - `dates`: Job period (text format).\n       - `bullets`: A list of 3 to 5 key points highlighting relevant responsibilities and achievements, focusing on concrete successes and factual skills.\n\n2. **Experience Selection**:\n   - Maintain between **3 and 5** of the most relevant experiences for the job description.\n   - Prioritize experiences directly aligned with the skills, responsibilities, and requirements outlined in the job description.\n   - Order the experiences in reverse chronological order (most recent to oldest).\n\n3. **Details in `bullets`**:\n   - Expand on points in the most relevant experiences.\n   - Be precise, concise, and impact-focused with a professional tone suitable for the CV.\n\n4. **Strict Format**:\n   - The output must be a raw and valid JSON.\n   - Avoid explanatory text, headers, or elements outside of the structured JSON.\n   - Ensure the language used in the JSON output matches the language of the job description.\n\n### Output Format\n\nThe final output should be provided as a well-structured JSON, strictly adhering to the format specified.\n\n### Example:\n\n```json\n{\n    \"intitule_section\": \"Expérience Professionnelle\",\n    \"experiences\": [\n        {\n            \"post\": \"Senior Consultant\",\n            \"company\": \"EY\",\n            \"location\": \"Paris, France\",\n            \"dates\": \"February 2023 – Present\",\n            \"bullets\": [\n                \"Successfully led Renault’s FLMDH project, creating a GCP Data Hub for automotive and financial integration.\",\n                \"Expertly deployed CI/CD pipelines and dbt workflows, optimizing processes with Dockerized solutions on Cloud Run.\",\n                \"Enhanced data quality for Enedis, significantly optimizing energy data exchanges.\"\n            ]\n        },\n        {\n            \"post\": \"Co-founder & CTO\",\n            \"company\": \"Kadi\",\n            \"location\": \"Paris, France\",\n            \"dates\": \"2022 – 2024\",\n            \"bullets\": [\n                \"Pioneered the development of a Faster R-CNN model on Google Cloud for automated receipt detection.\",\n                \"Designed robust technical architecture and led the team to successful deployments.\"\n            ]\n        },\n        {\n            \"post\": \"Energy Market Analysis Intern\",\n            \"company\": \"TotalEnergies\",\n            \"location\": \"Paris, France\",\n            \"dates\": \"February 2020 – July 2020\",\n            \"bullets\": [\n                \"Conducted comprehensive analysis of global LNG and electricity markets, offering strategic insights.\",\n                \"Developed advanced Python tools that optimized LNG carrier routes and automated key workflows.\"\n            ]\n        }\n    ]\n}\n```"
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
        temperature=0.25,
        max_completion_tokens=2048,
        top_p=0.9,
        frequency_penalty=0,
        presence_penalty=0
        )

        # Extraire le contenu généré
        condensed_description = response.choices[0].message.content.strip()

        # Enregistrer le contenu dans le fichier cible
        with open(exp_output, "w", encoding="utf-8") as file:
            file.write(condensed_description)

        print(f"Fiche de poste condensée enregistrée dans : {exp_output}")

    except openai.APIError as e:
        print(f"Erreur API : {e}")
    except openai.InvalidRequestError as e:
        print(f"Requête invalide : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")



if __name__ == "__main__":
    profil = "Alexis1"
    cv = "poste1"

    get_exp(profil, cv)