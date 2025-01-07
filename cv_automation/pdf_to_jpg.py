from pdf2image import convert_from_path
from PIL import Image, ImageDraw


# Chemin vers le fichier PDF
pdf_path = "data_local/Alexis1/cvs/poste1/cv.pdf"
output_image_path = "data_local/Alexis1/cvs/poste1/cv_image.jpg"

# Paramètre pour la hauteur du trait noir
separator_height = 10

# Conversion du PDF en images par page
images = convert_from_path(pdf_path, dpi=200)  # Ajustez DPI pour la qualité

# Obtenir la largeur maximale et la hauteur totale pour la nouvelle image
width = max(image.width for image in images)
total_height = sum(image.height for image in images) + (separator_height * (len(images) - 1))

# Créer une image vide pour contenir toutes les pages avec les séparateurs
combined_image = Image.new('RGB', (width, total_height), (255, 255, 255))

# Coller chaque page dans la nouvelle image et ajouter un séparateur
current_height = 0
for i, image in enumerate(images):
    # Coller l'image
    combined_image.paste(image, (0, current_height))
    current_height += image.height

    # Ajouter un séparateur noir sauf après la dernière page
    if i < len(images) - 1:
        draw = ImageDraw.Draw(combined_image)
        draw.rectangle([0, current_height, width, current_height + separator_height], fill=(0, 0, 0))
        current_height += separator_height

# Enregistrer l'image combinée avec compression
combined_image = combined_image.resize((width // 6, total_height // 6))
combined_image.save(output_image_path, "JPEG", quality=100, optimize=True)
print(f"Toutes les pages ont été combinées avec des séparateurs en {output_image_path}")