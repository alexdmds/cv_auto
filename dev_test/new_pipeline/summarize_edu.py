import operator
import os
from typing import List, Dict
from typing_extensions import TypedDict, Annotated

# LangGraph
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send

from langchain_openai import ChatOpenAI

from data_structures import Education
from data_converter import convert_to_global_state

# Chemin vers le fichier de données
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(CURRENT_DIR, "data_test.json")

llm = ChatOpenAI(
    model="gpt-4o-mini",
)

##############################################################################
# 1. Définition des structures de données (state principal, worker state)
##############################################################################

class EduState(TypedDict):
    education: List[Education]
    sumups: Annotated[List[str], operator.add]
    final_synthesis: str

class WorkerState(TypedDict):
    education: Education
    sumups: Annotated[List[str], operator.add]


##############################################################################
# 2. Définition des noeuds (fonctions) du graphe
##############################################################################

def summarize_edu(worker_state: WorkerState):
    """Worker : génère le résumé pour une formation."""
    edu = worker_state["education"]
    prompt = f"""
    Résume cette formation de façon concise :
    Diplôme : {edu.degree_raw}
    Établissement : {edu.institution_raw}
    Période : {edu.dates_raw}
    Description : {edu.description_raw}
    """
    response = llm.invoke(prompt)
    return {"sumups": [response.content]}

def synthesize(state: EduState):
    """Synthétise tous les résumés."""
    final_report = "Synthèse du parcours de formation :\n\n"
    for idx, sumup in enumerate(state["sumups"], 1):
        final_report += f"{idx}. {sumup}\n\n"
    return {"final_synthesis": final_report}


##############################################################################
# 3. Construction du graphe
##############################################################################

# On crée notre graphe
edu_graph = StateGraph(EduState)

# On ajoute nos noeuds
edu_graph.add_node("summarize_edu", summarize_edu)
edu_graph.add_node("synthesize", synthesize)

# 4. Définition des transitions
#    START -> summarize_edu (en parallèle, un worker par éducation)
#    summarize_edu -> synthesize
#    synthesize -> END
#
# On utilise Send() pour lancer un worker par item dans 'education'.

def route_education(state: EduState):
    """
    Crée un worker 'summarize_edu' pour chaque éducation.
    """
    return [Send("summarize_edu", {"education": edu}) for edu in state["education"]]

edu_graph.add_conditional_edges(START, route_education, ["summarize_edu"])
edu_graph.add_edge("summarize_edu", "synthesize")
edu_graph.add_edge("synthesize", END)

# Compilation du workflow
compiled_edu_graph = edu_graph.compile()

##############################################################################
# 5. Exécution du workflow
##############################################################################

if __name__ == "__main__":
    # Chargement et conversion des données de test
    import json
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Erreur : Impossible de trouver le fichier {DATA_FILE}")
        print(f"Dossier courant : {os.getcwd()}")
        exit(1)
    
    # Conversion en GlobalState
    global_state = convert_to_global_state(data)
    
    # Préparation de l'état initial pour le workflow
    initial_state = {
        "education": global_state.education,
        "sumups": [],
        "final_synthesis": ""
    }

    # Invocation
    result_state = compiled_edu_graph.invoke(initial_state)

    # Affichage du résultat
    print("=== RÉSUMÉS GÉNÉRÉS ===")
    for idx, summary in enumerate(result_state["sumups"], start=1):
        print(f"{idx}. {summary}\n")
        
    print("\n=== SYNTHÈSE FINALE ===")
    print(result_state["final_synthesis"])

    