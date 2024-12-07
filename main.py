import json
import os
from reportlab.platypus import SimpleDocTemplate, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

# Import des sections
from sections.header import create_header
from sections.education import create_education_section
from sections.experience import create_experience_section
from sections.skills import create_skills_section
from sections.hobbies import create_hobbies_section


def load_json(file_path):
    """Charge les données d'un fichier JSON."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def load_cv_data():
    """Charge toutes les données du CV à partir des fichiers JSON."""
    base_path = os.path.join(os.path.dirname(__file__), 'cv_data')

    data = {}
    data.update(load_json(os.path.join(base_path, 'personal_info.json')))  # Données personnelles
    data['experience'] = load_json(os.path.join(base_path, 'experience.json'))  # Expérience professionnelle
    data['education'] = load_json(os.path.join(base_path, 'education.json'))  # Formation
    data.update(load_json(os.path.join(base_path, 'skills.json')))  # Compétences
    data['hobbies'] = load_json(os.path.join(base_path, 'hobbies.json'))  # Centres d'intérêt
    
    return data


def generate_cv(output_file, data):
    # Initialiser le document
    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm
    )
    
    elements = []

    # **1. En-tête**
    elements += create_header(data)

    # **2. Expérience professionnelle**
    elements += create_experience_section(data)

    # **3. Éducation**
    elements += create_education_section(data)

    # **4. Compétences techniques**
    elements += create_skills_section(data)
    
    # **5. Centres d'intérêt**
    elements += create_hobbies_section(data)
    
    # Générer le PDF
    doc.build(elements)
    print(f"CV généré : {output_file}")


if __name__ == '__main__':
    # Charger les données à partir des fichiers sources
    cv_data = load_cv_data()

    # Générer le CV
    generate_cv("CV_Alexis_de_Monts.pdf", cv_data)