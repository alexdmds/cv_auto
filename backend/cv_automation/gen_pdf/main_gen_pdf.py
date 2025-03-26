import sys
from pathlib import Path
import json
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import logging
import os

# Configurer le logger
logging.basicConfig(
    level=logging.DEBUG,  # Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()  # Envoyer les logs à la sortie standard
    ]
)

logger = logging.getLogger(__name__)

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent.parent  # Chemin vers 'backend'
sys.path.append(str(ROOT_DIR))

# Import des fonctions utilitaires
from backend.utils_old import get_file, save_file

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


def build_pdf(profil, cv):
    """
    Génère un CV en PDF à partir des données dans `data_cv.json`.

    :param profil: Nom du profil (sous-dossier dans `data_local`).
    :param cv: Nom du CV (sous-dossier dans `profil/cvs`).
    """
    logger.info(f"Début de la génération du CV pour le profil : {profil}, CV : {cv}")

    # Chemins des fichiers nécessaires
    data_file_path = f"{profil}/cvs/{cv}/data_cv.json"
    photo_file_path = f"{profil}/photo.jpg"
    output_file_path = f"{profil}/cvs/{cv}/cv.pdf"

    # Charger les données JSON
    try:
        logger.debug(f"Chargement des données depuis : {data_file_path}")
        data_file = get_file(data_file_path)
        if isinstance(data_file, list):  # Si une liste est retournée
            data_file = data_file[0]

        data = load_json(data_file)
        logger.info("Données JSON chargées avec succès.")

        # Définir un chemin par défaut pour la photo
        # Ajouter le répertoire racine au chemin Python
        ROOT_DIR = Path(__file__).resolve().parent # Chemin du script
        default_photo_path = ROOT_DIR / "sections" / "photo_default.jpg"

        # Récupérer la photo (si disponible)
        try:
            logger.debug(f"Chargement de la photo depuis : {photo_file_path}")
            photo_file = get_file(photo_file_path)
            if isinstance(photo_file, list):
                photo_file = photo_file[0]
            logger.info("Photo chargée avec succès.")
        except FileNotFoundError:
            # Utiliser une photo par défaut si aucune photo n'est disponible
            if not default_photo_path.exists():
                logger.error(f"Le fichier photo par défaut n'existe pas : {default_photo_path}")
                raise FileNotFoundError(f"Le fichier photo par défaut n'existe pas : {default_photo_path}")
            photo_file = default_photo_path
            logger.warning(f"Photo non trouvée pour le profil, utilisation de la photo par défaut : {default_photo_path}")

    except FileNotFoundError as e:
        logger.error(f"Erreur lors du chargement des fichiers nécessaires : {e}")
        return

    # Créer les répertoires nécessaires pour le fichier PDF
    output_dir = Path(output_file_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Répertoire de sortie vérifié/créé : {output_dir}")

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
    try:
        logger.debug("Ajout de l'en-tête au document PDF.")
        elements += create_header(data, photo_file)
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'en-tête : {e}")

    # **2. Expérience professionnelle**
    try:
        logger.debug("Ajout des expériences professionnelles au document PDF.")
        elements += create_experience_section(data)
    except Exception as e:
        logger.error(f"Erreur lors de la création de la section expérience : {e}")

    # **3. Éducation**
    try:
        logger.debug("Ajout de la section éducation au document PDF.")
        elements += create_education_section(data)
    except Exception as e:
        logger.error(f"Erreur lors de la création de la section éducation : {e}")

    # **4. Compétences techniques**
    try:
        logger.debug("Ajout des compétences techniques au document PDF.")
        elements += create_skills_section(data)
    except Exception as e:
        logger.error(f"Erreur lors de la création de la section compétences : {e}")

    # **5. Centres d'intérêt**
    try:
        logger.debug("Ajout des centres d'intérêt au document PDF.")
        elements += create_hobbies_section(data)
    except Exception as e:
        logger.error(f"Erreur lors de la création de la section centres d'intérêt : {e}")

    # Générer le PDF
    try:
        logger.debug("Génération du fichier PDF.")
        doc.build(elements)
        logger.info(f"CV généré avec succès : {output_file_path}")

        # Sauvegarder le fichier PDF dans l'environnement approprié
        save_file(output_file_path, Path(output_file_path).read_bytes())
        logger.info("Fichier PDF sauvegardé avec succès.")
    except Exception as e:
        logger.error(f"Erreur lors de la génération du CV : {e}")


if __name__ == "__main__":
    profil = "Alexis1"
    cv = "augura"
    build_pdf(profil, cv)