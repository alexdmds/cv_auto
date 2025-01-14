import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent.parent  # Chemin vers 'CV_auto'
sys.path.append(str(ROOT_DIR))

from PyPDF2 import PdfReader
from backend.config import Config
from backend.utils import download_files_from_bucket, upload_to_bucket



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
    Les fichiers sont traités localement ou téléchargés depuis un bucket en mode backend.
    """
    config = Config()
    env = config.ENV

    # Configurer les chemins en fonction de l'environnement
    if env == "local":
        source_profil_path = config.LOCAL_BASE_PATH / profil / "sources"
        output_path = config.LOCAL_BASE_PATH / profil / "sources"
    else:
        source_profil_path = config.TEMP_PATH / profil / "sources"
        output_path = config.TEMP_PATH / profil / "sources"

        # Télécharger les fichiers PDF depuis le bucket
        download_files_from_bucket(config.BUCKET_NAME, f"{profil}/sources/", source_profil_path)

    # Assurez-vous que le répertoire de sortie existe
    output_path.mkdir(parents=True, exist_ok=True)

    # Parcourir les fichiers PDF et extraire leur contenu
    for pdf_file in source_profil_path.glob("*.pdf"):
        txt_file = output_path / pdf_file.with_suffix(".txt").name
        text = extract_text_from_pdf(pdf_file)

        # Sauvegarder le texte extrait
        if env == "local":
            with open(txt_file, "w", encoding="utf-8") as file:
                file.write(text)
            print(f"Texte extrait enregistré localement dans : {txt_file}")
        else:
            # Envoyer le fichier texte dans le bucket
            bucket_destination = f"{profil}/sources/{txt_file.name}"
            upload_to_bucket(config.BUCKET_NAME, bucket_destination, text)
            print(f"Texte extrait enregistré dans le bucket à : {bucket_destination}")


if __name__ == "__main__":
    # Exemple d'exécution pour un profil spécifique
    profil = "j4WSNb5TuQVwVwSpq65N7o06GC52"
    convert_source_pdf_to_txt(profil)