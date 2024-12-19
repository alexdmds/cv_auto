from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib import colors

def create_education_section(data, language='fr'):
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

    elements = [Paragraph(data['standard_names']['education'][language], section_title_style)]

    #Politecnico
    table_data = [
        [
            Paragraph(f"{data['standard_names']['diplome_politecnico'][language]}", degree_style),
            Paragraph("2021 - 2022", date_style)
        ]
    ]

    table = Table(table_data, colWidths=[400, 100])
    table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(table)

    if 'description' in data['education']['politecnico'] and data['education']['politecnico']['description']:
        bullets = [Paragraph(f"• {item}", bullet_style) for item in data['education']['politecnico']['description']]
        elements.extend(bullets)

    elements.append(Spacer(1, 10))

    #Ponts

    table_data = [
        [
            Paragraph(f"{data['standard_names']['diplome_ponts'][language]}", degree_style),
            Paragraph("2017 - 2022", date_style)
        ]
    ]

    table = Table(table_data, colWidths=[400, 100])
    table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(table)

    if 'description' in data['education']['ponts'] and data['education']['ponts']['description']:
        bullets = [Paragraph(f"• {item}", bullet_style) for item in data['education']['ponts']['description']]
        elements.extend(bullets)

    elements.append(Spacer(1, 10))

    #Stan

    table_data = [
        [
            Paragraph(f"{data['standard_names']['diplome_stan'][language]}", degree_style),
            Paragraph("2015 - 2017", date_style)
        ]
    ]

    table = Table(table_data, colWidths=[400, 100])
    table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(table)
    bullets = [Paragraph(f"• {data['standard_names']['stan_body'][language]}", bullet_style)]
    elements.extend(bullets)

    elements.append(Spacer(1, 10))

    return elements