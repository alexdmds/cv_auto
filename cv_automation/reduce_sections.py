import json
from pathlib import Path


from openai import OpenAI



# Fonction simulateur pour la réduction
def reduce(section, percentage):
    print(f"Réduction de {percentage}% appliquée à la section '{section}'")

    client = OpenAI()
    current_dir = Path(__file__).parent  # Obtenir le répertoire du script
    prompt_path = current_dir / "prompt_reduction.txt"  # Construire le chemin absolu
    cv_path = Path(f"data_local/{profil}/cvs/{cv}")

    if section == 1:
        output_json_path = cv_path / "exp.json"
    elif section == 2:
        output_json_path = cv_path / "edu.json"
    elif section == 3:
        output_json_path = cv_path / "skills.json"
    elif section == 4:
        output_json_path = cv_path / "projects.json"

    with open(prompt_path, "r", encoding="utf-8") as file:
        system_prompt = file.read()
    with open(output_json_path, "r", encoding="utf-8") as file:
        json_file = json.load(file)
    
    # Préparer le prompt
    user_prompt = f"""
    Voici le JSON à réduire :\n
    {json.dumps(json_file, indent=4)}
    \nRéduis-le de {percentage}% et retoune-le en suivant les règles scrupuleusement
    """

    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
        "role": "system",
        "content": [
            {
            "text": system_prompt,
            "type": "text"
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": user_prompt
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
    # Extraire la réponse JSON avec notation par points
    response_json = response.choices[0].message.content

    with open(output_json_path, "w") as output_file:
        json.dump(json.loads(response_json), output_file, indent=4)

    print(f"JSON de sortie enregistré dans : {output_json_path}")

def apply_reduce(profil, cv):
    # Chemin vers le fichier JSON d'entrée
    cv_path = Path(f"data_local/{profil}/cvs/{cv}")
    input_json_path = cv_path / "adjust.json"

    # Charger le JSON depuis le fichier
    with open(input_json_path, "r") as json_file:
        data = json.load(json_file)

    # Vérifier la présence de la clé "adjustments"
    if "adjustments" in data:
        for adjustment in data["adjustments"]:
            section = adjustment.get("section")
            percentage = adjustment.get("suggested_reduction_percentage")
            
            if section and percentage is not None:
                # Appeler la fonction reduce pour chaque section
                reduce(section, percentage)
            else:
                print(f"Section ou pourcentage manquant dans : {adjustment}")
    else:
        print("Aucune clé 'adjustments' trouvée dans le JSON.")

if __name__ == "__main__":
    profil = "Alexis1"
    cv = "poste1"
    apply_reduce(profil, cv)