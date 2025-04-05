#!/usr/bin/env python3
"""Tests unitaires pour les méthodes de manipulation des CVs dans UserDocument"""

import pytest
from backend.models import (
    UserDocument, CV, CVData, SectionsName,
    ExperienceCV, EducationCV, SkillCV, LanguageCV
)

@pytest.fixture
def mock_result_state():
    """Fixture pour créer un état global simulé"""
    class MockResultState:
        def __init__(self):
            self.head = type('MockHead', (), {
                'name': 'John Doe',
                'title_refined': 'Développeur Senior',
                'mail': 'john.doe@example.com',
                'tel_refined': '+33 6 12 34 56 78'
            })
            self.sections = {
                'experience': 'Expérience Pro',
                'education': 'Formation',
                'skills': 'Compétences',
                'languages': 'Langues',
                'hobbies': 'Loisirs'
            }
            self.experiences = [
                type('MockExperience', (), {
                    'title_refined': 'Dev Senior',
                    'company_refined': 'Tech Corp',
                    'dates_refined': '2020-2023',
                    'location_refined': 'Paris',
                    'bullets': ['Développement Python', 'Lead technique']
                })
            ]
            self.education = [
                type('MockEducation', (), {
                    'degree_refined': 'Master Info',
                    'institution_refined': 'Université Paris',
                    'dates_refined': '2018-2020',
                    'location_refined': 'Paris',
                    'description_refined': 'Spécialisation IA'
                })
            ]
            self.competences = {
                'Programmation': ['Python', 'JavaScript'],
                'DevOps': ['Docker', 'Kubernetes']
            }
            self.langues = [
                type('MockLanguage', (), {
                    'language': 'Français',
                    'level': 'C2'
                })
            ]
            self.hobbies_refined = 'Sport, Lecture'
            self.job_refined = 'Description du poste raffinée'
    return MockResultState()

def test_update_section_names():
    """Test de la mise à jour des noms de sections"""
    sections_name = SectionsName()
    new_sections = {
        'experience': 'Expérience Pro',
        'education': 'Formation',
        'skills': 'Compétences',
        'languages': 'Langues',
        'hobbies': 'Loisirs'
    }
    
    UserDocument._update_section_names(sections_name, new_sections)
    
    assert sections_name.experience_section_name == 'Expérience Pro'
    assert sections_name.education_section_name == 'Formation'
    assert sections_name.skills_section_name == 'Compétences'
    assert sections_name.languages_section_name == 'Langues'
    assert sections_name.hobbies_section_name == 'Loisirs'

def test_create_experiences():
    """Test de la création des expériences"""
    mock_exp = type('MockExperience', (), {
        'title_refined': 'Dev Senior',
        'company_refined': 'Tech Corp',
        'dates_refined': '2020-2023',
        'location_refined': 'Paris',
        'bullets': ['Développement Python', 'Lead technique']
    })
    
    experiences = UserDocument._create_experiences([mock_exp])
    
    assert len(experiences) == 1
    assert experiences[0].title == 'Dev Senior'
    assert experiences[0].company == 'Tech Corp'
    assert experiences[0].dates == '2020-2023'
    assert experiences[0].location == 'Paris'
    assert experiences[0].bullets == ['Développement Python', 'Lead technique']

def test_create_educations():
    """Test de la création des formations"""
    mock_edu = type('MockEducation', (), {
        'degree_refined': 'Master Info',
        'institution_refined': 'Université Paris',
        'dates_refined': '2018-2020',
        'location_refined': 'Paris',
        'description_refined': 'Spécialisation IA'
    })
    
    educations = UserDocument._create_educations([mock_edu])
    
    assert len(educations) == 1
    assert educations[0].title == 'Master Info'
    assert educations[0].university == 'Université Paris'
    assert educations[0].dates == '2018-2020'
    assert educations[0].location == 'Paris'
    assert educations[0].description == 'Spécialisation IA'

def test_create_skills():
    """Test de la création des compétences"""
    competences = {
        'Programmation': ['Python', 'JavaScript'],
        'DevOps': ['Docker', 'Kubernetes']
    }
    
    skills = UserDocument._create_skills(competences)
    
    assert len(skills) == 2
    prog_skill = next(s for s in skills if s.category_name == 'Programmation')
    devops_skill = next(s for s in skills if s.category_name == 'DevOps')
    
    assert prog_skill.skills == 'Python, JavaScript'
    assert devops_skill.skills == 'Docker, Kubernetes'

def test_create_languages():
    """Test de la création des langues"""
    mock_lang = type('MockLanguage', (), {
        'language': 'Français',
        'level': 'C2'
    })
    
    languages = UserDocument._create_languages([mock_lang])
    
    assert len(languages) == 1
    assert languages[0].language == 'Français'
    assert languages[0].level == 'C2'

def test_create_update_info():
    """Test de la création des informations de mise à jour"""
    cv = CV(
        cv_name="Test CV",
        job_raw="Description du poste",
        cv_data=CVData(
            name="John Doe",
            title="Développeur",
            experiences=[ExperienceCV()],
            educations=[EducationCV()],
            skills=[SkillCV()],
            languages=[LanguageCV()],
            hobbies="Sport"
        )
    )
    
    info = UserDocument._create_update_info(cv)
    
    assert info["cv_name"] == "Test CV"
    assert info["updated"] is True
    assert info["name"] == "John Doe"
    assert info["title"] == "Développeur"
    assert info["experiences"] == 1
    assert info["educations"] == 1
    assert info["skills"] == 1
    assert info["languages"] == 1
    assert info["hobbies_updated"] is True
    assert info["job_updated"] is True

def test_update_cv_data(mock_result_state):
    """Test de la mise à jour complète des données d'un CV"""
    cv = CV(
        cv_name="Test CV",
        cv_data=CVData()
    )
    
    user_doc = UserDocument()
    user_doc._update_cv_data(cv, mock_result_state)
    
    # Vérifier les informations de base
    assert cv.cv_data.name == "John Doe"
    assert cv.cv_data.title == "Développeur Senior"
    assert cv.cv_data.mail == "john.doe@example.com"
    assert cv.cv_data.phone == "+33 6 12 34 56 78"
    
    # Vérifier les noms des sections
    assert cv.cv_data.sections_name.experience_section_name == "Expérience Pro"
    
    # Vérifier les expériences
    assert len(cv.cv_data.experiences) == 1
    assert cv.cv_data.experiences[0].title == "Dev Senior"
    
    # Vérifier les formations
    assert len(cv.cv_data.educations) == 1
    assert cv.cv_data.educations[0].title == "Master Info"
    
    # Vérifier les compétences
    assert len(cv.cv_data.skills) == 2
    
    # Vérifier les langues
    assert len(cv.cv_data.languages) == 1
    assert cv.cv_data.languages[0].language == "Français"
    
    # Vérifier les autres champs
    assert cv.cv_data.hobbies == "Sport, Lecture"
    assert cv.job_raw == "Description du poste raffinée"

if __name__ == "__main__":
    pytest.main([__file__]) 