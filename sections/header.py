from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors


def create_header(data):
    # **1️⃣ Définir les styles de texte**
    title_style = ParagraphStyle(
        name="Title",
        fontSize=18,
        leading=22,
        alignment=0
    )

    subtitle_style = ParagraphStyle(
        name="Subtitle",
        fontSize=12,
        leading=14,
        alignment=0,
        textColor=colors.grey
    )

    normal_style = ParagraphStyle(
        name="Normal",
        fontSize=12,
        leading=14,
        alignment=0
    )

    # **2️⃣ Charger et redimensionner l'image**
    image_path = "photo_CV.jpg"  # Chemin de l'image
    image_width = 100  # Largeur souhaitée
    image_height = 100  # Hauteur souhaitée
    image = Image(image_path)
    
    # Redimensionner l'image tout en respectant son ratio
    aspect_ratio = image.imageWidth / image.imageHeight  # Calculer le ratio de l'image
    if image_width / image_height > aspect_ratio:  # Trop large, on ajuste la largeur
        image_width = image_height * aspect_ratio
    else:  # Trop haut, on ajuste la hauteur
        image_height = image_width / aspect_ratio
    
    image._restrictSize(image_width, image_height)  # Appliquer la taille à l'image

    # **3️⃣ Créer les paragraphes**
    name_paragraph = Paragraph(f"<b>{data['name']}</b>", title_style)
    title_paragraph = Paragraph(f"<i>{data['title']}</i>", subtitle_style)
    phone_paragraph = Paragraph(f"{data['phone']}", normal_style)
    email_paragraph = Paragraph(f"<a href='mailto:{data['email']}'>{data['email']}</a>", normal_style)
    
    # **4️⃣ Disposition du texte à côté de l'image**
    text_content = [name_paragraph, title_paragraph, phone_paragraph, email_paragraph]
    text_table = [[para] for para in text_content]  # Empiler le texte verticalement
    text_table = Table(text_table, colWidths=[300])  # Largeur de la colonne de texte

    # **5️⃣ Positionner le texte et l'image côte à côte**
    header_table = Table(
        [[text_table, image]],  # Texte à gauche, image à droite
        colWidths=[400, image_width + 10]  # Largeur de la colonne de texte et de l'image
    )

    # **6️⃣ Appliquer le style à la table principale**
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Aligner le contenu en haut
        ('LEFTPADDING', (1, 0), (1, 0), 10),  # Un petit espace entre le texte et l'image
        ('RIGHTPADDING', (1, 0), (1, 0), 0),  # Pas de padding à droite de l'image
        ('LEFTPADDING', (0, 0), (0, 0), 0),  # Pas de padding à gauche du texte
        ('TOPPADDING', (0, 0), (-1, -1), 0),  # Pas d'espacement en haut
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Pas d'espacement en bas
    ]))
    
    return [header_table, Spacer(1, 20)]