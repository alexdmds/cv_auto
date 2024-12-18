from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib import colors

def create_education_section(data):
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

    elements = [Paragraph(data['standard_names']['education'], section_title_style)]

    for edu in data['education']:
        table_data = [
            [
                Paragraph(f"{edu['degree']}", degree_style),
                Paragraph(edu['dates'], date_style)
            ]
        ]

        table = Table(table_data, colWidths=[400, 100])
        table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(table)
        elements.append(Paragraph(f"{edu['school']}", school_style))

        if 'description' in edu and edu['description']:
            bullets = [Paragraph(f"• {item}", bullet_style) for item in edu['description']]
            elements.extend(bullets)

        elements.append(Spacer(1, 10))

    return elements