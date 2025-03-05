import operator
from typing import List, Dict
from typing_extensions import TypedDict, Annotated

# LangGraph
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send

from langchain_openai import ChatOpenAI

from data_structures import Experience

llm = ChatOpenAI(
    model="gpt-4o-mini",
)

##############################################################################
# 1. Définition des structures de données (state principal, worker state)
##############################################################################

class ExpState(TypedDict):
    experiences: List[Experience]
    sumups: Annotated[List[str], operator.add]
    final_synthesis: str

class WorkerState(TypedDict):
    experience: Experience
    sumups: Annotated[List[str], operator.add]

##############################################################################
# 2. Définition des noeuds (fonctions) du graphe
##############################################################################

def summarize_exp(worker_state: WorkerState):
    """Worker : génère le résumé pour une expérience."""
    exp = worker_state["experience"]
    prompt = f"""
    Résume cette expérience professionnelle de façon concise :
    Poste : {exp['title_raw']}
    Entreprise : {exp['company_raw']}
    Période : {exp['dates_raw']}
    Description : {exp['description_raw']}
    """
    response = llm.invoke(prompt)
    return {"sumups": [response.content]}

def synthesize(state: ExpState):
    """Synthétise tous les résumés."""
    final_report = "Synthèse des expériences professionnelles :\n\n"
    for idx, sumup in enumerate(state["sumups"], 1):
        final_report += f"{idx}. {sumup}\n\n"
    return {"final_synthesis": final_report}

##############################################################################
# 3. Construction du graphe
##############################################################################

# Construction du graphe
exp_graph = StateGraph(ExpState)
exp_graph.add_node("summarize_exp", summarize_exp)
exp_graph.add_node("synthesize", synthesize)

def route_experiences(state: ExpState):
    return [Send("summarize_exp", {"experience": exp}) for exp in state["experiences"]]

exp_graph.add_conditional_edges(START, route_experiences, ["summarize_exp"])
exp_graph.add_edge("summarize_exp", "synthesize")
exp_graph.add_edge("synthesize", END)

# Compilation du workflow
compiled_exp_graph = exp_graph.compile()

##############################################################################
# 5. Exécution du workflow
##############################################################################

if __name__ == "__main__":
    # Exemple d'input : 2 expérience(s)
    initial_state = {
        "experiences": [
            {
                "title_raw": "Lead Developer",
                "dates_raw": "2020 - 2023",
                "company_raw": "TechCorp",
                "description_raw": "Direction d'une équipe de 5 développeurs. Mise en place d'une architecture microservices. Amélioration de 40% des performances."
            },
            {
                "title_raw": "Développeur Full Stack",
                "dates_raw": "2018 - 2020",
                "company_raw": "StartupXYZ",
                "description_raw": "Développement d'une application web avec React et Node.js. Mise en place de CI/CD. Réduction de 50% du temps de déploiement."
            },
        ],
        "sumups": [],
        "final_synthesis": ""
    }

    # Invocation
    result_state = compiled_exp_graph.invoke(initial_state)

    # Affichage du résultat
    print("=== RÉSUMÉS GÉNÉRÉS ===")
    for idx, summary in enumerate(result_state["sumups"], start=1):
        print(f"\nExpérience {idx}:")
        print(summary)
        
    print("\n=== SYNTHÈSE FINALE ===")
    print(result_state["final_synthesis"]) 