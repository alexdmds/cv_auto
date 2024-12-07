from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

def create_education_section(data):
    section_title_style = ParagraphStyle(
        name="SectionTitle",
        fontSize=14,
        leading=18
    )
    normal_style = ParagraphStyle(
        name="Normal",
        fontSize=12
    )
    elements = [Paragraph("Éducation", section_title_style)]
    for edu in data['education']:
        elements.append(Paragraph(f"<b>{edu['degree']}</b> - {edu['school']} ({edu['dates']})", normal_style))
        elements.append(Paragraph(edu['description'], normal_style))
        elements.append(Spacer(1, 12))
    return elements