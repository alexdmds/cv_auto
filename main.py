from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepInFrame, Image, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors

def generate_cv(output_file, data):
    # Initialiser le document
    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="Title",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        alignment=0
    )
    section_title_style = ParagraphStyle(
        name="SectionTitle",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        spaceBefore=12
    )
    normal_style = styles["Normal"]
    
    # Contenu
    elements = []
    
    # En-tête
    r_im = 12
    # Définir l'image
    image = Image("photo_CV.jpg", width=int(1091/r_im), height=int(1403/r_im))

    # Définir les paragraphes pour le nom et le contact
    name_paragraph = Paragraph(f"<b>{data['name']}</b>", title_style)
    contact_paragraph = Paragraph(data['contact'], normal_style)

    # Créer une table avec deux colonnes : texte à gauche, image à droite
    data_table = [
        [name_paragraph, image],
        [contact_paragraph, ""],  # Contact sur la ligne suivante
    ]

    # Définir la largeur des colonnes pour contrôler l'espace alloué
    col_widths = [400, int(1091/r_im)]  # Largeur pour le texte et l'image
    table = Table(data_table, colWidths=col_widths)

    # Ajouter des styles à la table pour le padding, alignement, etc.
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Aligner en haut
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Aligner l'image à droite
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # Pas de padding à gauche du texte
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Pas de padding vertical
    ]))

    # Ajouter la table aux éléments
    elements.append(table)
    elements.append(Spacer(1, 20))  # Ajouter un espacement après l'en-tête
        
    # Section Expérience professionnelle
    elements.append(Paragraph("Expérience professionnelle", section_title_style))
    for exp in data['experience']:
        elements.append(Paragraph(f"<b>{exp['post']}</b> - {exp['company']} ({exp['dates']})", normal_style))
        elements.append(Paragraph(exp['description'], normal_style))
        elements.append(Spacer(1, 12))
    
    # Section Éducation
    elements.append(Paragraph("Éducation", section_title_style))
    for edu in data['education']:
        elements.append(Paragraph(f"<b>{edu['degree']}</b> - {edu['school']} ({edu['dates']})", normal_style))
        elements.append(Paragraph(edu['description'], normal_style))
        elements.append(Spacer(1, 12))
    
    # Section Autres
    elements.append(Paragraph("Langues et Compétences", section_title_style))
    elements.append(Paragraph(f"Langues : {', '.join(data['languages'])}", normal_style))
    elements.append(Paragraph(f"Compétences : {', '.join(data['skills'])}", normal_style))
    elements.append(Spacer(1, 12))
    
    # Générer le PDF
    doc.build(elements)
    print(f"CV généré : {output_file}")

# Données d'exemple
cv_data = {
    "name": "Alexis de Monts",
    "contact": "Paris, France | +33 6 12 34 56 78 | alexis.demonts@email.com",
    "experience": [
        {
            "post": "Data Engineer",
            "company": "Renault",
            "dates": "2023-Présent",
            "description": "Restructuration de pipelines de données et amélioration de la qualité des données sur GCP."
        },
        {
            "post": "Data Scientist",
            "company": "TotSA",
            "dates": "2020-2023",
            "description": "Mise en place de modèles de machine learning pour optimiser les flux énergétiques."
        }
    ],
    "education": [
        {
            "degree": "Diplôme d'ingénieur",
            "school": "École des Ponts ParisTech",
            "dates": "2017-2020",
            "description": "Spécialisation en optimisation et modélisation mathématique."
        },
        {
            "degree": "Master 2",
            "school": "Politecnico di Milano",
            "dates": "2019-2020",
            "description": "Focus sur Energy Finance, Machine Learning et Computational Finance."
        }
    ],
    "languages": ["Français (natif)", "Anglais (courant)"],
    "skills": ["Python", "BigQuery", "GCP", "Machine Learning", "Airflow", "SQL"]
}

# Générer le CV
generate_cv("CV_Alexis_de_Monts.pdf", cv_data)