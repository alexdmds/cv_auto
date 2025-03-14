"""
Utilitaires pour adapter les structures de données entre différents formats
"""
from typing import Dict, Any, List

def cv_data_to_global_state_format(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convertit les données CV du format Firestore au format attendu par GlobalState
    
    Args:
        cv_data: Données CV au format Firestore (selon firestore_schema.json)
        
    Returns:
        Données formatées pour être compatibles avec GlobalState.from_json()
    """
    # Structure de base pour GlobalState
    global_state_data = {
        "head": {
            "name": cv_data.get("name", ""),
            "title_raw": cv_data.get("title", ""),
            "title_generated": cv_data.get("title", ""),
            "title_refined": cv_data.get("title", ""),
            "mail": cv_data.get("mail", ""),
            "tel_raw": cv_data.get("phone", ""),
            "tel_refined": cv_data.get("phone", "")
        },
        "sections": {
            "experience": cv_data.get("sections_name", {}).get("experience_section_name", "Expérience Professionnelle"),
            "education": cv_data.get("sections_name", {}).get("education_section_name", "Formation")
        },
        "experiences": [],
        "education": []
    }
    
    # Conversion des expériences
    if "experiences" in cv_data and cv_data["experiences"]:
        for exp in cv_data["experiences"]:
            # Extraire la description à partir des bullets si disponible
            description = ""
            if "bullets" in exp and exp["bullets"]:
                if isinstance(exp["bullets"], list):
                    description = ". ".join(exp["bullets"])
                elif isinstance(exp["bullets"], str):
                    description = exp["bullets"]
            
            exp_converted = {
                "title_raw": exp.get("title", ""),
                "title_refined": exp.get("title", ""),
                "company_raw": exp.get("company", ""),
                "company_refined": exp.get("company", ""),
                "location_raw": exp.get("location", ""),
                "location_refined": exp.get("location", ""),
                "dates_raw": exp.get("dates", ""),
                "dates_refined": exp.get("dates", ""),
                "description_raw": description,  # Champ requis manquant ajouté
                "description_refined": description,  # Ajout du champ raffiné
                "bullets": exp.get("bullets", []),
                "summary": "",  # Champ requis par GlobalState
                "weight": 1.0,  # Valeur par défaut
                "order": 1,     # Valeur par défaut
                "nb_bullets": len(exp.get("bullets", []))
            }
            global_state_data["experiences"].append(exp_converted)
    
    # Conversion des formations
    if "educations" in cv_data and cv_data["educations"]:
        for edu in cv_data["educations"]:
            edu_converted = {
                "degree_raw": edu.get("title", ""),
                "degree_refined": edu.get("title", ""),
                "institution_raw": edu.get("university", ""),
                "institution_refined": edu.get("university", ""),
                "location_raw": edu.get("location", ""),
                "location_refined": edu.get("location", ""),
                "dates_raw": edu.get("dates", ""),
                "dates_refined": edu.get("dates", ""),
                "description_raw": edu.get("description", ""),
                "description_generated": edu.get("description", ""),  # Pour compléter le modèle
                "description_refined": edu.get("description", ""),
                "summary": "",  # Champ requis par GlobalState
                "weight": 1.0,  # Valeur par défaut
                "order": 1,     # Valeur par défaut
                "nb_mots": 0    # Valeur par défaut
            }
            global_state_data["education"].append(edu_converted)
    
    # Conversion des compétences
    skills_raw = []
    competences = {}
    if "skills" in cv_data:
        for skill_category in cv_data["skills"]:
            if isinstance(skill_category, dict):
                category_name = skill_category.get("category_name", "")
                skill_text = skill_category.get("skills", "")
                
                # Ajouter aux skills_raw pour le format texte
                if skill_text:
                    if isinstance(skill_text, str):
                        skills_raw.append(skill_text)
                    elif isinstance(skill_text, list):
                        skills_raw.extend(skill_text)
                
                # Ajouter aux compétences pour le format structuré
                if category_name:
                    if isinstance(skill_text, str):
                        competences[category_name] = skill_text.split(", ")
                    elif isinstance(skill_text, list):
                        competences[category_name] = skill_text
    
    global_state_data["skills_raw"] = ", ".join(skills_raw)
    global_state_data["competences"] = competences
    
    # Conversion des langues
    langues = []
    if "languages" in cv_data:
        for lang in cv_data["languages"]:
            if isinstance(lang, dict):
                langue = {
                    "language": lang.get("language", ""),
                    "level": lang.get("level", "")
                }
                langues.append(langue)
    
    global_state_data["langues"] = langues
    
    # Hobbies
    global_state_data["hobbies_raw"] = cv_data.get("hobbies", "")
    global_state_data["hobbies_refined"] = cv_data.get("hobbies", "")
    
    # Poste
    global_state_data["job_raw"] = cv_data.get("job_raw", "")
    global_state_data["job_refined"] = cv_data.get("job_raw", "")
    
    return global_state_data 