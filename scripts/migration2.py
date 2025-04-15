import firebase_admin
from firebase_admin import firestore
import os
from typing import Dict, Any
import uuid

def init_firebase():
    """Initialise la connexion à Firebase"""
    # Utilise l'authentification existante
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    return firestore.client()

def normalize_section_names(section_names: Dict[str, Any]) -> Dict[str, Any]:
    """Normalise les noms des sections selon le schéma"""
    normalized = {
        "experience_section_name": "Expérience Professionnelle",
        "education_section_name": "Formation",
        "skills_section_name": "Compétences",
        "languages_section_name": "Langues",
        "hobbies_section_name": "Centres d'intérêt"
    }
    
    # Copier les valeurs existantes si elles existent
    for key in normalized:
        if key in section_names:
            normalized[key] = section_names[key]
    
    return normalized

def normalize_skills(skills: list) -> list:
    """Normalise la structure des skills pour qu'elle corresponde au schéma"""
    normalized_skills = []
    for skill in skills:
        if isinstance(skill, dict):
            if "skills" in skill:
                # Si skills est une chaîne, la convertir en liste
                if isinstance(skill["skills"], str):
                    skill["skills"] = [skill["skills"]]
                # Si skills est déjà une liste, la garder telle quelle
                elif isinstance(skill["skills"], list):
                    pass
                else:
                    # Si c'est un autre type, le convertir en liste avec une seule valeur
                    skill["skills"] = [str(skill["skills"])]
            normalized_skills.append(skill)
    return normalized_skills

def convert_dict_to_list(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convertit les dictionnaires en listes pour les champs spécifiques"""
    if "cvs" in data and isinstance(data["cvs"], dict):
        data["cvs"] = list(data["cvs"].values())
    
    if "profile" in data:
        profile = data["profile"]
        if "educations" in profile and isinstance(profile["educations"], dict):
            profile["educations"] = list(profile["educations"].values())
        if "experiences" in profile and isinstance(profile["experiences"], dict):
            profile["experiences"] = list(profile["experiences"].values())
    
    return data

def migrate_document(db: firestore.Client, doc_id: str):
    """Migre un document spécifique de la collection users vers profiles et cvs"""
    doc_ref = db.collection("users").document(doc_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        print(f"Document {doc_id} non trouvé")
        return
    
    data = doc.to_dict()
    
    # Convertir les dictionnaires en listes
    data = convert_dict_to_list(data)
    
    # Migration du profil
    if "profile" in data:
        profile = data["profile"]
        
        # S'assurer que le champ head existe
        if "head" not in profile:
            profile["head"] = {}
        
        # Ajouter linkedin_url s'il n'existe pas
        if "linkedin_url" not in profile["head"]:
            profile["head"]["linkedin_url"] = ""
        
        # Migration des éducations
        if "educations" in profile:
            for edu in profile["educations"]:
                if "full_descriptions" in edu:
                    edu["description"] = edu["full_descriptions"]
                    del edu["full_descriptions"]
                elif "full_description" in edu:
                    edu["description"] = edu["full_description"]
                    del edu["full_description"]
        
        # Migration des expériences
        if "experiences" in profile:
            for exp in profile["experiences"]:
                if "full_descriptions" in exp:
                    exp["description"] = exp["full_descriptions"]
                    del exp["full_descriptions"]
        
        # Créer le document dans la collection profiles
        db.collection("profiles").document(doc_id).set(profile)
        print(f"Profil migré pour l'utilisateur {doc_id}")
    
    # Migration des CVs
    if "cvs" in data:
        for cv in data["cvs"]:
            if "cv_data" in cv:
                cv_data = cv["cv_data"]
                # Renommer sections_name en section_names et normaliser les noms
                if "sections_name" in cv_data:
                    cv_data["section_names"] = normalize_section_names(cv_data["sections_name"])
                    del cv_data["sections_name"]
                elif "section_names" in cv_data:
                    cv_data["section_names"] = normalize_section_names(cv_data["section_names"])
                
                # Normaliser la structure des skills
                if "skills" in cv_data:
                    cv_data["skills"] = normalize_skills(cv_data["skills"])
                
                # Créer un nouveau document CV avec un ID aléatoire
                cv_doc = {
                    "user_id": doc_id,
                    "cv_url": cv.get("cv_url", ""),
                    "job_raw": cv.get("job_raw", ""),
                    "job_sumup": cv.get("job_sumup", ""),
                    "cv_name": cv.get("cv_name", ""),
                    "cv_data": cv_data
                }
                
                # Générer un ID aléatoire pour le CV
                cv_id = str(uuid.uuid4())
                db.collection("cvs").document(cv_id).set(cv_doc)
                print(f"CV migré avec l'ID {cv_id} pour l'utilisateur {doc_id}")
    
    print(f"Migration terminée pour le document {doc_id}")

def main():
    """Fonction principale"""
    db = init_firebase()
    
    # Demander l'ID du document à migrer
    doc_id = input("Entrez l'ID du document à migrer (ou 'all' pour tous les documents) : ")
    
    if doc_id.lower() == "all":
        # Récupérer tous les documents de la collection users
        docs = db.collection("users").stream()
        for doc in docs:
            print(f"\nMigration du document {doc.id}")
            migrate_document(db, doc.id)
    else:
        migrate_document(db, doc_id)

if __name__ == "__main__":
    main()
