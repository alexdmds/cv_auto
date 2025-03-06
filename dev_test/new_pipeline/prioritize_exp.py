import operator
from typing import List, Dict
from typing_extensions import TypedDict, Annotated
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
)

##############################################################################
# 1. Définition des structures de données
##############################################################################

# Structures pour les réponses structurées du LLM
class WeightedExperience(BaseModel):
    title: str = Field(description="Titre exact de l'expérience à évaluer")
    weight: float = Field(description="Poids entre 0 et 1", ge=0, le=1)
    order: int = Field(description="Position dans le CV (commence à 1)", ge=1)

class WeightAssignment(BaseModel):
    experiences: List[WeightedExperience] = Field(
        description="Liste des expériences avec leurs poids et ordre",
        min_items=1
    )

class Experience(TypedDict):
    title_raw: str
    company_raw: str
    dates_raw: str
    description_raw: str
    sumup: str
    weight: float
    order: int
    nb_bullets: int
    bullets: List[str]

class State(TypedDict):
    job_summary: str
    experiences: Annotated[List[Experience], operator.add]
    choix_exp: str

class WorkerState(TypedDict):
    experience: Experience
    job_summary: str
    nb_bullets: int

# Modification des structures pour gérer les mises à jour concurrentes
class BulletState(TypedDict):
    job_summary: str
    experiences: Annotated[List[Experience], operator.add]

##############################################################################
# 2. Modèles pour les réponses structurées
##############################################################################

class ExperienceAllocation(BaseModel):
    title: str = Field(description="Titre exact de l'expérience")
    weight: float = Field(description="Poids entre 0 et 1", ge=0, le=1)
    order: int = Field(description="Position dans le CV", ge=1)
    nb_bullets: int = Field(description="Nombre de bullet points à générer", ge=0)

class AllocationPlan(BaseModel):
    experiences: List[ExperienceAllocation]

class BulletPoints(BaseModel):
    bullets: List[str] = Field(description="Liste des bullet points")

##############################################################################
# 3. Définition des noeuds du graphe
##############################################################################

def select_experiences_from_sumup(state: State) -> dict:
    """Première étape : Analyse initiale des expériences à partir des sumup."""
    prompt = f"""Tu es un expert en recrutement. Analyse ces expériences par rapport au poste visé.
    
    POSTE VISÉ :
    {state['job_summary']}
    
    EXPÉRIENCES DISPONIBLES :
    {[f"{exp['title_raw']} chez {exp['company_raw']} ({exp['dates_raw']}) : {exp['sumup']}" for exp in state['experiences']]}
    
    INSTRUCTIONS :
    1. Analyse la pertinence de chaque expérience pour le poste
    2. Propose une stratégie de priorisation
    3. Indique quelles expériences garder et leur importance relative
    
    FORMAT :
    1. Stratégie globale
    2. Pour chaque expérience :
       - Pertinence détaillée pour le poste
       - Recommandation de poids (0-1)
       - Justification
    """
    
    response = llm.invoke(prompt)
    return {"choix_exp": response.content}

def assign_weights_from_choix_exp(state: State) -> dict:
    """Deuxième étape : Distribution des poids et bullets basée sur choix_exp."""
    llm_structured = llm.with_structured_output(AllocationPlan)
    
    prompt = f"""Tu dois répartir 12 bullet points entre les expériences selon leur pertinence.
    
    ANALYSE PRÉCÉDENTE :
    {state['choix_exp']}
    
    EXPÉRIENCES À ÉVALUER :
    {[exp['title_raw'] for exp in state['experiences']]}
    
    RÈGLES :
    1. Total exact de 12 bullet points à répartir
    2. Chaque expérience retenue doit avoir au moins 1 bullet
    3. Les expériences peu pertinentes doivent être exclues (poids = 0)
    4. L'ordre doit être unique et commencer à 1
    """
    
    allocation = llm_structured.invoke(prompt)
    
    # Mise à jour des expériences
    updated_experiences = []
    for exp in state['experiences']:
        exp_copy = exp.copy()
        matched = False
        for alloc in allocation.experiences:
            if alloc.title == exp['title_raw']:
                exp_copy.update({
                    'weight': alloc.weight,
                    'order': alloc.order,
                    'nb_bullets': alloc.nb_bullets
                })
                matched = True
                break
        if not matched:
            exp_copy.update({
                'weight': 0,
                'order': len(state['experiences']) + 1,
                'nb_bullets': 0
            })
        updated_experiences.append(exp_copy)
    
    return {
        "job_summary": state["job_summary"],
        "experiences": updated_experiences
    }

def create_bullets_from_description(state: State) -> dict:
    """Troisième étape : Génération des bullets à partir de description_raw."""
    exp = state["experience"]
    if exp['nb_bullets'] == 0:
        return {"experiences": [{**exp, "bullets": []}]}
    
    llm_structured = llm.with_structured_output(BulletPoints)
    
    prompt = f"""Crée exactement {exp['nb_bullets']} bullet points percutants pour cette expérience.
    
    POSTE VISÉ :
    {state['job_summary']}
    
    EXPÉRIENCE DÉTAILLÉE :
    {exp['description_raw']}
    """
    
    response = llm_structured.invoke(prompt)
    return {"experiences": [{**exp, "bullets": response.bullets[:exp['nb_bullets']]}]}

def synthesiseur(state: State, results: List[dict]) -> dict:
    """Quatrième étape : Synthèse finale des expériences et leurs bullets."""
    updated_experiences = []
    for result in results:
        updated_experiences.extend(result["experiences"])
    
    for exp in state["experiences"]:
        if exp["nb_bullets"] == 0:
            updated_experiences.append(exp)
    
    updated_experiences.sort(key=lambda x: x["order"])
    return {"experiences": updated_experiences}

##############################################################################
# 4. Construction du graphe selon le diagramme
##############################################################################

graph = StateGraph(State)

# Configuration des nœuds avec les nouveaux noms
graph.add_node("select_experiences", select_experiences_from_sumup)
graph.add_node("assign_weights", assign_weights_from_choix_exp)
graph.add_node("create_bullets", create_bullets_from_description)
graph.add_node("synthesiseur", synthesiseur)

# Configuration des transitions selon le diagramme
graph.add_edge(START, "select_experiences")
graph.add_edge("select_experiences", "assign_weights")

def route_to_bullets(state: State):
    """Route les expériences vers la création de bullets avec description_raw."""
    return [
        Send("create_bullets", {
            "experience": exp,
            "job_summary": state["job_summary"]
        })
        for exp in state["experiences"]
        if exp["nb_bullets"] > 0
    ]

# Configuration des transitions conditionnelles
graph.add_conditional_edges(
    "assign_weights",
    route_to_bullets,
    ["create_bullets"]
)

# Configuration de la synthèse finale
graph.add_edge("create_bullets", "synthesiseur")
graph.add_edge("synthesiseur", END)

# Compilation du workflow
compiled_graph = graph.compile()

##############################################################################
# 5. Test du workflow
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
                "title_raw": "Senior Developer",
                "company_raw": "TechCorp",
                "dates_raw": "2020-2023",
                "description_raw": "Direction d'une équipe de 5 développeurs. Architecture microservices. Stack Python/React.",
                "sumup": "Senior Developer - TechCorp",
                "weight": 0.0,  # Initialisation des champs requis
                "order": 0,     # Initialisation des champs requis
                "nb_bullets": 0, # Initialisation des champs requis
                "bullets": []    # Initialisation des champs requis
            },
            {
                "title_raw": "Développeur Full Stack",
                "company_raw": "StartupXYZ",
                "dates_raw": "2018-2020",
                "description_raw": "Développement frontend React. Backend Node.js. DevOps AWS.",
                "sumup": "Développeur Full Stack - StartupXYZ",
                "weight": 0.0,  # Initialisation des champs requis
                "order": 0,     # Initialisation des champs requis
                "nb_bullets": 0, # Initialisation des champs requis
                "bullets": []    # Initialisation des champs requis
            }
        ],
        "choix_exp": "",  # Ajout du champ requis
        "final_output": ""
    }

    # Invocation
    result = compiled_graph.invoke(initial_state)
    
    # Affichage des résultats pour test
    for exp in result["experiences"]:
        print(f"\n{exp['title_raw']} - {exp['company_raw']} ({exp['dates_raw']})")
        print(f"Poids: {exp['weight']:.2f} - Ordre: {exp['order']}")
        print("Bullets:")
        for bullet in exp["bullets"]:
            print(f"• {bullet}") 