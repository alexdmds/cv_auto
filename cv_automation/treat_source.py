import os
import re
from openai import OpenAI

# ✅ Configurez votre clé API OpenAI ici
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")  # Assurez-vous que la clé API est définie dans les variables d'environnement
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
    # Supprime les lignes vides multiples et les espaces inutiles
    text = re.sub(r'\n+', '\n', raw_text)  # Supprime les sauts de ligne excessifs
    text = re.sub(r'\t+', ' ', text)  # Remplace les tabulations par des espaces
    text = re.sub(r' +', ' ', text)  # Remplace les multiples espaces par un espace
    text = text.strip()  # Supprime les espaces au début et à la fin
    return text


def call_openai_to_structure_cv(raw_text):
    """
    Appelle l'API OpenAI pour structurer le texte en format de CV organisé.
    """
    prompt = f"""
    Tu es un assistant spécialisé dans la structuration de profils professionnels. 
    Ta mission est d'extraire et de restituer **toutes les informations utiles** du texte brut suivant, de manière complète et concise. 
    Ne te répète pas, mais ne laisse **aucune information importante de côté**.
    Présente les informations de manière organisée et claire, en respectant la structure suivante :

    1️⃣ **Informations personnelles** :
    - Nom complet 
    - Titre professionnel 
    - E-mail 
    - Téléphone 
    - Localisation (ville, région, pays) 
    - Liens vers des profils (LinkedIn, GitHub, site personnel, etc.) 

    2️⃣ **Expériences professionnelles** :
    - **Poste occupé** (intitulé du poste) 
    - **Entreprise** (nom de l'entreprise) 
    - **Dates précises** (mois/année de début et de fin) 
    - **Description concise des missions et projets clés** (mets l'accent sur les résultats ou réalisations marquantes) 
    - **Compétences et outils mobilisés** (technologies, langages, frameworks, outils utilisés) 

    3️⃣ **Éducation** :
    - **Diplômes obtenus** (nom complet) 
    - **Écoles ou universités** (nom complet) 
    - **Dates** (mois/année de début et de fin) 
    - **Spécialisations et majeures** (par exemple, data science, finance, IA, etc.) 
    - **Projets ou travaux notables** (par exemple, mémoire, projet de recherche, projet académique significatif) 

    4️⃣ **Compétences techniques** :
    - **Langages de programmation** (Python, SQL, etc.) 
    - **Outils et technologies** (GCP, AWS, BigQuery, etc.) 
    - **Certifications et formations techniques** (AWS Certified, Google Cloud Certification, etc.) 
    - **Frameworks et bibliothèques** (Pandas, NumPy, Scikit-learn, etc.) 
    - **Outils de visualisation et d'analyse** (Power BI, Tableau, Looker, etc.) 

    5️⃣ **Langues et centres d'intérêt** :
    - **Langues parlées** (indique le niveau : natif, courant, avancé, intermédiaire, etc.) 
    - **Centres d'intérêt et passions** (sport, art, activités extra-professionnelles, engagement associatif, etc.) 

    💡 **Règles à suivre** :
    1️⃣ **Ne répète pas les informations** déjà mentionnées ailleurs (sauf si elles sont nécessaires pour la compréhension). 
    2️⃣ Si une information est incomplète (exemple : "Data Engineer chez Renault"), n'essaie pas de deviner, mais **indique simplement qu'il manque des informations**. 
    3️⃣ **Ne crée aucune information fictive**. Si une information manque, ne l'invente pas. 
    4️⃣ Ne simplifie pas les descriptions de projets et missions. Sois précis mais concis. 
    5️⃣ Respecte le format et la structure, avec des titres clairs et des listes organisées. 
    6️⃣ Les descriptions de projets doivent se concentrer sur les **résultats, impacts ou livrables concrets**. 

    🔽 **Voici le texte brut à structurer** 🔽
    {raw_text}
    """
    
    print("🔄 Envoi du texte à OpenAI pour structuration...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # ⚠️ Changement ici : on utilise des attributs au lieu des clés du dictionnaire
        structured_content = response.choices[0].message.content

    except Exception as e:
        print(f"⚠️ Erreur lors de l'appel à OpenAI : {e}")
        structured_content = None
    
    return structured_content


def save_to_file(content, output_path):
    """
    Enregistre le contenu structuré dans un fichier.
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"✅ Fichier structuré enregistré sous : {output_path}")


def main(text_path):
    """
    Fonction principale pour extraire le contenu du fichier texte brut et générer le fichier de sortie.
    """

    #output path reprend le nom du fichier brut et ajoute _structured et le met dans data_intermediate
    output_path = os.path.join('data_intermediate', os.path.basename(text_path).replace('.txt', '_structured.txt'))

    print(f"📄 Chargement du texte brut à partir de {text_path}...")
    raw_text = load_text_file(text_path)
    
    print(f"🔍 Nettoyage du texte brut...")
    clean_raw_text = clean_text(raw_text)
    
    print(f"🧠 Appel de l'API OpenAI pour structurer le CV...")
    structured_content = call_openai_to_structure_cv(clean_raw_text)
    
    if structured_content:
        print(f"✅ Structure du CV générée avec succès.")
        save_to_file(structured_content, output_path)
    else:
        print(f"❌ Échec de la structuration du CV.")
        

if __name__ == "__main__":
    # Chemin du fichier texte brut
    text_path = 'source_data/linkedin_brut.txt'  # Remplacez par le chemin de votre fichier texte
    main(text_path)