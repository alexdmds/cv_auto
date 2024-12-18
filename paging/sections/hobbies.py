from reportlab.platypus import Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import ParagraphStyle

def create_hobbies_section(data):
    # Styles
    section_title_style = ParagraphStyle(
        name="SectionTitle",
        fontSize=14,
        textColor="darkblue",
        spaceAfter=8,
        leading=18
    )

    bullet_style = ParagraphStyle(
        name="Bullet",
        fontSize=10,
        leading=12,
        leftIndent=15,
        bulletIndent=10,
        spaceAfter=2
    )

    # Section title
    elements = [Paragraph(data['standard_names']['hobbies'], section_title_style)]

    # Ajout des hobbies sous forme de liste à puces
    if data.get('hobbies'):
        bullet_items = [ListItem(Paragraph(hobby, bullet_style)) for hobby in data['hobbies']]
        elements.append(ListFlowable(bullet_items, bulletType='bullet'))
    else:
        elements.append(Paragraph("Aucun centre d'intérêt spécifié.", bullet_style))

    elements.append(Spacer(1, 12))
    return elements