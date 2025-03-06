"""
Convertit les données JSON brutes en GlobalState structuré.
"""

from typing import Dict, Any
from data_structures import GlobalState, Head, Experience, Education, Language

def convert_to_global_state(data: Dict[str, Any]) -> GlobalState:
    """
    Convertit les données JSON brutes en GlobalState.
    
    Args:
        data: Dictionnaire contenant les données JSON brutes
    
    Returns:
        GlobalState: État global structuré
    """
    cv_data = data["cv_data"]
    
    # Construction du Head
    head_data = cv_data["head"]
    head = Head(
        name=head_data["name"],
        title_raw=head_data["general_title"],
        title_refined="",  # À remplir par le LLM
        mail=head_data["email"],
        tel_raw=head_data["phone"],
        tel_refined="",  # À remplir par le LLM
    )
    
    # Construction des expériences
    experiences = []
    for exp in cv_data["experiences"]["experiences"]:
        experience = Experience(
            title_raw=exp["intitule"],
            title_refined="",  # À remplir par le LLM
            company_raw=exp["etablissement"],
            company_refined="",  # À remplir par le LLM
            location_raw=exp.get("lieu", ""),
            location_refined="",  # À remplir par le LLM
            dates_raw=exp["dates"],
            dates_refined="",  # À remplir par le LLM
            description_raw=exp["description"],
            description_refined="",  # À remplir par le LLM
            summary="",  # À remplir par le LLM
            bullets=[],  # À remplir par le LLM
            weight=0.0,  # À calculer plus tard
            order=None,  # À définir plus tard
            nb_bullets=0  # À calculer plus tard
        )
        experiences.append(experience)
    
    # Construction des formations
    education = []
    for edu in cv_data["education"]["educations"]:
        education_item = Education(
            degree_raw=edu["intitule"],
            degree_refined="",  # À remplir par le LLM
            institution_raw=edu["etablissement"],
            institution_refined="",  # À remplir par le LLM
            location_raw=edu.get("lieu", ""),
            location_refined="",  # À remplir par le LLM
            dates_raw=edu["dates"],
            dates_refined="",  # À remplir par le LLM
            description_raw=edu["description"],
            description_refined="",  # À remplir par le LLM
            summary="",  # À remplir par le LLM
            weight=0.0,  # À calculer plus tard
            order=None,  # À définir plus tard
            nb_bullets=0  # À calculer plus tard
        )
        education.append(education_item)
    
    # Construction de l'état global
    return GlobalState(
        head=head,
        sections={
            "skills": cv_data["skills"]["description"],
            "hobbies": cv_data["hobbies"]["description"]
        },
        experiences=experiences,
        education=education,
        competences={},  # À remplir par le LLM
        langues=[],  # À remplir par le LLM
        hobbies_raw=cv_data["hobbies"]["description"],
        hobbies_refined="",  # À remplir par le LLM
        job_raw="",  # À extraire du titre général
        job_refined=""  # À remplir par le LLM
    )

if __name__ == "__main__":
    # Test de la fonction
    import json
    
    with open("data_test.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    state = convert_to_global_state(data)
    print("État global créé avec succès !")
    print(f"Nombre d'expériences : {len(state.experiences)}")
    print(f"Nombre de formations : {len(state.education)}") 