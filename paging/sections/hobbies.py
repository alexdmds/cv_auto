from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

def create_hobbies_section(data, language='fr'):
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
    elements = [Paragraph(data['standard_names']['hobbies'][language], section_title_style)]


    elements.append(Paragraph(data['standard_names']['interest_body'][language], hobbies_style))


    elements.append(Spacer(1, 12))
    return elements