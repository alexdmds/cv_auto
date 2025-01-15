import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent.parent  # Chemin vers 'backend'
sys.path.append(str(ROOT_DIR))

import json
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
# Import des fonctions utilitaires
from utils import get_file, save_file

# Import des sections
from cv_automation.gen_pdf.sections.header import create_header
from cv_automation.gen_pdf.sections.education import create_education_section
from cv_automation.gen_pdf.sections.experience import create_experience_section
from cv_automation.gen_pdf.sections.skills import create_skills_section
from cv_automation.gen_pdf.sections.hobbies import create_hobbies_section




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
    # Chemins des fichiers nécessaires
    data_file_path = f"{profil}/cvs/{cv}/data_cv.json"
    photo_file_path = f"{profil}/photo.jpg"
    output_file_path = f"{profil}/cvs/{cv}/cv.pdf"

    # Charger les données JSON
    try:
        data_file = get_file(data_file_path)
        if isinstance(data_file, list):  # Si une liste est retournée
            data_file = data_file[0]

        data = load_json(data_file)

        # Définir un chemin par défaut pour la photo
        default_photo_path = Path("backend/cv_automation/gen_pdf/sections/photo_default.jpg")

        # Récupérer la photo (si disponible)
        try:
            photo_file = get_file(photo_file_path)
            if isinstance(photo_file, list):
                photo_file = photo_file[0]
        except FileNotFoundError:
            # Utiliser une photo par défaut si aucune photo n'est disponible
            if not default_photo_path.exists():
                raise FileNotFoundError(f"Le fichier photo par défaut n'existe pas : {default_photo_path}")
            photo_file = default_photo_path
            print(f"Photo non trouvée pour le profil, utilisation de la photo par défaut : {default_photo_path}")

    except FileNotFoundError as e:
        print(f"Erreur : {e}")
        return

    # Créer les répertoires nécessaires pour le fichier PDF
    output_dir = Path(output_file_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialiser le document PDF
    doc = SimpleDocTemplate(
        output_file_path,
        pagesize=A4,
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm
    )
    elements = []

    # **1. En-tête**
    elements += create_header(data, photo_file)

    # **2. Expérience professionnelle**
    elements += create_experience_section(data)

    # **3. Éducation**
    elements += create_education_section(data)

    # **4. Compétences techniques**
    elements += create_skills_section(data)

    # **5. Centres d'intérêt**
    elements += create_hobbies_section(data)

    # Générer le PDF
    try:
        doc.build(elements)
        print(f"CV généré avec succès : {output_file_path}")

        # Sauvegarder le fichier PDF dans l'environnement approprié
        save_file(output_file_path, Path(output_file_path).read_bytes())
    except Exception as e:
        print(f"Erreur lors de la génération du CV : {e}")


if __name__ == "__main__":
    profil = "j4WSNb5TuQVwVwSpq65N7o06GC52"
    cv = "cv1"
    generate_cv(profil, cv)