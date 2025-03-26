import pytest
from unittest.mock import Mock, patch
from flask import Flask
from backend.api.endpoint_generate_cv import generate_cv_endpoint
from backend.models import UserDocument, CV, CVData, Profile, HeadProfile, ExperienceProfile, EducationProfile
from ai_module.lg_models import CVGenState
from datetime import datetime

# Création d'une application Flask de test
app = Flask(__name__)

@pytest.fixture
def mock_user_document():
    """Fixture pour créer un mock de UserDocument"""
    user_doc = Mock(spec=UserDocument)
    user_doc.id = "test_user"
    user_doc.cvs = []
    
    # Configuration de la structure imbriquée
    head = Mock(spec=HeadProfile)
    head.name = "Test User"
    head.title = "Test Title"
    head.mail = "test@example.com"
    head.phone = "+33123456789"
    
    # Création des expériences
    experience = Mock(spec=ExperienceProfile)
    experience.title = "Senior Developer"
    experience.company = "Tech Corp"
    experience.dates = "2020-2023"
    experience.location = "Paris"
    experience.full_description = "Lead developer on multiple projects"
    
    # Création des formations
    education = Mock(spec=EducationProfile)
    education.title = "Master in Computer Science"
    education.university = "University of Tech"
    education.dates = "2018-2020"
    education.full_description = "Specialized in AI"
    
    profile = Mock(spec=Profile)
    profile.head = head
    profile.experiences = [experience]
    profile.educations = [education]
    profile.languages = "English (C2), French (Native)"
    profile.skills = "Python, JavaScript, Machine Learning"
    profile.hobbies = "Reading, Sports"
    
    user_doc.profile = profile
    return user_doc

@pytest.fixture
def mock_cv_gen_state():
    """Fixture pour créer un mock de CVGenState"""
    cv_state = Mock(spec=CVGenState)
    cv_state.head.name = "Test User"
    cv_state.head.title_refined = "Senior Developer"
    cv_state.head.mail = "test@example.com"
    cv_state.head.tel_refined = "+33123456789"
    return cv_state

@patch('backend.api.endpoint_generate_cv.UserDocument')
@patch('backend.api.endpoint_generate_cv.generate_cv')
@patch('backend.api.endpoint_generate_cv.upload_to_firebase_storage')
def test_generate_cv_endpoint_success(mock_upload, mock_generate_cv, mock_user_document_class, mock_user_document):
    """Test du cas de succès de generate_cv_endpoint"""
    with app.app_context():
        # Configuration des mocks
        mock_user_document_class.from_firestore_id.return_value = mock_user_document
        mock_generate_cv.return_value = mock_cv_gen_state
        mock_upload.return_value = "https://storage.example.com/cv.pdf"
        
        # Simuler un CV existant
        cv = CV(cv_name="test_cv", cv_data=CVData())
        mock_user_document.cvs = [cv]
        mock_user_document.update_cv_from_global_state.return_value = {
            "cv_name": "test_cv",
            "updated": True,
            "name": "Test User",
            "title": "Test Title",
            "experiences": 1,
            "educations": 1,
            "skills": 1,
            "languages": 1,
            "hobbies_updated": True,
            "job_updated": True
        }

        # Appel de la fonction
        response, status_code = generate_cv_endpoint("test_user", "test_cv")

        # Vérifications
        assert status_code == 200
        assert response.json["success"] is True
        assert "data" in response.json
        assert response.json["data"]["user_id"] == "test_user"
        assert response.json["data"]["cv_name"] == "test_cv"
        assert "timestamp" in response.json["data"]
        assert response.json["data"]["pdf_url"] == "https://storage.example.com/cv.pdf"
        assert response.json["data"]["firestore_updated"] is True

@patch('backend.api.endpoint_generate_cv.UserDocument')
def test_generate_cv_endpoint_user_not_found(mock_user_document_class):
    """Test du cas où l'utilisateur n'est pas trouvé"""
    with app.app_context():
        # Configuration du mock
        mock_user_document_class.from_firestore_id.return_value = None

        # Appel de la fonction
        response, status_code = generate_cv_endpoint("nonexistent_user", "test_cv")

        # Vérifications
        assert status_code == 404
        assert "error" in response.json
        assert "introuvable" in response.json["error"]

@patch('backend.api.endpoint_generate_cv.UserDocument')
@patch('backend.api.endpoint_generate_cv.generate_cv')
def test_generate_cv_endpoint_cv_update_failed(mock_generate_cv, mock_user_document_class, mock_user_document):
    """Test du cas où la mise à jour du CV échoue"""
    with app.app_context():
        # Configuration des mocks
        mock_user_document_class.from_firestore_id.return_value = mock_user_document
        mock_generate_cv.return_value = mock_cv_gen_state
        mock_user_document.update_cv_from_global_state.return_value = None

        # Appel de la fonction
        response, status_code = generate_cv_endpoint("test_user", "nonexistent_cv")

        # Vérifications
        assert status_code == 404
        assert "error" in response.json
        assert "non trouvé pour mise à jour" in response.json["error"]

@patch('backend.api.endpoint_generate_cv.UserDocument')
@patch('backend.api.endpoint_generate_cv.generate_cv')
def test_generate_cv_endpoint_exception(mock_generate_cv, mock_user_document_class, mock_user_document):
    """Test du cas où une exception est levée"""
    with app.app_context():
        # Configuration des mocks
        mock_user_document_class.from_firestore_id.return_value = mock_user_document
        mock_generate_cv.side_effect = Exception("Test error")

        # Appel de la fonction
        response, status_code = generate_cv_endpoint("test_user", "test_cv")

        # Vérifications
        assert status_code == 500
        assert "error" in response.json
        assert "Test error" in response.json["error"] 