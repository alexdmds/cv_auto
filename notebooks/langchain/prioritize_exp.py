import operator
from typing import List, Dict
from typing_extensions import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
)

##############################################################################
# 1. Définition des structures de données
##############################################################################

class Experience(TypedDict):
    titre: str
    dates: str
    entreprise: str
    lieu: str
    description_raw: str
    sumup: str
    weight: float  # Poids pour la priorisation
    bullets: List[str]  # Liste des bullet points

class State(TypedDict):
    """État principal du workflow."""
    job_summary: str  # Résumé du poste
    experiences: List[Experience]
    final_output: str

class WorkerState(TypedDict):
    """État transmis à chaque worker."""
    experience: Experience
    job_summary: str

##############################################################################
# 2. Définition des noeuds du graphe
##############################################################################

def select_experiences(state: State):
    """
    Sélectionne et prépare les expériences pour le traitement.
    """
    # On ne fait que passer l'état, la logique est dans l'orchestrateur
    return {}

def assign_weight_and_order(worker_state: WorkerState):
    """
    Évalue la pertinence de l'expérience par rapport au poste.
    """
    exp = worker_state["experience"]
    job = worker_state["job_summary"]
    
    prompt = f"""
    Évalue la pertinence de cette expérience professionnelle par rapport au poste.
    Attribue un score de 0 à 1 (1 étant le plus pertinent).

    Description du poste :
    {job}

    Expérience à évaluer :
    Titre : {exp['titre']}
    Entreprise : {exp['entreprise']}
    Description : {exp['description_raw']}

    Retourne uniquement le score numérique, par exemple : 0.85
    """
    
    response = llm.invoke(prompt)
    weight = float(response.content.strip())
    
    return {"experience": {**exp, "weight": weight}}

def create_bullets(worker_state: WorkerState):
    """
    Crée des bullet points détaillés pour l'expérience.
    """
    exp = worker_state["experience"]
    job = worker_state["job_summary"]
    
    prompt = f"""
    Crée 3-5 bullet points percutants pour cette expérience en mettant en avant
    les éléments les plus pertinents pour le poste visé.

    Poste visé (résumé) :
    {job}

    Expérience :
    Titre : {exp['titre']}
    Entreprise : {exp['entreprise']}
    Description : {exp['description_raw']}

    Format de réponse : une liste de bullet points, un par ligne, commençant par "•"
    """
    
    response = llm.invoke(prompt)
    bullets = [b.strip()[2:].strip() for b in response.content.split('\n') if b.strip().startswith('•')]
    
    return {"experience": {**exp, "bullets": bullets}}

def validate_output(state: State):
    """
    Vérifie que les sorties sont conformes aux attentes.
    """
    # Vérification basique que toutes les expériences ont des weights et bullets
    for exp in state["experiences"]:
        if "weight" not in exp or "bullets" not in exp:
            raise ValueError(f"Expérience {exp['titre']} manque weight ou bullets")
    return {}

def synthesize(state: State):
    """
    Crée la sortie finale avec les expériences priorisées et leurs bullets.
    """
    # Trier les expériences par poids
    sorted_experiences = sorted(
        state["experiences"],
        key=lambda x: x.get("weight", 0),
        reverse=True
    )
    
    # Créer la sortie formatée
    output = []
    for exp in sorted_experiences:
        output.append(f"\n{exp['titre']} - {exp['entreprise']} ({exp['dates']})")
        output.append(f"Pertinence: {exp['weight']:.2f}")
        for bullet in exp.get("bullets", []):
            output.append(f"• {bullet}")
        output.append("")
    
    return {"final_output": "\n".join(output)}

##############################################################################
# 3. Construction du graphe
##############################################################################

# Création du graphe
graph = StateGraph(State)

# Ajout des noeuds
graph.add_node("select_experiences", select_experiences)
graph.add_node("assign_weight", assign_weight_and_order)
graph.add_node("create_bullets", create_bullets)
graph.add_node("validate", validate_output)
graph.add_node("synthesize", synthesize)

# Définition des transitions pour le traitement parallèle
def route_to_weight(state: State):
    """Route chaque expérience vers l'évaluation du poids."""
    return [
        Send("assign_weight", {
            "experience": exp,
            "job_summary": state["job_summary"]
        })
        for exp in state["experiences"]
    ]

def route_to_bullets(state: State):
    """Route chaque expérience vers la création de bullets."""
    return [
        Send("create_bullets", {
            "experience": exp,
            "job_summary": state["job_summary"]
        })
        for exp in state["experiences"]
    ]

# Configuration des transitions
graph.add_edge(START, "select_experiences")
graph.add_conditional_edges(
    "select_experiences",
    route_to_weight,
    ["assign_weight"]
)
graph.add_edge("assign_weight", "validate")
graph.add_edge("validate", "create_bullets")
graph.add_edge("create_bullets", "synthesize")
graph.add_edge("synthesize", END)

# Compilation du workflow
compiled_graph = graph.compile()

##############################################################################
# 4. Exécution du workflow
##############################################################################

if __name__ == "__main__":
    # Exemple d'input
    initial_state = {
        "job_summary": """
        Lead Developer - Équipe Produit
        - Direction d'une équipe de développeurs
        - Architecture de solutions cloud
        - Développement full-stack (Python/React)
        """,
        "experiences": [
            {
                "titre": "Senior Developer",
                "dates": "2020-2023",
                "entreprise": "TechCorp",
                "lieu": "Paris",
                "description_raw": "Direction d'une équipe de 5 développeurs. Architecture microservices. Stack Python/React."
            },
            {
                "titre": "Développeur Full Stack",
                "dates": "2018-2020",
                "entreprise": "StartupXYZ",
                "lieu": "Lyon",
                "description_raw": "Développement frontend React. Backend Node.js. DevOps AWS."
            }
        ],
        "final_output": ""
    }

    # Invocation
    result = compiled_graph.invoke(initial_state)
    print(result["final_output"]) 