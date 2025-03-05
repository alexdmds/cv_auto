import operator
from typing import List
from typing_extensions import TypedDict, Annotated

# LangGraph
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
)

##############################################################################
# 1. Définition des structures de données (state principal, worker state)
##############################################################################

class Experience(TypedDict):
    titre: str
    dates: str
    entreprise: str
    lieu: str
    description_raw: str
    sumup: str  # Résumé généré pour cette expérience

class State(TypedDict):
    """État principal du workflow."""
    experiences: List[Experience]
    sumups: Annotated[List[str], operator.add]  # liste de résumés
    final_synthesis: str  # texte final agrégé

class WorkerState(TypedDict):
    """État transmis à chaque worker."""
    experience: Experience
    sumups: Annotated[List[str], operator.add]  # chaque worker ajoute son résumé

##############################################################################
# 2. Définition des noeuds (fonctions) du graphe
##############################################################################

def orchestrator(state: State):
    """
    Orchestrator : distribue les expériences aux workers.
    """
    # On ne modifie pas l'état principal ici
    return {}

def summarize_exp(worker_state: WorkerState):
    """
    Worker : génère le résumé pour une expérience donnée.
    """
    exp_data = worker_state["experience"]

    # Appel au LLM pour résumer l'expérience
    prompt = f"""
    Résume cette expérience professionnelle de façon concise et impactante :
    Poste : {exp_data['titre']}
    Période : {exp_data['dates']}
    Entreprise : {exp_data['entreprise']}
    Lieu : {exp_data['lieu']}
    Description : {exp_data['description_raw']}
    
    Mets en valeur :
    1. Les responsabilités clés
    2. Les réalisations concrètes
    3. Les compétences démontrées
    """
    
    response = llm.invoke(prompt)
    summary_text = response.content

    return {"sumups": [summary_text]}

def synthesize(state: State):
    """
    Synthétise tous les résumés en un texte cohérent.
    """
    all_sumups = state["sumups"]
    final_report = "Synthèse du parcours professionnel :\n\n"

    # Création d'une synthèse structurée
    for idx, sumup in enumerate(all_sumups, start=1):
        final_report += f"Expérience {idx}:\n{sumup}\n\n"

    return {"final_synthesis": final_report}

##############################################################################
# 3. Construction du graphe
##############################################################################

# Création du graphe
graph = StateGraph(State)

# Ajout des noeuds
graph.add_node("orchestrator", orchestrator)
graph.add_node("summarize_exp", summarize_exp)
graph.add_node("synthesize", synthesize)

# 4. Définition des transitions
def route_experiences(state: State):
    """
    Crée un worker 'summarize_exp' pour chaque expérience.
    """
    return [Send("summarize_exp", {"experience": exp}) for exp in state["experiences"]]

graph.add_edge(START, "orchestrator")
graph.add_conditional_edges("orchestrator", route_experiences, ["summarize_exp"])
graph.add_edge("summarize_exp", "synthesize")
graph.add_edge("synthesize", END)

# Compilation du workflow
compiled_graph = graph.compile()

##############################################################################
# 5. Exécution du workflow
##############################################################################

if __name__ == "__main__":
    # Exemple d'input : 2 expérience(s)
    initial_state = {
        "experiences": [
            {
                "titre": "Lead Developer",
                "dates": "2020 - 2023",
                "entreprise": "TechCorp",
                "lieu": "Paris",
                "description_raw": "Direction d'une équipe de 5 développeurs. Mise en place d'une architecture microservices. Amélioration de 40% des performances."
            },
            {
                "titre": "Développeur Full Stack",
                "dates": "2018 - 2020",
                "entreprise": "StartupXYZ",
                "lieu": "Lyon",
                "description_raw": "Développement d'une application web avec React et Node.js. Mise en place de CI/CD. Réduction de 50% du temps de déploiement."
            },
        ],
        "sumups": [],
        "final_synthesis": ""
    }

    # Invocation
    result_state = compiled_graph.invoke(initial_state)

    # Affichage du résultat
    print("=== RÉSUMÉS GÉNÉRÉS ===")
    for idx, summary in enumerate(result_state["sumups"], start=1):
        print(f"\nExpérience {idx}:")
        print(summary)
        
    print("\n=== SYNTHÈSE FINALE ===")
    print(result_state["final_synthesis"]) 