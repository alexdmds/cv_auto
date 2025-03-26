#!/usr/bin/env python3
"""Tests unitaires pour les modèles."""

import pytest
from unittest.mock import patch, MagicMock
from backend.models import UserDocument, Profile, HeadProfile
from ai_module.lg_models import ProfileState, GeneralInfo, GlobalExperience, GlobalEducation

@pytest.fixture
def mock_profile_state():
    """Fixture pour créer un ProfileState de test."""
    head = GeneralInfo(
        name="Jean Dupont",
        general_title="Développeur Full Stack",
        email="jean.dupont@email.com",
        phone="06 12 34 56 78",
        skills="Python, JavaScript",
        langues="Français (natif), Anglais (courant)",
        hobbies="Randonnée, photographie"
    )
    
    experiences = [
        GlobalExperience(
            intitule="Développeur Full Stack Senior",
            etablissement="TechSolutions SA",
            dates="2020 - Présent",
            lieu="Paris",
            description="Développement d'applications web"
        )
    ]
    
    education = [
        GlobalEducation(
            intitule="Master en Informatique",
            etablissement="Université de Paris",
            dates="2015 - 2017",
            description="Spécialisation en développement web"
        )
    ]
    
    return ProfileState(
        head=head,
        experiences=experiences,
        education=education
    )

@pytest.fixture
def existing_user_document():
    """Fixture pour créer un UserDocument existant."""
    head = HeadProfile(
        name="Pierre Martin",
        title="Data Scientist",
        mail="pierre.martin@email.com",
        phone="07 11 22 33 44",
        linkedin_url="linkedin.com/pierre"
    )
    profile = Profile(head=head)
    return UserDocument(id="test_user", profile=profile)

def test_from_profile_state_new_user(mock_profile_state):
    """Test de from_profile_state pour un nouvel utilisateur."""
    with patch('backend.models.UserDocument.from_firestore_id', return_value=None):
        user_doc = UserDocument.from_profile_state(mock_profile_state, "new_user")
        
        # Vérification des données de base
        assert user_doc.id == "new_user"
        assert user_doc.profile.head.name == "Jean Dupont"
        assert user_doc.profile.head.title == "Développeur Full Stack"
        assert user_doc.profile.head.mail == "jean.dupont@email.com"
        assert user_doc.profile.head.phone == "06 12 34 56 78"
        
        # Vérification des expériences
        assert len(user_doc.profile.experiences) == 1
        exp = user_doc.profile.experiences[0]
        assert exp.title == "Développeur Full Stack Senior"
        assert exp.company == "TechSolutions SA"
        assert exp.dates == "2020 - Présent"
        assert exp.location == "Paris"
        assert exp.full_descriptions == "Développement d'applications web"
        
        # Vérification des formations
        assert len(user_doc.profile.educations) == 1
        edu = user_doc.profile.educations[0]
        assert edu.title == "Master en Informatique"
        assert edu.university == "Université de Paris"
        assert edu.dates == "2015 - 2017"
        assert edu.full_descriptions == "Spécialisation en développement web"
        
        # Vérification des autres champs
        assert user_doc.profile.skills == "Python, JavaScript"
        assert user_doc.profile.languages == "Français (natif), Anglais (courant)"
        assert user_doc.profile.hobbies == "Randonnée, photographie"

def test_from_profile_state_existing_user(mock_profile_state, existing_user_document):
    """Test de from_profile_state pour un utilisateur existant."""
    with patch('backend.models.UserDocument.from_firestore_id', return_value=existing_user_document):
        user_doc = UserDocument.from_profile_state(mock_profile_state, "test_user")
        
        # Vérification que l'ID est préservé
        assert user_doc.id == "test_user"
        
        # Vérification que les données sont mises à jour
        assert user_doc.profile.head.name == "Jean Dupont"  # Nouvelle valeur
        assert user_doc.profile.head.title == "Développeur Full Stack"  # Nouvelle valeur
        assert user_doc.profile.head.mail == "jean.dupont@email.com"  # Nouvelle valeur
        assert user_doc.profile.head.phone == "06 12 34 56 78"  # Nouvelle valeur
        assert user_doc.profile.head.linkedin_url == "linkedin.com/pierre"  # Valeur existante préservée
        
        # Vérification des expériences
        assert len(user_doc.profile.experiences) == 1
        exp = user_doc.profile.experiences[0]
        assert exp.title == "Développeur Full Stack Senior"
        
        # Vérification des formations
        assert len(user_doc.profile.educations) == 1
        edu = user_doc.profile.educations[0]
        assert edu.title == "Master en Informatique"
        
        # Vérification des autres champs
        assert user_doc.profile.skills == "Python, JavaScript"
        assert user_doc.profile.languages == "Français (natif), Anglais (courant)"
        assert user_doc.profile.hobbies == "Randonnée, photographie" 