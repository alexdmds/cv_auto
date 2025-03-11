import operator
from typing import List, Dict
from typing_extensions import TypedDict, Annotated
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from dev_test.models_langchain.llm_config import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from data_structures import Experience

class State(TypedDict):
    job_summary: str
    markdown_choice: str
    experiences_raw: List[Experience]
    experiences_weighted: Annotated[List[Experience], operator.add]
    experiences_bullets: Annotated[List[Experience], operator.add]

def generate_markdown_choice(state: State) -> dict:
    """Génère un markdown de choix d'expériences à partir du résumé de poste et des expériences brutes"""
    llm = get_llm()
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
Tu n'es pas obligé de choisir toutes les expériences.
Pour chaque expérience, attribue:
1. Un poids entre 0 et 1 (0 = non pertinent, 1 = très pertinent)
2. Un ordre d'apparition sur le CV (1 = première position, null si elle n'est pas choisie)

Réponds sous forme de markdown avec ce format:
# Analyse des Expériences

## Expérience 1
- Poids: [poids]
- Ordre: [ordre]
- Justification: [courte explication]

[etc pour chaque expérience]"""

    response = llm.invoke([
        SystemMessage(content="Tu es un expert en recrutement qui analyse la pertinence des expériences par rapport à un poste."),
        HumanMessage(content=prompt)
    ])

    # Met à jour les poids et ordres dans les objets Experience
    markdown = response.content
    
    return {"markdown_choice": markdown}