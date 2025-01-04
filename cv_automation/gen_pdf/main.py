import json
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate
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


def generate_cv(profil, cv):
    """
    Génère un CV en PDF à partir des données dans `data_cv.json`.

    :param profil: Nom du profil (sous-dossier dans `data_local`).
    :param cv: Nom du CV (sous-dossier dans `profil/cvs`).
    """
    # Chemin de base
    base_path = Path(f"data_local/{profil}/cvs/{cv}")
    data_file = base_path / "data_cv.json"

    if not data_file.exists():
        raise FileNotFoundError(f"Le fichier agrégé 'data_cv.json' n'existe pas : {data_file}")

    # Charger les données
    data = load_json(data_file)

    # Initialiser le document PDF
    output_file = str(base_path / "cv.pdf")
    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm
    )
    elements = []

    photo_path = base_path / "photo.png"

    # **1. En-tête**
    elements += create_header(data, photo_path)

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
    print(f"CV généré avec succès : {output_file}")


if __name__ == '__main__':

    profil = "Alexis1"
    cv = "poste1"

    generate_cv(profil, cv)