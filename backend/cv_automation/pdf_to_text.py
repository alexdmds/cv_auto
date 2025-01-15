import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent  # Chemin vers 'backend'
sys.path.append(str(ROOT_DIR))

from PyPDF2 import PdfReader
from utils import get_files_in_directory, save_file, get_file

def extract_text_from_pdf(pdf_path):
    """
    Extrait le texte d'un fichier PDF.
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        raise ValueError(f"Erreur lors de la lecture du fichier PDF : {pdf_path} - {e}")

def convert_source_pdf_to_txt(profil):
    """
    Convertit les fichiers PDF en fichiers texte pour un profil donné.
    :param profil: Nom du profil (chemin relatif au répertoire de base).
    """
    try:
        # Récupérer tous les fichiers PDF dans le dossier sources du profil
        pdf_files = get_files_in_directory(f"{profil}/sources")

        for pdf_file in pdf_files:

            # Vérifier que le fichier a une extension PDF
            if pdf_file.suffix.lower() == ".pdf":
                # Obtenir le fichier local (télécharger si nécessaire)
                local_pdf_file = get_file(str(pdf_file))

                # Extraire le texte du PDF
                text = extract_text_from_pdf(local_pdf_file)

                # Définir le chemin du fichier texte de sortie
                txt_file_path = Path(pdf_file).with_suffix(".txt")

                # Sauvegarder le texte extrait dans un fichier texte
                save_file(str(txt_file_path), text)

    except FileNotFoundError as e:
        print(f"Erreur : {e}")
    except ValueError as e:
        print(f"Erreur de traitement : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")

if __name__ == "__main__":
    # Exemple d'exécution pour un profil spécifique
    profil = "j4WSNb5TuQVwVwSpq65N7o06GC52"
    convert_source_pdf_to_txt(profil)
