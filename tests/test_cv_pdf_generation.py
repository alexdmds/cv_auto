from backend.models import CVData, SectionsName, ExperienceCV, EducationCV, SkillCV, LanguageCV
from pathlib import Path
import os

def test_cv_pdf_generation():
    """Test la génération de PDF à partir d'un CV"""
    
    # Créer un CV de test
    cv_data = CVData(
        name="Jean Dupont",
        title="Développeur Full Stack",
        mail="jean.dupont@example.com",
        phone="+33 6 12 34 56 78",
        lang_of_cv="fr",
        sections_name=SectionsName(
            experience_section_name="Expérience Professionnelle",
            education_section_name="Formation",
            skills_section_name="Compétences",
            languages_section_name="Langues",
            hobbies_section_name="Centres d'intérêt"
        ),
        experiences=[
            ExperienceCV(
                title="Développeur Senior",
                company="Tech Corp",
                dates="2020 - 2023",
                location="Paris",
                bullets=[
                    "Développement d'applications web en React et Node.js",
                    "Lead d'une équipe de 5 développeurs",
                    "Mise en place de CI/CD avec GitHub Actions"
                ]
            )
        ],
        educations=[
            EducationCV(
                title="Master en Informatique",
                university="Université de Paris",
                dates="2018 - 2020",
                location="Paris",
                description="Spécialisation en Intelligence Artificielle"
            )
        ],
        skills=[
            SkillCV(
                category_name="Langages de programmation",
                skills="Python, JavaScript, TypeScript"
            ),
            SkillCV(
                category_name="Frameworks",
                skills="React, Node.js, Django"
            )
        ],
        languages=[
            LanguageCV(
                language="Français",
                level="Natif"
            ),
            LanguageCV(
                language="Anglais",
                level="Courant"
            )
        ],
        hobbies="Photographie, Randonnée, Lecture"
    )

    # Créer le dossier output s'il n'existe pas
    output_dir = Path(__file__).resolve().parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Définir le chemin de sortie du PDF
    output_path = output_dir / "cv_test.pdf"
    
    # Générer le PDF
    generated_path = cv_data.generate_pdf(str(output_path))
    
    # Vérifier que le fichier a été créé
    assert os.path.exists(generated_path)
    assert os.path.getsize(generated_path) > 0
    
    print(f"PDF généré avec succès : {generated_path}")

if __name__ == "__main__":
    test_cv_pdf_generation()
    print("Test de génération de PDF réussi !") 