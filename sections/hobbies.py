from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

def create_hobbies_section(data):
    section_title_style = ParagraphStyle(
        name="SectionTitle",
        fontSize=14,
        leading=18
    )
    normal_style = ParagraphStyle(
        name="Normal",
        fontSize=12
    )
    elements = [Paragraph("Centres d'intérêt", section_title_style)]
    elements.append(Paragraph(f"{', '.join(data['hobbies'])}", normal_style))
    elements.append(Spacer(1, 12))
    return elements