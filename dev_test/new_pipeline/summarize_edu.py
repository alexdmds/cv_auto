import operator
from typing import List, Dict
from typing_extensions import TypedDict, Annotated

# LangGraph
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send

from dev_test.models_langchain.llm_config_dev import get_llm
from data_structures import Education

##############################################################################
# 1. Définition des structures de données (state principal, worker state)
##############################################################################

class EduState(TypedDict):
    education_raw: List[Education]
    education_refined: Annotated[List[Education], operator.add]

class WorkerState(TypedDict):
    education: Education

##############################################################################
# 2. Définition des noeuds (fonctions) du graphe
##############################################################################

def summarize_edu(state: WorkerState) -> dict:
    """
    Résume une formation.
    """
    llm = get_llm()
    edu = state["education"]
    
    prompt = f"""
    Résume cette formation en 50 mots maximum :
    
    Diplôme : {edu.degree_raw}
    Établissement : {edu.institution_raw}
    Période : {edu.dates_raw}
    Description : {edu.description_raw}

    Donne seulement le résumé, pas besoin de rappeler les informations de la formation.
    """
    
    response = llm.invoke(prompt)

    # Création d'une nouvelle formation en copiant l'originale et en mettant à jour les champs
    education_refined = Education(**edu.model_dump())  # Copie tous les champs
    education_refined.summary = response.content  # Met le résumé comme summary
    
    return {"education_refined": [education_refined]}

##############################################################################
# 3. Construction du graphe
##############################################################################

# Construction du graphe
edu_graph = StateGraph(EduState)
edu_graph.add_node("summarize_edu", summarize_edu)

def route_education(state: EduState):
    """Route chaque formation vers le worker de résumé"""
    return [Send("summarize_edu", {"education": edu}) for edu in state["education_raw"]]

edu_graph.add_conditional_edges(START, route_education, ["summarize_edu"])
edu_graph.add_edge("summarize_edu", END)

# Compilation du workflow
compiled_edu_graph = edu_graph.compile()

def summarize_edus(education: List[Education]) -> List[Education]:
    """
    Résume une liste de formations en utilisant le graphe de traitement.
    
    Args:
        education: Liste des formations à traiter
        
    Returns:
        Liste des formations enrichies avec leurs résumés
    """
    # Prépare l'état initial
    state = {
        "education_raw": education,
        "education_refined": []
    }
    
    # Exécute le graphe
    result = compiled_edu_graph.invoke(state)
    
    # Retourne les formations enrichies
    return result["education_refined"]