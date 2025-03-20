import operator
from typing import List, Dict
from typing_extensions import TypedDict, Annotated
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from ai_module.llm_config import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from ai_module.lg_models import CVExperience

class State(TypedDict):
    job_summary: str
    markdown_choice: str
    experiences_raw: List[CVExperience]
    experiences_weighted: Annotated[List[CVExperience], operator.add]
    experience_with_nb_bullets: List[CVExperience]
    experiences_bullets: Annotated[List[CVExperience], operator.add]

class WorkerWeightState(TypedDict):
    experience: CVExperience
    markdown_choice: str

class WorkerBulletsState(TypedDict):
    experience: CVExperience
    job_summary: str

class PlanWeight(BaseModel):
    """Structure pour les poids et l'ordre d'une expérience"""
    order: int = Field(description="Ordre d'apparition dans le CV (1 = premier, null si non retenu)", default=None)
    weight: float = Field(description="Poids de l'expérience (0-1)")

def generate_markdown_choice(state: State) -> dict:
    """Génère un markdown de choix d'expériences à partir du résumé de poste et des expériences brutes"""
    llm = get_llm(model="gpt-4o")
    job_summary = state["job_summary"]
    experiences = state["experiences_raw"]
    
    # Prépare le prompt pour le LLM
    experiences_text = ""
    for i, exp in enumerate(experiences):
        experiences_text += f"\nExpérience {i+1}:\n"
        experiences_text += f"Titre: {exp.title_raw}\n"
        experiences_text += f"Entreprise: {exp.company_raw}\n"
        experiences_text += f"Lieu: {exp.location_raw}\n"
        experiences_text += f"Dates: {exp.dates_raw}\n"
        experiences_text += f"Résumé: {exp.summary}\n"

    prompt = f"""En te basant sur le résumé du poste suivant:
{job_summary}

Et les expériences suivantes:
{experiences_text}

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

def weight_experiences(state: WorkerWeightState) -> dict:
    """Poids les expériences en fonction du markdown de choix"""
    llm = get_llm().with_structured_output(PlanWeight)
    markdown = state["markdown_choice"]
    experience = state["experience"]
    
    prompt = f"""Analyse ce markdown de choix d'expériences et trouve l'expérience suivante:
Titre: {experience.title_raw}
Entreprise: {experience.company_raw}

Si cette expérience n'est pas mentionnée dans le markdown, réponds avec:
- order: null  
- weight: 0

Si elle est mentionnée, extrait simplement et exactement:
1. Le poids indiqué après "Poids:" dans le markdown
2. L'ordre indiqué après "Ordre:" dans le markdown

Ne fais aucun autre calcul ou raisonnement, copie simplement ces valeurs.

Voici le markdown à analyser:
{markdown}"""

    response = llm.invoke(prompt)
    
    experience.order = response.order
    experience.weight = response.weight
    
    return {"experiences_weighted": [experience]}

def collect_weighted_experiences(state: State) -> dict:
    """Collecte toutes les expériences pondérées et les transmet aux workers de génération de bullets"""
    # Filtre les expériences avec un poids > 0.1
    experiences = [exp for exp in state["experiences_weighted"] if exp.weight > 0.1]
    
    # Trie par ordre
    experiences = sorted(
        experiences,
        key=lambda x: x.order if x.order is not None else float('inf')
    )
    
    # Répartit les 12 bullets points proportionnellement aux poids
    total_weight = sum(exp.weight for exp in experiences)
    remaining_bullets = 12
    
    for exp in experiences:
        # Calcule le nombre de bullets proportionnel au poids
        bullets = int(round((exp.weight / total_weight) * 12))
        # Assure au moins 1 bullet si weight > 0.1
        bullets = max(1, bullets)
        # Ajuste pour ne pas dépasser 12 au total
        bullets = min(bullets, remaining_bullets)
        exp.nb_bullets = bullets
        remaining_bullets -= bullets
    
    # Si il reste des bullets, les ajoute aux expériences les plus importantes
    i = 0
    while remaining_bullets > 0 and i < len(experiences):
        experiences[i].nb_bullets += 1
        remaining_bullets -= 1
        i += 1
    
    return {
        "job_summary": state["job_summary"],
        "experience_with_nb_bullets": experiences
    }

def generate_bullets(state: WorkerBulletsState) -> dict:
    """Génère les bullet points pour une expérience donnée"""
    experience = state["experience"]
    llm = get_llm()
    job_summary = state["job_summary"]
    
    if not experience.order or experience.nb_bullets == 0:  # Si l'expérience n'est pas retenue ou nb_bullets = 0
        return {"experiences_bullets": [experience]}
        
    prompt = f"""
    Pour cette expérience professionnelle, génère exactement {experience.nb_bullets} points clés (bullet points) qui mettent en valeur les réalisations et compétences les plus importantes.
    
    Poste visé : {job_summary}
    
    Poste : {experience.title_raw}
    Entreprise : {experience.company_raw}
    Description complète : {experience.description_raw}

    Règles :
    - Commence chaque bullet point par un verbe d'action fort à la première personne
    - Mets l'accent sur les résultats quantifiables et l'impact UNIQUEMENT s'ils sont mentionnés dans la description
    - Sois TRÈS concis (maximum 100 caractères par bullet point)
    - Utilise un format cohérent
    - Retourne uniquement la liste des bullet points, un par ligne, commençant par •
    - Adapte les points clés pour montrer la pertinence par rapport au poste visé
    - Chaque bullet point doit tenir sur une seule ligne de CV
    - Évite les phrases complexes avec des subordonnées
    - Privilégie un format "Action + Résultat" court et direct
    - Supprime tout mot superflu qui n'apporte pas de valeur
    - Ne fais AUCUNE supposition ou invention - base-toi UNIQUEMENT sur les informations fournies dans la description
    - Si un chiffre ou un impact n'est pas explicitement mentionné dans la description, ne l'invente pas

    """
    
    response = llm.invoke(prompt)
    
    # Met à jour l'expérience avec les bullets générés
    experience.bullets = [
        bullet.strip().replace('• ', '') 
        for bullet in response.content.split('\n') 
        if bullet.strip() and bullet.strip().startswith('•')
    ]
    
    return {"experiences_bullets": [experience]}


# Construction du graphe
graph = StateGraph(State)

# Ajout des nœuds
graph.add_node("generate_markdown_choice", generate_markdown_choice)
graph.add_node("weight_experiences", weight_experiences)
graph.add_node("collect_weighted", collect_weighted_experiences)
graph.add_node("generate_bullets", generate_bullets)

# Configuration des transitions
graph.add_edge(START, "generate_markdown_choice")

def route_to_weight_workers(state: State):
    """Route chaque expérience vers un worker de pondération"""
    return [
        Send("weight_experiences", {
            "experience": experience,
            "markdown_choice": state["markdown_choice"]
        })
        for experience in state["experiences_raw"]
    ]

def route_to_bullet_workers(state: State):
    """Route chaque expérience pondérée vers un worker de génération de bullets"""
    return [
        Send("generate_bullets", {
            "experience": experience,
            "job_summary": state["job_summary"]
        })
        for experience in state["experience_with_nb_bullets"]
    ]

graph.add_conditional_edges(
    "generate_markdown_choice",
    route_to_weight_workers,
    ["weight_experiences"]
)

graph.add_edge("weight_experiences", "collect_weighted")

graph.add_conditional_edges(
    "collect_weighted",
    route_to_bullet_workers,
    ["generate_bullets"]
)

graph.add_edge("generate_bullets", END)

# Compilation
chain = graph.compile()

def prioritize_exp(job_summary: str, experiences: List[CVExperience]) -> List[CVExperience]:
    """
    Priorise et enrichit une liste d'expériences en fonction d'un résumé de poste.
    
    Args:
        job_summary: Description du poste visé
        experiences: Liste des expériences à traiter
        
    Returns:
        Liste des expériences enrichies et priorisées
    """
    # Exécution du workflow
    result = chain.invoke({
        "job_summary": job_summary,
        "experiences_raw": experiences,
        "experiences_bullets": [],
        "experiences_weighted": [],
        "markdown_choice": ""
    })
    
    # Tri des expériences par ordre
    sorted_experiences = sorted(
        result["experiences_bullets"],
        key=lambda x: x.order if x.order is not None else float('inf')
    )
    
    return sorted_experiences