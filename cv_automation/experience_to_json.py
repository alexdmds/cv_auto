import os
import json
import re
from openai import OpenAI

# 🔐 Assurez-vous que la clé API est définie dans la variable d'environnement
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def load_text_file(file_path):
    """
    Charge le fichier texte brut.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_text = file.read()
    return raw_text


def clean_text(raw_text):
    """
    Nettoie le texte brut pour supprimer les espaces, tabulations et lignes vides excessives.
    """
    text = re.sub(r'\n+', '\n', raw_text)  # Supprime les lignes vides multiples
    text = re.sub(r'\t+', ' ', text)  # Remplace les tabulations par des espaces
    text = re.sub(r' +', ' ', text)  # Remplace les multiples espaces par un seul espace
    text = text.strip()  # Supprime les espaces au début et à la fin
    return text


def call_openai_to_generate_json(experience_text, fiche_poste_text):
    """
    Appelle l'API OpenAI pour générer un JSON structuré avec les expériences professionnelles adaptées au poste visé.
    """
    prompt = f"""
    Tu es un assistant expert en création de CV. 
    À partir du texte brut de l'expérience et de la fiche de poste ci-dessous, 
    génère un **JSON structuré** listant uniquement les expériences pertinentes et adaptées au poste visé.
    **Attention** : 
    - Adapte le contenu à la langue de la fiche de poste (s'il est en français, garde le français, s'il est en anglais, garde l'anglais). 
    - Ne garde que les expériences qui correspondent aux compétences et missions demandées dans la fiche de poste. 
    - Sois précis, mais concis. 
    - Si le lieu de l'expérience n'est pas explicitement mentionné, laisse-le vide (""). 
    - La structure du JSON doit être la suivante : 
      [
        {{
          "post": "Nom du poste",
          "company": "Nom de l'entreprise",
          "location": "Lieu de l'expérience",
          "dates": "Dates de l'expérience",
          "description": "Description concise de l'expérience, adaptée au poste visé"
        }},
        ...
      ]
    
    🔽 **Expérience brute** 🔽
    {experience_text}
    
    🔽 **Fiche de poste** 🔽
    {fiche_poste_text}
    """
    
    print("🔄 Envoi du texte à OpenAI pour structuration...")
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # ⚠️ Extraction du contenu structuré
        structured_content = response.choices[0].message.content

    except Exception as e:
        print(f"⚠️ Erreur lors de l'appel à OpenAI : {e}")
        structured_content = None
    
    return structured_content


def convert_to_json(content):
    """
    Convertit le contenu renvoyé par OpenAI en JSON.
    """
    try:
        json_data = json.loads(content)
        return json_data
    except json.JSONDecodeError as e:
        print(f"⚠️ Erreur lors de la conversion en JSON : {e}")
        return None


def save_to_json_file(data, output_path="experiences_structured.json"):
    """
    Enregistre le contenu JSON dans un fichier.
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"✅ Fichier JSON structuré enregistré sous : {output_path}")


def main(experience_path, fiche_poste_path, output_path="experiences_structured.json"):
    """
    Fonction principale pour extraire le contenu des fichiers et générer le fichier JSON structuré.
    """
    print(f"📄 Chargement du fichier d'expérience à partir de {experience_path}...")
    experience_text = load_text_file(experience_path)
    
    print(f"📄 Chargement du fichier de la fiche de poste à partir de {fiche_poste_path}...")
    fiche_poste_text = load_text_file(fiche_poste_path)
    
    print(f"🔍 Nettoyage des textes...")
    clean_experience_text = clean_text(experience_text)
    clean_fiche_poste_text = clean_text(fiche_poste_text)
    
    print(f"🧠 Appel de l'API OpenAI pour générer le JSON structuré...")
    structured_content = call_openai_to_generate_json(clean_experience_text, clean_fiche_poste_text)
    
    if structured_content:
        print(f"✅ Structure du JSON générée avec succès.")
        json_data = convert_to_json(structured_content)
        if json_data:
            save_to_json_file(json_data, output_path)
    else:
        print(f"❌ Échec de la génération du JSON structuré.")
        

if __name__ == "__main__":
    # Chemins des fichiers texte bruts
    experience_path = 'data_enrichie/experience.txt'  # Chemin du fichier experience.txt
    fiche_poste_path = 'fiche_poste.txt'  # Chemin du fichier fiche_de_poste.txt
    main(experience_path, fiche_poste_path)