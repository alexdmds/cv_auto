from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

def create_header(data, language='fr'):
    # **1️⃣ Styles**
    name_style = ParagraphStyle(
        name="Name",
        fontSize=20,
        leading=24,
        textColor="darkblue",
        alignment=1  # Centré
    )

    title_style = ParagraphStyle(
        name="Title",
        fontSize=12,
        leading=14,
        textColor=colors.grey,
        alignment=1  # Centré
    )

    contact_style = ParagraphStyle(
        name="Contact",
        fontSize=10,
        leading=12,
        textColor="black",
        alignment=1  # Centré
    )

    # **2️⃣ Image**
    image_path = "photo_CV.jpg"  # Chemin de l'image
    image_width, image_height = 80, 80
    image = Image(image_path)
    aspect_ratio = image.imageWidth / image.imageHeight
    if image_width / image_height > aspect_ratio:
        image_width = image_height * aspect_ratio
    else:
        image_height = image_width / aspect_ratio
    image._restrictSize(image_width, image_height)

    # **3️⃣ Contenu textuel**
    name_paragraph = Paragraph(f"<b>{data['name']}</b>", name_style)
    title_paragraph = Paragraph(f"<i>{data['title']}</i>", title_style)

    contact_paragraph = Paragraph(
        f"{data['phone']} | <a href='mailto:{data['email']}'>{data['email']}</a>", contact_style
    )

    # **4️⃣ Disposition - Texte et Image**
    # Texte principal (nom et titre) centré avec contact en dessous
    text_content = Table([
        [name_paragraph],
        [title_paragraph],
        [Spacer(1, 5)],
        [contact_paragraph]
    ], colWidths=[400])

    text_content.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    # Table principale avec image à droite
    header_table = Table([
        [text_content, image]
    ], colWidths=[400, image_width + 10])

    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (1, 0), (1, 0), 10),
        ('RIGHTPADDING', (0, 0), (0, 0), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    # **5️⃣ Ligne de séparation**
    separator = Table(
        [[Paragraph("", ParagraphStyle(name="Line", backColor=colors.grey, spaceAfter=5))]],
        colWidths=[500], rowHeights=1
    )
    separator.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey)]))

    # Retourner le header complet
    return [header_table, Spacer(1, 10), separator, Spacer(1, 10)]