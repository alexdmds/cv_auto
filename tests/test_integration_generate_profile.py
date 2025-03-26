#!/usr/bin/env python3
"""Test d'intégration pour le flux complet de génération de profil."""

import pytest
from unittest.mock import patch
from flask import Flask
from backend.models import UserDocument, Profile, HeadProfile
from backend.api.endpoint__generate_profile import generate_profile_endpoint
from backend.utils.utils_gcs import get_concatenated_text_files

# Création d'une application Flask de test
app = Flask(__name__)

@pytest.fixture
def mock_user_document():
    """Fixture pour créer un document utilisateur de test."""
    head = HeadProfile(
        name="",
        title="",
        mail="",
        phone="",
        linkedin_url=""
    )
    profile = Profile(head=head)
    return UserDocument(id="test_user", profile=profile)

@patch('backend.models.UserDocument.from_firestore_id')
@patch('backend.utils.utils_gcs.get_concatenated_text_files')
@patch('backend.models.CallDocument.create_call')
@patch('backend.models.UsageDocument.get_or_create')
def test_generate_profile_integration(
    mock_usage_doc,
    mock_call_doc,
    mock_get_text,
    mock_from_firestore,
    mock_user_document
):
    """Test d'intégration du flux complet de génération de profil."""
    
    # Configuration des mocks
    mock_from_firestore.return_value = mock_user_document
    mock_get_text.return_value = "Test input text"
    mock_usage_doc.return_value.increment_usage = lambda: None
    
    # Utilisation du contexte d'application Flask
    with app.app_context():
        # Appel de l'endpoint
        response, status_code = generate_profile_endpoint("test_user")
        
        # Vérification de la réponse HTTP
        assert status_code == 200
        assert response.json["success"] is True
        assert "execution_time" in response.json
        
        # Vérification des données dans Firestore
        saved_user = UserDocument.from_firestore_id("test_user")
        assert saved_user is not None
        
        # Vérification des données du profil par rapport au mock d'inference
        assert saved_user.profile.head.name == "Jean Dupont"
        assert saved_user.profile.head.title == "Développeur Full Stack Senior avec 8 ans d'expérience"
        assert saved_user.profile.head.mail == "jean.dupont@email.com"
        assert saved_user.profile.head.phone == "06 12 34 56 78"
        
        # Vérification des expériences
        assert len(saved_user.profile.experiences) == 2
        exp = saved_user.profile.experiences[0]
        assert exp.title == "Développeur Full Stack Senior"
        assert exp.company == "TechSolutions SA"
        assert exp.dates == "2020 - Présent"
        assert exp.location == "Paris"
        assert "Développement d'applications web" in exp.full_description
        
        # Vérification des formations
        assert len(saved_user.profile.educations) == 2
        edu = saved_user.profile.educations[0]
        assert edu.title == "Master en Informatique"
        assert edu.university == "Université de Paris"
        assert edu.dates == "2015 - 2017"
        assert "Spécialisation en développement web" in edu.full_description
        
        # Vérification des compétences et langues
        assert "Python" in saved_user.profile.skills
        assert "JavaScript" in saved_user.profile.skills
        assert "Français (natif)" in saved_user.profile.languages
        assert "Anglais (courant)" in saved_user.profile.languages
        
        # Vérification des hobbies
        assert "Randonnée" in saved_user.profile.hobbies
        assert "photographie" in saved_user.profile.hobbies
        
        # Vérification des appels aux services
        mock_call_doc.assert_called_once_with("test_user", "generate_profile")
        mock_usage_doc.assert_called_once_with("test_user") 