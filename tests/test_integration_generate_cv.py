#!/usr/bin/env python3
"""Test d'intégration pour le flux complet de génération de CV."""

import pytest
from flask import Flask
from backend.models import (
    UserDocument, Profile, HeadProfile, CV, CVData, 
    SectionsName, ExperienceCV, EducationCV, SkillCV, LanguageCV
)

# Création d'une application Flask de test
app = Flask(__name__)

def test_generate_cv_integration():
    """Test d'intégration du flux complet de génération de CV."""
    
    # Créer un utilisateur de test avec un profil et un CV
    head = HeadProfile(
        name="Jean Dupont",
        title="Développeur Full Stack",
        mail="jean.dupont@email.com",
        phone="06 12 34 56 78",
        linkedin_url="https://linkedin.com/in/jean-dupont"  # Ajout du linkedin_url requis
    )
    
    # Création du profil avec tous les champs requis
    profile = Profile(
        head=head,
        experiences=[{
            "title": "Développeur Full Stack",
            "company": "TechCorp",
            "dates": "2020-2023",
            "location": "Paris",
            "full_descriptions": "Développement d'applications web modernes"
        }],
        educations=[{
            "title": "Master en Informatique",
            "university": "Université de Paris",
            "dates": "2018-2020",
            "full_descriptions": "Spécialisation en développement web"
        }],
        languages="Français (natif), Anglais (C1)",
        skills="Python, JavaScript, React, Node.js",
        hobbies="Randonnée, photographie, lecture"
    )
    
    # Création des données du CV avec la structure complète
    sections_name = SectionsName(
        experience_section_name="Expérience Professionnelle",
        education_section_name="Formation",
        skills_section_name="Compétences",
        languages_section_name="Langues",
        hobbies_section_name="Centres d'intérêt"  # Correction du nom du champ
    )
    
    cv_data = CVData(
        name="Jean Dupont",
        title="Développeur Full Stack",
        mail="jean.dupont@email.com",
        phone="06 12 34 56 78",
        lang_of_cv="FR",
        sections_name=sections_name,
        experiences=[
            ExperienceCV(
                title="Développeur Full Stack",
                company="TechCorp",
                dates="2020-2023",
                location="Paris",
                bullets=["Développement d'applications web", "Gestion d'équipe", "Architecture logicielle"]
            )
        ],
        educations=[
            EducationCV(
                title="Master en Informatique",
                university="Université de Paris",
                dates="2018-2020",
                location="Paris",
                description="Spécialisation en développement web"
            )
        ],
        skills=[
            SkillCV(
                category_name="Développement",
                skills="Python, JavaScript, React, Node.js"
            )
        ],
        languages=[
            LanguageCV(
                language="Français",
                level="Natif"
            ),
            LanguageCV(
                language="Anglais",
                level="C1"
            )
        ],
        hobbies="Randonnée, photographie, lecture"
    )
    
    cv = CV(
        cv_name="test_cv",
        job_raw="Développeur Full Stack Senior recherché pour projet innovant",
        cv_data=cv_data
    )
    
    user_doc = UserDocument(id="test_user", profile=profile, cvs=[cv])
    
    # Sauvegarder l'utilisateur dans Firestore
    user_doc.save()

    # Utilisation du contexte d'application Flask
    with app.app_context():
        # Appel de l'endpoint
        from backend.api.endpoint_generate_cv import generate_cv_endpoint
        response, status_code = generate_cv_endpoint("test_user", "test_cv")
        
        # Vérification de la réponse HTTP
        assert status_code == 200
        assert "success" in response.json
        assert response.json["success"] is True
        
        # Vérification des données de réponse
        data = response.json["data"]
        assert data["user_id"] == "test_user"
        assert data["cv_name"] == "test_cv"
        assert "timestamp" in data
        assert "pdf_url" in data
        
        # Vérification des données dans Firestore
        saved_user = UserDocument.from_firestore_id("test_user")
        assert saved_user is not None
        
        # Trouver le CV mis à jour
        cv = next((cv for cv in saved_user.cvs if cv.cv_name == "test_cv"), None)
        assert cv is not None
        
        # Afficher le contenu du CV pour le debug
        print("\nContenu du CV après génération:")
        print(f"Title: {cv.cv_data.title}")
        print(f"Experiences: {cv.cv_data.experiences}")
        print(f"Educations: {cv.cv_data.educations}")
        print(f"Skills: {cv.cv_data.skills}")
        print(f"Languages: {cv.cv_data.languages}")
        print(f"Hobbies: {cv.cv_data.hobbies}")
    