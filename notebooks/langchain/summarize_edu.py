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

class Education(TypedDict):
    titre: str
    dates: str
    etablissement: str
    lieu: str
    description_raw: str

class State(TypedDict):
    """État principal du workflow."""
    educations: List[Education]
    sumups: Annotated[List[str], operator.add]  # liste de résumés
    final_synthesis: str  # texte final agrégé

class WorkerState(TypedDict):
    """État transmis à chaque worker."""
    education: Education
    sumups: Annotated[List[str], operator.add]  # chaque worker ajoute son résumé


##############################################################################
# 2. Définition des noeuds (fonctions) du graphe
##############################################################################

def orchestrator(state: State):
    """
    Orchestrator : il ne fait que renvoyer un objet vide
    car nous allons "envoyer" chaque education à un worker via Send().
    """
    # Ici, vous pouvez éventuellement faire un pré-traitement.
    # On renvoie {} car on n'a pas de modification directe de l'état principal.
    return {}

def summarize_edu(worker_state: WorkerState):
    """
    Worker : génère le résumé pour une 'education' donnée.
    """
    education_data = worker_state["education"]

    # Appel au LLM GPT-4-mini pour résumer l'éducation
    prompt = f"""
    Résume cette expérience éducative de façon concise :
    Titre : {education_data['titre']}
    Dates : {education_data['dates']}
    Établissement : {education_data['etablissement']}
    Lieu : {education_data['lieu']}
    Description : {education_data['description_raw']}
    """
    
    response = llm.invoke(prompt)
    summary_text = response.content

    return {"sumups": [summary_text]}

def synthesize(state: State):
    """
    Synthétise tous les résumés en un seul texte final.
    """
    # state["sumups"] contient la liste de tous les résumés générés par les workers
    all_sumups = state["sumups"]
    final_report = "Synthèse de toutes les formations :\n\n"

    # On concatène simplement tous les résumés, vous pouvez personnaliser
    for idx, s in enumerate(all_sumups, start=1):
        final_report += f"{idx}. {s}\n\n"

    return {"final_synthesis": final_report}


##############################################################################
# 3. Construction du graphe
##############################################################################

# On crée notre graphe
graph = StateGraph(State)

# On ajoute nos noeuds
graph.add_node("orchestrator", orchestrator)
graph.add_node("summarize_edu", summarize_edu)
graph.add_node("synthesize", synthesize)

# 4. Définition des transitions
#    START -> orchestrator
#    orchestrator -> summarize_edu (en parallèle, un worker par éducation)
#    summarize_edu -> synthesize
#    synthesize -> END
#
# On utilise Send() pour lancer un worker par item dans 'educations'.

def route_educations(state: State):
    """
    Crée un worker 'summarize_edu' pour chaque éducation.
    """
    return [Send("summarize_edu", {"education": edu}) for edu in state["educations"]]

graph.add_edge(START, "orchestrator")
graph.add_conditional_edges("orchestrator", route_educations, ["summarize_edu"])
graph.add_edge("summarize_edu", "synthesize")
graph.add_edge("synthesize", END)

# Compilation du workflow
compiled_graph = graph.compile()

##############################################################################
# 5. Exécution du workflow
##############################################################################

if __name__ == "__main__":
    # Exemple d'input : 2 éducation(s)
    initial_state = {
        "educations": [
            {
                "titre": "Master en Informatique",
                "dates": "2018 - 2020",
                "etablissement": "Université de Paris",
                "lieu": "Paris",
                "description_raw": "Formation en intelligence artificielle..."
            },
            {
                "titre": "Licence en Mathématiques",
                "dates": "2015 - 2018",
                "etablissement": "Université de Lyon",
                "lieu": "Lyon",
                "description_raw": "Approfondissement en analyse, algèbre..."
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
        print(f"{idx}. {summary}")
        
    print("\n=== SYNTHÈSE FINALE ===")
    print(result_state["final_synthesis"])

    