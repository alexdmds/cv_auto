from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

def create_hobbies_section(data):
    data = data['hobbies']
    # Styles
    section_title_style = ParagraphStyle(
        name="SectionTitle",
        fontSize=14,
        textColor="darkblue",
        spaceAfter=8,
        leading=18
    )

    hobbies_style = ParagraphStyle(
        name="Hobbies",
        fontSize=10,
        leading=12,
        spaceAfter=2
    )

    # Section title
    elements = [Paragraph(data['intitule_section'], section_title_style)]


    elements.append(Paragraph(data['hobbies'], hobbies_style))


    elements.append(Spacer(1, 12))
    return elements