#!/usr/bin/env python3
"""
Script de test pour les constructeurs de la classe UserDocument.
"""

import sys
import os
from typing import Optional

# Ajout du répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import UserDocument
from ai_module.lg_models import ProfileState, GeneralInfo, GlobalExperience, GlobalEducation

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
                intitule="Développeur Senior",
                dates="2020-2023",
                etablissement="Tech Company",
                lieu="Paris",
                description="Développement d'applications web"
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

def test_from_firestore_id(user_id: str) -> Optional[UserDocument]:
    """
    Teste la récupération d'un document utilisateur depuis Firestore
    
    Args:
        user_id (str): ID du document à récupérer
        
    Returns:
        Optional[UserDocument]: Le document récupéré ou None
    """
    print(f"\n=== Test de from_firestore_id avec ID: {user_id} ===")
    
    user = UserDocument.from_firestore_id(user_id)
    
    if user is None:
        print(f"❌ Aucun utilisateur trouvé avec l'ID: {user_id}")
        return None
        
    print(f"✅ Utilisateur trouvé avec l'ID: {user_id}")
    print_user_document(user)
    return user

def test_from_profile_state() -> Optional[UserDocument]:
    """
    Teste la création d'un document utilisateur depuis un ProfileState
    
    Returns:
        Optional[UserDocument]: Le document créé ou None
    """
    print("\n=== Test de from_profile_state ===")
    
    profile_state = create_mock_profile_state()
    user = UserDocument.from_profile_state(profile_state, "test_user_id")
    
    if user is None:
        print("❌ Échec de la création depuis ProfileState")
        return None
        
    print("✅ Document créé avec succès depuis ProfileState")
    print_user_document(user)
    return user

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
    firestore_user = test_from_firestore_id(user_id)
    profile_user = test_from_profile_state()

if __name__ == "__main__":
    main() 