#!/usr/bin/env python3
"""Test d'intégration pour le flux complet de génération de CV."""

import pytest
from unittest.mock import patch
from flask import Flask
from backend.models import UserDocument, CV, CVData
from backend.api.endpoint_generate_cv import generate_cv_endpoint

# Création d'une application Flask de test
app = Flask(__name__)

@pytest.fixture
def mock_user_document():
    """Fixture pour créer un document utilisateur de test."""
    user_doc = UserDocument(id="test_user")
    cv = CV(cv_name="test_cv", cv_data=CVData())
    user_doc.cvs = [cv]
    return user_doc

@patch('backend.models.UserDocument.from_firestore_id')
@patch('backend.api.endpoint_generate_cv.upload_to_firebase_storage')
def test_generate_cv_integration(mock_upload, mock_from_firestore, mock_user_document):
    """Test d'intégration du flux complet de génération de CV."""
    
    # Configuration des mocks
    mock_from_firestore.return_value = mock_user_document
    mock_upload.return_value = "https://storage.example.com/cv.pdf"
    
    # Utilisation du contexte d'application Flask
    with app.app_context():
        # Appel de l'endpoint
        response, status_code = generate_cv_endpoint("test_user", "test_cv")
        
        # Vérification de la réponse HTTP
        assert status_code == 200
        assert response.json["success"] is True
        assert response.json["data"]["user_id"] == "test_user"
        assert response.json["data"]["cv_name"] == "test_cv"
        assert "timestamp" in response.json["data"]
        assert response.json["data"]["pdf_url"] == "https://storage.example.com/cv.pdf"
        
        # Vérification des données dans Firestore
        updated_user = mock_user_document
        assert len(updated_user.cvs) == 1
        updated_cv = updated_user.cvs[0]
        
        # Vérification des données du CV par rapport au mock d'inference
        assert updated_cv.cv_data.name == "Jean Dupont"
        assert updated_cv.cv_data.title == "Développeur Full Stack Senior | Expert Python & JavaScript"
        assert updated_cv.cv_data.mail == "jean.dupont@email.com"
        assert updated_cv.cv_data.phone == "06 12 34 56 78"
        
        # Vérification des sections
        assert updated_cv.cv_data.sections_name.experience_section_name == "Expérience Professionnelle"
        assert updated_cv.cv_data.sections_name.education_section_name == "Formation"
        assert updated_cv.cv_data.sections_name.skills_section_name == "Compétences"
        assert updated_cv.cv_data.sections_name.languages_section_name == "Langues"
        assert updated_cv.cv_data.sections_name.hobbies_section_name == "Centres d'Intérêt"
        
        # Vérification des expériences
        assert len(updated_cv.cv_data.experiences) == 1
        exp = updated_cv.cv_data.experiences[0]
        assert exp.title == "Développeur Full Stack Senior"
        assert exp.company == "TechSolutions SA"
        assert exp.dates == "2020 - Présent"
        assert exp.location == "Paris"
        assert exp.bullets == ["Développement d'applications Web avec technologies modernes"]
        
        # Vérification des compétences
        assert len(updated_cv.cv_data.skills) == 3
        expected_skills = {
            "Développement Web": "React, JavaScript, HTML/CSS, Node.js",
            "Backend": "Python, Django, FastAPI, SQL",
            "DevOps": "Docker, CI/CD, AWS, Git"
        }
        for skill in updated_cv.cv_data.skills:
            assert skill.skills == expected_skills[skill.category_name] 