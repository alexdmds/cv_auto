#!/usr/bin/env python3
"""Tests unitaires pour les méthodes de normalisation de UserDocument"""

import pytest
from backend.models import UserDocument

def test_normalize_full_descriptions():
    """Test de la normalisation des descriptions d'expérience"""
    # Test avec une liste
    assert UserDocument._normalize_full_descriptions(["Description 1", "Description 2"]) == "Description 1"
    
    # Test avec une liste vide
    assert UserDocument._normalize_full_descriptions([]) == ""
    
    # Test avec une chaîne
    assert UserDocument._normalize_full_descriptions("Description simple") == "Description simple"
    
    # Test avec None
    assert UserDocument._normalize_full_descriptions(None) == ""

def test_normalize_skills():
    """Test de la normalisation des compétences"""
    # Test avec un dictionnaire
    skills_dict = {
        "Programmation": ["Python", "JavaScript"],
        "DevOps": ["Docker", "Kubernetes"]
    }
    expected = "Python, JavaScript, Docker, Kubernetes"
    assert sorted(UserDocument._normalize_skills(skills_dict).split(", ")) == sorted(expected.split(", "))
    
    # Test avec une liste
    skills_list = ["Python", "JavaScript", "Docker"]
    assert UserDocument._normalize_skills(skills_list) == "Python, JavaScript, Docker"
    
    # Test avec une chaîne
    assert UserDocument._normalize_skills("Python, JavaScript") == "Python, JavaScript"
    
    # Test avec None
    assert UserDocument._normalize_skills(None) == ""

def test_normalize_languages():
    """Test de la normalisation des langues"""
    # Test avec une liste de dictionnaires
    languages_list = [
        {"language": "Français", "level": "C2"},
        {"language": "Anglais", "level": "B2"}
    ]
    expected = "Français (C2), Anglais (B2)"
    assert UserDocument._normalize_languages(languages_list) == expected
    
    # Test avec une liste de dictionnaires incomplets
    incomplete_list = [
        {"language": "Français"},
        {"level": "B2"},
        {}
    ]
    assert UserDocument._normalize_languages(incomplete_list) == "Français"
    
    # Test avec une chaîne
    assert UserDocument._normalize_languages("Français (C2), Anglais (B2)") == "Français (C2), Anglais (B2)"
    
    # Test avec None
    assert UserDocument._normalize_languages(None) == ""

def test_preprocess_firestore_data():
    """Test du prétraitement complet des données Firestore"""
    raw_data = {
        "profile": {
            "experiences": [
                {
                    "title": "Développeur",
                    "full_descriptions": ["Description principale", "Description secondaire"]
                }
            ],
            "skills": {
                "Programmation": ["Python", "JavaScript"],
                "DevOps": ["Docker"]
            },
            "languages": [
                {"language": "Français", "level": "C2"},
                {"language": "Anglais", "level": "B2"}
            ]
        }
    }
    
    processed = UserDocument._preprocess_firestore_data(raw_data)
    
    assert processed["profile"]["experiences"][0]["full_descriptions"] == "Description principale"
    assert sorted(processed["profile"]["skills"].split(", ")) == sorted("Python, JavaScript, Docker".split(", "))
    assert processed["profile"]["languages"] == "Français (C2), Anglais (B2)"

if __name__ == "__main__":
    pytest.main([__file__]) 