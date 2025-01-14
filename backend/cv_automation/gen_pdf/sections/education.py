from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT


def create_education_section(data):
    # Récupérer la section éducation et son titre
    education_data = data["education"]
    educations = education_data["educations"]
    section_title = education_data["intitule_section"]

    # Styles
    section_title_style = ParagraphStyle(
        name="SectionTitle",
        fontSize=16,
        spaceAfter=12,
        textColor="darkblue"
    )

    education_style = ParagraphStyle(
        name="Education",
        fontSize=12,
        fontName="Helvetica-Bold",
        textColor="black",
        spaceAfter=4
    )

    description_style = ParagraphStyle(
        name="Description",
        fontSize=10,
        fontName="Helvetica",
        textColor="black",
        leading=12
    )

    date_style = ParagraphStyle(
        name="Date",
        fontSize=10,
        alignment=TA_RIGHT,
        fontName="Helvetica-Oblique",
        textColor="black"
    )

    # Ajouter le titre de la section
    elements = [Paragraph(section_title, section_title_style)]

    for education in educations:
        # Récupérer les données
        institution_name = education.get('etablissement', 'Établissement inconnu')
        degree_title = education.get('intitule', 'Diplôme inconnu')
        dates = education.get('dates', '')

        # Construire le texte principal : "École - Diplôme"
        education_text = f"<b>{institution_name}</b> – {degree_title}"

        # Table contenant école - diplôme et dates
        table_data = [
            [
                Paragraph(education_text, education_style),  # École et diplôme
                Paragraph(dates, date_style)                 # Dates
            ]
        ]

        # Créer une table pour aligner les colonnes
        table = Table(table_data, colWidths=[400, 100])  # Largeur ajustée pour éviter les retours à la ligne
        table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(table)

        # Ajouter la description (s'il y en a)
        if 'description' in education and education['description']:
            description_paragraph = Paragraph(education['description'], description_style)
            elements.append(description_paragraph)

        # Ajouter un espacement entre les entrées
        elements.append(Spacer(1, 12))

    return elements