from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

def create_experience_section(data):
    section_title_style = ParagraphStyle(
        name="SectionTitle",
        fontSize=14,
        leading=18
    )
    normal_style = ParagraphStyle(
        name="Normal",
        fontSize=12
    )
    elements = [Paragraph("Expérience professionnelle", section_title_style)]
    for exp in data['experience']:
        elements.append(Paragraph(f"<b>{exp['post']}</b> - {exp['company']} ({exp['dates']})", normal_style))
        elements.append(Paragraph(exp['description'], normal_style))
        elements.append(Spacer(1, 12))
    return elements