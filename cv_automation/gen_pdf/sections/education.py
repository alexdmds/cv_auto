from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT


def create_education_section(data):
    # Récupérer la section éducation et son titre
    education_data = data.get('education', {})
    educations = education_data.get('eductations', [])
    section_title = education_data.get('intitule_section', 'Education')

    # Styles
    section_title_style = ParagraphStyle(
        name="SectionTitle",
        fontSize=16,
        spaceAfter=12,
        textColor="darkblue"
    )

    degree_style = ParagraphStyle(
        name="Degree",
        fontSize=12,
        fontName="Helvetica-Bold",
        textColor="black"
    )

    school_style = ParagraphStyle(
        name="School",
        fontSize=10,
        fontName="Helvetica-Oblique",
        textColor="gray"
    )

    date_style = ParagraphStyle(
        name="Date",
        fontSize=10,
        alignment=TA_RIGHT,
        fontName="Helvetica-Oblique",
        textColor="black"
    )

    bullet_style = ParagraphStyle(
        name="Bullet",
        fontSize=10,
        leftIndent=15,
        spaceAfter=2
    )

    # Ajouter le titre de la section
    elements = [Paragraph(section_title, section_title_style)]

    for education in educations:
        # Titre du diplôme et dates
        table_data = [
            [
                Paragraph(education.get('intitule', 'Diplôme inconnu'), degree_style),
                Paragraph(education.get('dates', ''), date_style)
            ]
        ]

        # Créer une table pour aligner les colonnes
        table = Table(table_data, colWidths=[400, 100])
        table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(table)

        # Description du diplôme (puces)
        if 'description' in education and education['description']:
            bullets = [Paragraph(f"• {education['description']}", bullet_style)]
            elements.extend(bullets)

        # Ajouter un espacement entre les diplômes
        elements.append(Spacer(1, 10))

    return elements