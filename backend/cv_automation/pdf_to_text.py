import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent  # Chemin vers 'backend'
sys.path.append(str(ROOT_DIR))

from PyPDF2 import PdfReader
from utils import process_files

def extract_text_from_pdf(pdf_path):
    """
    Extrait le texte d'un fichier PDF.
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def convert_source_pdf_to_txt(profil):
    """
    Convertit les fichiers PDF en fichiers texte pour un profil donné.
    """
    process_files(profil, ".pdf", ".txt", extract_text_from_pdf)


if __name__ == "__main__":
    # Exemple d'exécution pour un profil spécifique
    profil = "j4WSNb5TuQVwVwSpq65N7o06GC52"
    convert_source_pdf_to_txt(profil)