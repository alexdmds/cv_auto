from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

def create_skills_section(data):
    section_title_style = ParagraphStyle(
        name="SectionTitle",
        fontSize=14,
        leading=18
    )
    normal_style = ParagraphStyle(
        name="Normal",
        fontSize=12
    )
    elements = [Paragraph("Langues et Compétences", section_title_style)]
    elements.append(Paragraph(f"Langues : {', '.join(data['languages'])}", normal_style))
    elements.append(Paragraph(f"Compétences : {', '.join(data['skills'])}", normal_style))
    elements.append(Spacer(1, 12))
    return elements