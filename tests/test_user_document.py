#!/usr/bin/env python3
"""
Script de test pour le constructeur from_firestore_id de la classe UserDocument.
Ce script permet de tester la récupération d'un document utilisateur depuis Firestore.
"""

import sys
import os
import argparse
from pprint import pprint

# Ajout du répertoire parent au PYTHONPATH pour trouver les modules du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import du modèle UserDocument
from backend.models import UserDocument

def test_user_document(user_id):
    """
    Teste la récupération d'un document utilisateur à partir de son ID Firestore.
    
    Args:
        user_id (str): ID du document utilisateur à récupérer
    """
    print(f"Tentative de récupération de l'utilisateur avec l'ID: {user_id}")
    
    # Utilisation du constructeur
    user = UserDocument.from_firestore_id(user_id)
    
    if user is None:
        print(f"❌ Aucun utilisateur trouvé avec l'ID: {user_id}")
        return
    
    print(f"✅ Utilisateur trouvé avec l'ID: {user_id}")
    
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
        if head.linkedin_url:
            print(f"LinkedIn: {head.linkedin_url}")
    
    # Affichage des CV disponibles
    if user.cvs:
        print(f"\n=== CVs ({len(user.cvs)}) ===")
        for idx, cv in enumerate(user.cvs, 1):
            print(f"\nCV #{idx}: {cv.cv_name}")
            if cv.job_raw:
                job_preview = cv.job_raw[:50] + "..." if len(cv.job_raw) > 50 else cv.job_raw
                print(f"Description du poste: {job_preview}")
    else:
        print("\nAucun CV trouvé pour cet utilisateur.")
    
    # Test de la structure complète
    print("\n=== TEST DE LA STRUCTURE COMPLÈTE ===")
    
    # Test des expériences dans le profil
    if user.profile.experiences:
        print(f"Nombre d'expériences dans le profil: {len(user.profile.experiences)}")
        
    # Test des formations dans le profil
    if user.profile.educations:
        print(f"Nombre de formations dans le profil: {len(user.profile.educations)}")
    
    # Test des compétences dans le profil
    if user.profile.skills:
        categories = user.profile.skills.keys()
        print(f"Catégories de compétences: {', '.join(categories)}")
    
    # Test des langues dans le profil
    if user.profile.languages:
        print(f"Nombre de langues: {len(user.profile.languages)}")
    
    print("\nTest terminé avec succès!")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Test du constructeur UserDocument.from_firestore_id")
    parser.add_argument("user_id", nargs="?", default="test_user", help="ID Firestore de l'utilisateur à récupérer")
    
    args = parser.parse_args()
    
    test_user_document(args.user_id)

if __name__ == "__main__":
    main() 