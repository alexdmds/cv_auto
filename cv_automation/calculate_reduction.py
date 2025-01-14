import base64
import json
from openai import OpenAI
from pathlib import Path


def calculate_reduction(profil, cv):
    # Initialisez le client OpenAI
    client = OpenAI()
    cv_path = Path(f"data_local/{profil}/cvs/{cv}")
    # Chemin vers l'image locale
    image_path = cv_path / "cv_image.jpg"
    current_dir = Path(__file__).parent  # Obtenir le répertoire du script
    prompt_path = current_dir / "prompt_calculate_reduction.txt"  # Construire le chemin absolu

    # Chemin pour enregistrer le fichier JSON de sortie
    output_json_path = cv_path / "adjust.json"

    # Lire l'image et l'encoder en base64
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    with open(prompt_path, "r", encoding="utf-8") as file:
        system_prompt = file.read()

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
            "content": f"data:image/jpeg;base64,{encoded_image}"
        }
    ],
    response_format={
        "type": "json_object"
    },
    temperature=0.39,
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


if __name__ == "__main__":
    profil = "Alexis1"
    cv = "laposte"
    calculate_reduction(profil, cv)