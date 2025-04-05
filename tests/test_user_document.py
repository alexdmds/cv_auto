#!/usr/bin/env python3
"""
Script de test pour les constructeurs de la classe UserDocument.
"""

import sys
import os
from typing import Optional
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Ajout du répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import (
    UserDocument, Profile, HeadProfile, ExperienceProfile, 
    EducationProfile, CV, CVData, ExperienceCV, EducationCV,
    SkillCV, LanguageCV, SectionsName
)
from ai_module.lg_models import ProfileState, GeneralInfo, GlobalExperience, GlobalEducation

@pytest.fixture
def mock_profile_state():
    """Fixture pour créer un état de profil de test"""
    head = GeneralInfo(
        name="John Doe",
        general_title="Développeur Senior",
        email="john@example.com",
        phone="+33123456789",
        skills="Python, JavaScript",
        langues="Anglais (C2), Français (Natif)",
        hobbies="Sport, Lecture"
    )
    
    experiences = [
        GlobalExperience(
            intitule="Lead Developer",
            etablissement="Tech Corp",
            dates="2020-2023",
            lieu="Paris",
            description="Lead d'une équipe de développeurs"
        )
    ]
    
    education = [
        GlobalEducation(
            intitule="Master Informatique",
            etablissement="Université Paris",
            dates="2018-2020",
            description="Spécialisation en IA"
        )
    ]
    
    return ProfileState(
        head=head,
        experiences=experiences,
        education=education,
        input_text=""
    )

@pytest.fixture
def mock_cv_state():
    """Fixture pour créer un état de CV de test"""
    head = Mock()
    head.name = "John Doe"
    head.title_refined = "Senior Developer"
    head.mail = "john@example.com"
    head.tel_refined = "+33123456789"
    
    mock_state = Mock()
    mock_state.head = head
    mock_state.sections = {
        "experience": "Professional Experience",
        "education": "Education",
        "skills": "Skills",
        "languages": "Languages",
        "hobbies": "Interests"
    }
    mock_state.experiences = [Mock(
        title_refined="Lead Developer",
        company_refined="Tech Corp",
        dates_refined="2020-2023",
        location_refined="Paris",
        bullets=["Leadership", "Development"]
    )]
    mock_state.education = [Mock(
        degree_refined="Master in CS",
        institution_refined="Paris University",
        dates_refined="2018-2020",
        location_refined="Paris",
        description_refined="AI Specialization"
    )]
    mock_state.competences = {
        "Programming": ["Python", "JavaScript"],
        "Tools": ["Git", "Docker"]
    }
    mock_state.langues = [Mock(
        language="English",
        level="C2"
    )]
    mock_state.hobbies_refined = "Sports, Reading"
    mock_state.job_refined = "Senior Developer Position"
    
    return mock_state

def create_mock_profile_state() -> ProfileState:
    """Crée un ProfileState de test"""
    return ProfileState(
        head=GeneralInfo(
            name="John Doe",
            phone="+33 6 12 34 56 78",
            email="john.doe@example.com",
            general_title="Développeur Full Stack",
            skills="Python, JavaScript, React",
            langues="Français (C2), Anglais (B2)",
            hobbies="Programmation, Lecture, Sport"
        ),
        experiences=[
            GlobalExperience(
                intitule="Master en Informatique",
                dates="2018-2020",
                etablissement="Université Paris-Saclay",
                lieu="Paris",
                description="Spécialisation en développement web"
            )
        ],
        education=[
            GlobalEducation(
                intitule="Master en Informatique",
                dates="2018-2020",
                etablissement="Université Paris-Saclay",
                lieu="Paris",
                description="Spécialisation en développement web"
            )
        ],
        input_text=""
    )

def test_from_firestore_id():
    """Test de la création d'un UserDocument depuis Firestore"""
    with patch('backend.models.UserDocument.get_db') as mock_get_db:
        # Configuration du mock
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "profile": {
                "head": {
                    "name": "John Doe",
                    "title": "Developer",
                    "mail": "john@example.com"
                },
                "experiences": [],
                "educations": []
            },
            "cvs": []
        }
        
        mock_doc_ref = Mock()
        mock_doc_ref.get.return_value = mock_doc
        
        mock_db = Mock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        mock_get_db.return_value = mock_db
        
        # Test
        user_doc = UserDocument.from_firestore_id("test_user")
        
        assert user_doc is not None
        assert user_doc.id == "test_user"
        assert user_doc.profile.head.name == "John Doe"

def test_from_profile_state(mock_profile_state):
    """Test de la création d'un UserDocument depuis un ProfileState"""
    user_doc = UserDocument.from_profile_state(mock_profile_state, "test_user")
    
    assert user_doc.id == "test_user"
    assert user_doc.profile.head.name == "John Doe"
    assert user_doc.profile.head.title == "Développeur Senior"
    assert user_doc.profile.head.mail == "john@example.com"
    assert user_doc.profile.head.phone == "+33123456789"
    
    assert len(user_doc.profile.experiences) == 1
    exp = user_doc.profile.experiences[0]
    assert exp.title == "Lead Developer"
    assert exp.company == "Tech Corp"
    
    assert len(user_doc.profile.educations) == 1
    edu = user_doc.profile.educations[0]
    assert edu.title == "Master Informatique"
    assert edu.university == "Université Paris"
    
    assert user_doc.profile.skills == "Python, JavaScript"
    assert user_doc.profile.languages == "Anglais (C2), Français (Natif)"
    assert user_doc.profile.hobbies == "Sport, Lecture"

def test_cv_update_from_cv_state(mock_cv_state):
    """Test de la mise à jour d'un CV depuis un CVGenState"""
    # Créer un CV vide
    cv = CV(cv_name="test_cv", cv_data=CVData())
    
    # Mettre à jour le CV
    cv.update_from_cv_state(mock_cv_state)
    
    # Vérifier les données de base
    assert cv.cv_data.name == "John Doe"
    assert cv.cv_data.title == "Senior Developer"
    assert cv.cv_data.mail == "john@example.com"
    assert cv.cv_data.phone == "+33123456789"
    
    # Vérifier les noms des sections
    assert cv.cv_data.sections_name.experience_section_name == "Professional Experience"
    assert cv.cv_data.sections_name.education_section_name == "Education"
    assert cv.cv_data.sections_name.skills_section_name == "Skills"
    assert cv.cv_data.sections_name.languages_section_name == "Languages"
    assert cv.cv_data.sections_name.hobbies_section_name == "Interests"
    
    # Vérifier les expériences
    assert len(cv.cv_data.experiences) == 1
    exp = cv.cv_data.experiences[0]
    assert exp.title == "Lead Developer"
    assert exp.company == "Tech Corp"
    assert exp.dates == "2020-2023"
    assert exp.location == "Paris"
    assert exp.bullets == ["Leadership", "Development"]
    
    # Vérifier les formations
    assert len(cv.cv_data.educations) == 1
    edu = cv.cv_data.educations[0]
    assert edu.title == "Master in CS"
    assert edu.university == "Paris University"
    assert edu.dates == "2018-2020"
    assert edu.location == "Paris"
    assert edu.description == "AI Specialization"
    
    # Vérifier les compétences
    assert len(cv.cv_data.skills) == 2
    skills_dict = {skill.category_name: skill.skills for skill in cv.cv_data.skills}
    assert skills_dict["Programming"] == "Python, JavaScript"
    assert skills_dict["Tools"] == "Git, Docker"
    
    # Vérifier les langues
    assert len(cv.cv_data.languages) == 1
    lang = cv.cv_data.languages[0]
    assert lang.language == "English"
    assert lang.level == "C2"
    
    # Vérifier les autres champs
    assert cv.cv_data.hobbies == "Sports, Reading"
    assert cv.job_raw == "Senior Developer Position"

def test_user_document_update_cv_from_cv_state(mock_cv_state):
    """Test de la mise à jour d'un CV dans UserDocument depuis un CVGenState"""
    # Créer un UserDocument avec un CV existant
    cv = CV(cv_name="test_cv", cv_data=CVData())
    user_doc = UserDocument(id="test_user", cvs=[cv])
    
    # Mettre à jour le CV
    with patch('backend.models.UserDocument.save'):
        result = user_doc.update_cv_from_cv_state("test_cv", mock_cv_state, save_to_firestore=True)
    
    assert result is not None
    assert result["cv_name"] == "test_cv"
    assert result["updated"] is True
    
    # Vérifier les données mises à jour
    updated_cv = user_doc.cvs[0]
    assert updated_cv.cv_data.name == "John Doe"
    assert updated_cv.cv_data.title == "Senior Developer"
    assert updated_cv.cv_data.mail == "john@example.com"
    
    assert len(updated_cv.cv_data.experiences) == 1
    exp = updated_cv.cv_data.experiences[0]
    assert exp.title == "Lead Developer"
    assert exp.company == "Tech Corp"
    
    assert len(updated_cv.cv_data.skills) == 2
    assert updated_cv.cv_data.hobbies == "Sports, Reading"
    assert updated_cv.job_raw == "Senior Developer Position"

def test_update_cv_not_found_cv_state():
    """Test de la mise à jour d'un CV inexistant avec CVGenState"""
    user_doc = UserDocument(id="test_user")
    result = user_doc.update_cv_from_cv_state("nonexistent_cv", Mock(), save_to_firestore=False)
    assert result is None

def test_create_update_info():
    """Test de la création des informations de mise à jour"""
    cv = CV(
        cv_name="test_cv",
        job_raw="Job description",
        cv_data=CVData(
            name="John Doe",
            title="Developer",
            experiences=[ExperienceCV()],
            educations=[EducationCV()],
            skills=[SkillCV()],
            languages=[LanguageCV()],
            hobbies="Sports"
        )
    )
    
    info = UserDocument._create_update_info(cv)
    
    assert info["cv_name"] == "test_cv"
    assert info["updated"] is True
    assert info["name"] == "John Doe"
    assert info["title"] == "Developer"
    assert info["experiences"] == 1
    assert info["educations"] == 1
    assert info["skills"] == 1
    assert info["languages"] == 1
    assert info["hobbies_updated"] is True
    assert info["job_updated"] is True

def print_user_document(user: UserDocument):
    """Affiche les informations d'un UserDocument"""
    # Affichage des informations du profil
    if user.profile and user.profile.head:
        head = user.profile.head
        print("\n=== INFORMATIONS DU PROFIL ===")
        if head.name:
            print(f"Nom: {head.name}")
        if head.title:
            print(f"Titre: {head.title}")
        if head.mail:
            print(f"Email: {head.mail}")
        if head.phone:
            print(f"Téléphone: {head.phone}")
    
    # Affichage des expériences
    if user.profile.experiences:
        print(f"\n=== EXPÉRIENCES ({len(user.profile.experiences)}) ===")
        for exp in user.profile.experiences:
            print(f"\nTitre: {exp.title}")
            print(f"Entreprise: {exp.company}")
            print(f"Dates: {exp.dates}")
    
    # Affichage des formations
    if user.profile.educations:
        print(f"\n=== FORMATIONS ({len(user.profile.educations)}) ===")
        for edu in user.profile.educations:
            print(f"\nDiplôme: {edu.title}")
            print(f"École: {edu.university}")
            print(f"Dates: {edu.dates}")
    
    # Affichage des compétences
    if user.profile.skills:
        print("\n=== COMPÉTENCES ===")
        for category, skills in user.profile.skills.items():
            print(f"{category}: {', '.join(skills)}")
    
    # Affichage des langues
    if user.profile.languages:
        print("\n=== LANGUES ===")
        for lang in user.profile.languages:
            print(f"{lang['language']}: {lang['level']}")
    
    # Affichage des CVs
    if user.cvs:
        print(f"\n=== CVs ({len(user.cvs)}) ===")
        for cv in user.cvs:
            print(f"\nNom du CV: {cv.cv_name}")
            if cv.job_raw:
                print(f"Description du poste: {cv.job_raw[:50]}...")

def main():
    """Fonction principale"""
    # Exécuter tous les tests par défaut
    user_id = "test_user"
    print("\n=== Exécution de tous les tests ===")
    firestore_user = test_from_firestore_id()
    profile_user = test_from_profile_state(mock_profile_state)

if __name__ == "__main__":
    main() 