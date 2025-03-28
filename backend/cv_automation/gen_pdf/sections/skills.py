from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle


def create_skills_section(data):
    data = data.get('skills', {})
    # Styles
    section_title_style = ParagraphStyle(
        name="SectionTitle",
        fontSize=16,
        spaceAfter=12,
        textColor="darkblue"
    )

    skills_style = ParagraphStyle(
        name="Skills",
        fontSize=10,
        leading=12,
        spaceAfter=5,
        textColor="black"
    )

    # Récupérer les données pour les compétences
    skills_data = data.get('skills', {})
    section_title = data.get('intitule_section', '')

    # Créer les éléments de la section
    elements = [Paragraph(section_title, section_title_style)]

    #ajouter une ligne avec les langues
    languages = data.get('langues', [])
    if languages:
        formatted_languages = ", ".join([f"{lang['nom']} ({lang['niveau']})" for lang in languages])
        languages_paragraph = f"<b>Langues :</b> {formatted_languages}"
        elements.append(Paragraph(languages_paragraph, skills_style))

    # Regrouper les compétences par catégorie
    compact_skills = []
    for category, skills in skills_data.items():
        compact_skills.append(f"<b>{category}:</b> {', '.join(skills)}")

    # Joindre toutes les compétences en une seule ligne avec un séparateur " | "
    skills_paragraph = " | ".join(compact_skills)
    elements.append(Paragraph(skills_paragraph, skills_style))
    elements.append(Spacer(1, 10))

    return elements