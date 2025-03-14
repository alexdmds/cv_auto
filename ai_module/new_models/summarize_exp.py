import operator
from typing import List, Dict
from typing_extensions import TypedDict, Annotated

# LangGraph
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send

from dev_test.models_langchain.llm_config import get_llm
from data_structures import Experience

##############################################################################
# 1. Définition des structures de données (state principal, worker state)
##############################################################################

class ExpState(TypedDict):
    experiences_raw: List[Experience]
    experiences_refined: Annotated[List[Experience], operator.add]

class WorkerState(TypedDict):
    experience: Experience

##############################################################################
# 2. Définition des noeuds (fonctions) du graphe
##############################################################################

def summarize_exp(state: WorkerState) -> dict:
    """
    Résume une expérience professionnelle.
    """
    llm = get_llm()
    exp = state["experience"]
    
    prompt = f"""
    Résume le contenu de cette expérience en 50 mots maximum :
    
    Poste : {exp.title_raw}
    Entreprise : {exp.company_raw}
    Lieu : {exp.location_raw}
    Dates : {exp.dates_raw}
    Description : {exp.description_raw}

    Donne seulement le résumé, pas besoin de rappeler les informations de l'expérience.
    """
    
    response = llm.invoke(prompt)

    # Création d'une nouvelle expérience en copiant l'originale et en mettant à jour les champs
    experience_refined = Experience(**exp.model_dump())  # Copie tous les champs
    experience_refined.summary = response.content  # Met le résumé comme summary
    
    return {"experiences_refined": [experience_refined]}


##############################################################################
# 3. Construction du graphe
##############################################################################

# Construction du graphe
exp_graph = StateGraph(ExpState)
exp_graph.add_node("summarize_exp", summarize_exp)

def route_experiences(state: ExpState):
    """Route chaque expérience vers le worker de résumé"""
    return [Send("summarize_exp", {"experience": exp}) for exp in state["experiences"]]

exp_graph.add_conditional_edges(START, route_experiences, ["summarize_exp"])
exp_graph.add_edge("summarize_exp", END)
# Compilation du workflow
compiled_exp_graph = exp_graph.compile()

def summarize_exps(experiences: List[Experience]) -> List[Experience]:
    """
    Résume une liste d'expériences en utilisant le graphe de traitement.
    
    Args:
        experiences: Liste des expériences à traiter
        
    Returns:
        Liste des expériences enrichies avec leurs résumés
    """
    # Prépare l'état initial
    state = {
        "experiences": experiences,
        "experiences_refined": []
    }
    
    # Exécute le graphe
    result = compiled_exp_graph.invoke(state)
    
    # Retourne les expériences enrichies
    return result["experiences_refined"]
