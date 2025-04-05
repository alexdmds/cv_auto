#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour importer les modules du backend
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from backend.models import UserDocument, CV, CVData
import firebase_admin
from firebase_admin import credentials

def create_cv(user_id: str, cv_name: str, job_raw: str):
    """
    Crée un nouveau CV dans Firestore pour un utilisateur donné.
    
    Args:
        user_id (str): ID de l'utilisateur
        cv_name (str): Nom du CV à créer
        job_raw (str): Description brute du poste
    """
    # Initialiser Firebase Admin si pas déjà fait
    if not firebase_admin._apps:
        # Utiliser les credentials par défaut ou le fichier de service si en local
        try:
            firebase_admin.initialize_app()
        except Exception as e:
            # Si en local, chercher le fichier de service
            cred_path = os.path.join(root_dir, "firebase-credentials.json")
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                raise Exception("Impossible d'initialiser Firebase: pas de credentials trouvés")

    # Récupérer ou créer le document utilisateur
    user_doc = UserDocument.from_firestore_id(user_id)
    if not user_doc:
        print(f"Création d'un nouveau document utilisateur pour {user_id}")
        user_doc = UserDocument(id=user_id)
    
    # Vérifier si un CV avec ce nom existe déjà
    if any(cv.cv_name == cv_name for cv in user_doc.cvs):
        raise ValueError(f"Un CV nommé '{cv_name}' existe déjà pour cet utilisateur")
    
    # Créer le CVData avec les champs requis initialisés
    cv_data = CVData(
        name="John Doe",  # Nom par défaut
        title="Machine Learning Engineer",  # Titre par défaut
        mail="john.doe@example.com",  # Email par défaut
        phone="+33 6 12 34 56 78",  # Téléphone par défaut
        sections_name={
            "experience_section_name": "Expérience Professionnelle",
            "education_section_name": "Formation",
            "skills_section_name": "Compétences",
            "languages_section_name": "Langues",
            "hobbies_section_name": "Centres d'intérêt"
        },
        experiences=[],  # Liste vide d'expériences
        educations=[],  # Liste vide de formations
        skills=[],  # Liste vide de compétences
        languages=[],  # Liste vide de langues
        hobbies="",  # Centres d'intérêt vides
        lang_of_cv="FR"  # Langue par défaut du CV
    )
    
    # Créer le nouveau CV avec le CVData initialisé
    new_cv = CV(
        cv_name=cv_name,
        job_raw=job_raw,
        cv_data=cv_data
    )
    
    # Ajouter le CV à la liste des CVs de l'utilisateur
    user_doc.cvs.append(new_cv)
    
    # Sauvegarder dans Firestore
    user_doc.save()
    print(f"CV '{cv_name}' créé avec succès pour l'utilisateur {user_id}")
    print(f"Longueur de la fiche de poste : {len(job_raw)} caractères")

if __name__ == "__main__":
    # Configuration en dur
    USER_ID = "test_user"
    CV_NAME = "cv_test"
    job_raw = """Fiche de Poste - Machine Learning Engineer

Localisation : Paris, France (Hybrid)
Type de Contrat : CDI
Experience : 3+ ans
Salaire : 55k - 75k EUR selon experience

Description du poste :
Nous recherchons un(e) Machine Learning Engineer expérimenté(e) pour rejoindre notre équipe.
Vous serez responsable de la conception, du développement et du déploiement de modèles ML."""
    
    try:
        create_cv(USER_ID, CV_NAME, job_raw)
    except Exception as e:
        print(f"Erreur lors de la création du CV: {e}")
        sys.exit(1) 