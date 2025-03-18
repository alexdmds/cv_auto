import operator
from typing import List, Dict
from typing_extensions import TypedDict, Annotated
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from dev_test.models_langchain.llm_config import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from data_structures import Education

class State(TypedDict):
    job_summary: str
    markdown_choice: str
    educations_raw: List[Education]
    educations_weighted: Annotated[List[Education], operator.add]
    educations_nb_mots: List[Education]
    educations_description: Annotated[List[Education], operator.add]

class WorkerWeightState(TypedDict):
    education: Education
    markdown_choice: str

class WorkerBulletsState(TypedDict):
    education: Education
    job_summary: str

class PlanWeight(BaseModel):
    """Structure pour les poids et l'ordre d'une éducation"""
    order: int = Field(description="Ordre d'apparition dans le CV (1 = premier, null si non retenu)", default=None)
    weight: float = Field(description="Poids de l'éducation (0-1)")

def generate_markdown_choice(state: State) -> dict:
    """Génère un markdown de choix d'expériences à partir du résumé de poste et des expériences brutes"""
    llm = get_llm()
    job_summary = state["job_summary"]
    educations = state["educations_raw"]
    
    # Prépare le prompt pour le LLM
    educations_text = ""
    for i, edu in enumerate(educations):
        educations_text += f"\nFormation {i+1}:\n"
        educations_text += f"Titre: {edu.degree_raw}\n"
        educations_text += f"Ecole: {edu.institution_raw}\n"
        educations_text += f"Lieu: {edu.location_raw}\n"
        educations_text += f"Dates: {edu.dates_raw}\n"
        educations_text += f"Résumé: {edu.summary}\n"

    prompt = f"""En te basant sur le résumé du poste suivant:
{job_summary}

Et les formations suivantes:
{educations_text}

Analyse la pertinence de chaque expérience pour ce poste.
Sélectionne uniquement les expériences les plus pertinentes (4 maximum) pour tenir sur un CV.
Pour chaque expérience, attribue:
1. Un poids entre 0 et 1 (0 = non pertinent, 1 = très pertinent)
2. Un ordre d'apparition sur le CV (1 = première position, null si elle n'est pas choisie)

Réponds sous forme de markdown avec ce format:
# Analyse des Expériences

## [Titre du poste] chez [Entreprise]
- Poids: [poids]
- Ordre: [ordre]
- Justification: [justification en une phrase]

[etc pour chaque expérience]"""

    response = llm.invoke([
        SystemMessage(content="Tu es un expert en recrutement qui analyse la pertinence des expériences par rapport à un poste."),
        HumanMessage(content=prompt)
    ])

    # Met à jour les poids et ordres dans les objets Experience
    markdown = response.content
    
    return {"markdown_choice": markdown}

def weight_educations(state: WorkerWeightState) -> dict:
    """Poids les éducations en fonction du markdown de choix"""
    llm = get_llm().with_structured_output(PlanWeight)
    markdown = state["markdown_choice"]
    education = state["education"]
    
    prompt = f"""Analyse ce markdown de choix d'expériences et trouve l'expérience suivante:
Titre: {education.degree_raw}
Ecole: {education.institution_raw}

Si cette formation n'est pas mentionnée dans le markdown, réponds avec:
- order: null  
- weight: 0

Si elle est mentionnée, extrait simplement et exactement:
1. Le poids indiqué après "Poids:" dans le markdown
2. L'ordre indiqué après "Ordre:" dans le markdown

Ne fais aucun autre calcul ou raisonnement, copie simplement ces valeurs.

Voici le markdown à analyser:
{markdown}"""

    response = llm.invoke(prompt)
    
    education.order = response.order
    education.weight = response.weight
    
    return {"educations_weighted": [education]}

def collect_weighted_educations(state: State) -> dict:
    """Collecte toutes les éducations pondérées et les transmet aux workers de génération de bullets"""
    # Met à jour le nombre de mots en fonction du poids
    for education in state["educations_weighted"]:
        # Calcul proportionnel entre 20 et 50 mots basé sur le weight (0-1)
        education.nb_mots = int(20 + (education.weight * 30))
            
    return {"educations_nb_mots": state["educations_weighted"]}

def generate_bullets(state: WorkerBulletsState) -> dict:
    """Génère une description adaptée pour une formation"""
    education = state["education"] 
    llm = get_llm()
    job_summary = state["job_summary"]
    
    if not education.order:  # Si la formation n'est pas retenue
        return {"educations_description": [education]}
        
    # Utilise nb_mots pour adapter la longueur de la description
    nb_mots = education.nb_mots
    
    prompt = f"""
    Génère une description de {nb_mots} mots qui met en valeur la pertinence de cette formation pour le poste visé.
    
    Poste visé : {job_summary}
    Formation : {education.degree_raw}
    Description : {education.description_raw}

    Règles :
    - Sois concis et factuel
    - Mentionne uniquement les aspects pertinents pour le poste
    - Base-toi uniquement sur les informations fournies sans inventer
    - Format : une phrase directe décrivant les compétences/connaissances acquises
    - Respecte strictement le nombre de mots demandé ({nb_mots} mots)
    - Ne pas mentionner l'établissement ou les dates
    """
    
    response = llm.invoke(prompt)
    
    # Met à jour l'éducation avec la description générée
    education.description_generated = response.content.strip()
    
    return {"educations_description": [education]}


# Construction du graphe
graph = StateGraph(State)

# Ajout des nœuds
graph.add_node("generate_markdown_choice", generate_markdown_choice)
graph.add_node("weight_educations", weight_educations)
graph.add_node("collect_weighted", collect_weighted_educations)
graph.add_node("generate_bullets", generate_bullets)

# Configuration des transitions
graph.add_edge(START, "generate_markdown_choice")

def route_to_weight_workers(state: State):
    """Route chaque expérience vers un worker de pondération"""
    return [
        Send("weight_educations", {
            "education": education,
            "markdown_choice": state["markdown_choice"]
        })
        for education in state["educations_raw"]
    ]

def route_to_bullet_workers(state: State):
    """Route chaque expérience pondérée vers un worker de génération de bullets"""
    return [
        Send("generate_bullets", {
            "education": education,
            "job_summary": state["job_summary"]
        })
        for education in state["educations_nb_mots"]
    ]

graph.add_conditional_edges(
    "generate_markdown_choice",
    route_to_weight_workers,
    ["weight_educations"]
)

graph.add_edge("weight_educations", "collect_weighted")

graph.add_conditional_edges(
    "collect_weighted",
    route_to_bullet_workers,
    ["generate_bullets"]
)

graph.add_edge("generate_bullets", END)

# Compilation
chain = graph.compile()

def prioritize_edu(job_summary: str, educations: List[Education]) -> List[Education]:
    """
    Priorise et enrichit une liste d'éducations en fonction d'un résumé de poste.
    
    Args:
        job_summary: Description du poste visé
        educations: Liste des éducations à traiter
        
    Returns:
        Liste des éducations enrichies et priorisées
    """
    # Exécution du workflow
    result = chain.invoke({
        "job_summary": job_summary,
        "educations_raw": educations,
        "educations_bullets": [],
        "educations_weighted": [],
        "markdown_choice": ""
    })
    
    # Tri des expériences par ordre
    sorted_educations = sorted(
        result["educations_description"],
        key=lambda x: x.order if x.order is not None else float('inf')
    )
    
    return sorted_educations

if __name__ == "__main__":
    import json
    import os
    from data_structures import GlobalState

    # Obtenir le chemin absolu du répertoire du script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    state_path = os.path.join(script_dir, "result_state.json")
    
    with open(state_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Création d'une instance de GlobalState à partir du JSON
    global_state = GlobalState.from_json(data)  # job_summary est optionnel

    #job summary
    print(global_state.job_refined)

    # Création du State pour prioritize_exp
    state = {
        "job_summary": global_state.job_refined,
        "markdown_choice": "",
        "educations_raw": global_state.education,
        "educations_weighted": [],
        "educations_description": []
    }

    # Test de la fonction
    educations_priorisees = prioritize_edu(state["job_summary"], state["educations_raw"])
    
    print("\nFormations priorisées:")
    for edu in educations_priorisees:
        print(f"\n{edu.degree_raw} à {edu.institution_raw}")
        print(f"Ordre: {edu.order}")
        print("Description:")
        print(edu.description_generated)
