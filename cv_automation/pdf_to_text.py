from PyPDF2 import PdfReader
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def convert_source_pdf_to_txt(profil):

    source_profil_path = Path(f"data_local/{profil}/sources")

    for pdf_file in source_profil_path.glob("*.pdf"):
        txt_file = pdf_file.with_suffix(".txt")
        text = extract_text_from_pdf(pdf_file)
        with open(txt_file, "w", encoding="utf-8") as file:
            file.write(text)
        print(f"Texte extrait enregistré dans : {txt_file}")

if __name__ == "__main__":

    profil = "Alix1"
    convert_source_pdf_to_txt(profil)