from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

def create_skills_section(data):
    # Styles
    section_title_style = ParagraphStyle(
        name="SectionTitle",
        fontSize=16,
        spaceAfter=8,
        textColor="darkblue"
    )

    skills_style = ParagraphStyle(
        name="Skills",
        fontSize=10,
        leading=12,
        spaceAfter=5,
        textColor="black"
    )

    elements = [Paragraph(data['standard_names']['languages_skills'], section_title_style)]

    # Langues en une seule ligne
    languages = f"<b>Langues :</b> {', '.join(data['languages'])}"
    elements.append(Paragraph(languages, skills_style))

    # Compétences regroupées de manière concise
    compact_skills = []
    for category, skills in data['skills'].items():
        compact_skills.append(f"<b>{category} :</b> {', '.join(skills)}")

    skills_paragraph = " | ".join(compact_skills)  # Séparateur pour compresser
    elements.append(Paragraph(skills_paragraph, skills_style))
    elements.append(Spacer(1, 10))

    return elements