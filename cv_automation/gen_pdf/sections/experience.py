from reportlab.platypus import Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib import colors


def create_experience_section(data):
    data = data['experiences']
    # Styles
    section_title_style = ParagraphStyle(
        name="SectionTitle",
        fontSize=16,
        spaceAfter=12,
        textColor="darkblue"
    )

    job_title_style = ParagraphStyle(
        name="JobTitle",
        fontSize=12,
        fontName="Helvetica-Bold",
        textColor="black"
    )

    company_style = ParagraphStyle(
        name="Company",
        fontSize=10,
        fontName="Helvetica-Oblique",
        textColor="gray",
        spaceAfter=6
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

    # Titre de la section
    elements = [Paragraph(data['intitule_section'], section_title_style)]

    for exp in data['experiences']:
        # Table avec Titre du poste et Dates alignées à droite
        table_data = [
            [
                Paragraph(f"{exp['post']}", job_title_style),
                Paragraph(exp['dates'], date_style)
            ]
        ]
        table = Table(table_data, colWidths=[300, 200])
        table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(table)

        table_data = [
            [   
                Paragraph(f"{exp['company']} - {exp['location']}", company_style),
                elements.append(Spacer(0, 0))
            ]
        ]
        table = Table(table_data, colWidths=[300, 200])
        table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(table)


        # Liste des réalisations avec des puces
        bullet_items = [ListItem(Paragraph(f"{bullet}", bullet_style)) for bullet in exp['bullets']]
        elements.append(ListFlowable(bullet_items, bulletType='bullet'))


    elements.append(Spacer(1, 6))

    return elements