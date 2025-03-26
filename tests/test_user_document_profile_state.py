#!/usr/bin/env python3
"""Tests unitaires pour les méthodes de conversion ProfileState de UserDocument"""

import pytest
from backend.models import UserDocument, Profile, HeadProfile
from ai_module.lg_models import ProfileState, GeneralInfo, GlobalExperience, GlobalEducation

@pytest.fixture
def mock_profile_state():
    """Fixture pour créer un ProfileState de test"""
    return ProfileState(
        head=GeneralInfo(
            name="John Doe",
            phone="+33 6 12 34 56 78",
            email="john.doe@example.com",
            general_title="Développeur Full Stack",
            skills="Python, JavaScript, React",
            langues="Français (C2), Anglais (B2)",
            hobbies="Sport, Lecture, Voyages"
        ),
        experiences=[
            GlobalExperience(
                intitule="Développeur Senior",
                dates="2020-2023",
                etablissement="Tech Corp",
                lieu="Paris",
                description="Lead technique sur projets web"
            ),
            GlobalExperience(
                intitule="Développeur Full Stack",
                dates="2018-2020",
                etablissement="Startup Inc",
                lieu="Lyon",
                description="Développement d'applications web"
            )
        ],
        education=[
            GlobalEducation(
                intitule="Master Informatique",
                dates="2016-2018",
                etablissement="Université de Paris",
                lieu="Paris",
                description="Spécialisation en développement web"
            )
        ],
        input_text=""
    )

def test_create_profile_from_state(mock_profile_state):
    """Test de la création d'un profil à partir d'un ProfileState"""
    profile = UserDocument._create_profile_from_state(mock_profile_state)
    
    # Vérifier les informations de base
    assert isinstance(profile, Profile)
    assert isinstance(profile.head, HeadProfile)
    assert profile.head.name == "John Doe"
    assert profile.head.title == "Développeur Full Stack"
    assert profile.head.mail == "john.doe@example.com"
    assert profile.head.phone == "+33 6 12 34 56 78"
    assert profile.head.linkedin_url == ""  # Valeur par défaut
    
    # Vérifier les expériences
    assert len(profile.experiences) == 2
    exp1, exp2 = profile.experiences
    
    assert exp1.title == "Développeur Senior"
    assert exp1.company == "Tech Corp"
    assert exp1.dates == "2020-2023"
    assert exp1.location == "Paris"
    assert exp1.full_descriptions == "Lead technique sur projets web"
    
    assert exp2.title == "Développeur Full Stack"
    assert exp2.company == "Startup Inc"
    assert exp2.dates == "2018-2020"
    assert exp2.location == "Lyon"
    assert exp2.full_descriptions == "Développement d'applications web"
    
    # Vérifier les formations
    assert len(profile.educations) == 1
    edu = profile.educations[0]
    
    assert edu.title == "Master Informatique"
    assert edu.university == "Université de Paris"
    assert edu.dates == "2016-2018"
    assert edu.full_descriptions == "Spécialisation en développement web"
    
    # Vérifier les autres champs
    assert profile.skills == "Python, JavaScript, React"
    assert profile.languages == "Français (C2), Anglais (B2)"
    assert profile.hobbies == "Sport, Lecture, Voyages"

def test_from_profile_state(mock_profile_state):
    """Test de la création d'un UserDocument à partir d'un ProfileState"""
    user_doc = UserDocument.from_profile_state(mock_profile_state, "test_user_id")
    
    # Vérifier l'ID
    assert user_doc.id == "test_user_id"
    
    # Vérifier que le profil a été correctement créé
    assert isinstance(user_doc.profile, Profile)
    assert user_doc.profile.head.name == "John Doe"
    
    # Vérifier que la liste des CVs est vide
    assert len(user_doc.cvs) == 0

def test_from_profile_state_empty():
    """Test de la création d'un UserDocument à partir d'un ProfileState vide"""
    empty_state = ProfileState(
        head=GeneralInfo(),
        experiences=[],
        education=[],
        input_text=""
    )
    
    user_doc = UserDocument.from_profile_state(empty_state, "test_user_id")
    
    # Vérifier que le document a été créé avec des valeurs par défaut
    assert user_doc.id == "test_user_id"
    assert isinstance(user_doc.profile, Profile)
    assert user_doc.profile.head.name is None
    assert len(user_doc.profile.experiences) == 0
    assert len(user_doc.profile.educations) == 0
    assert len(user_doc.cvs) == 0

if __name__ == "__main__":
    pytest.main([__file__]) 