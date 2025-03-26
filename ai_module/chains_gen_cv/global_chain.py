from langgraph.graph import StateGraph, START, END
from ai_module.llm_config import get_llm
import json
from pathlib import Path
import sys
from os.path import dirname, abspath
from pydantic import BaseModel, Field
from typing import Dict, List
import langdetect

from .summarize_exp import summarize_exps
from .summarize_edu import summarize_edus
from ai_module.lg_models import CVGenState
from .prioritize_edu import prioritize_edu
from .prioritize_exp import prioritize_exp
from langchain_core.messages import SystemMessage, HumanMessage
from .translate_cv import translate_cv
# Ajout du répertoire parent au PYTHONPATH
root_dir = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root_dir)

##############################################################################
# 1. Définition des noeuds du graphe
##############################################################################

def detect_language(state: CVGenState) -> dict:
    """
    Détecte la langue du CV.
    """

    detected_language = langdetect.detect(state.job_raw)
    return {"language_cv": detected_language}

def summarize_job(state: CVGenState) -> dict:
    """
    Résume la description du poste.
    """
    llm = get_llm()
    prompt = f"""
    Fait un résumé du poste en 100 mots maximum :
    {state.job_raw}
    """
    
    response = llm.invoke(prompt)
    return {"job_refined": response.content}

def process_experiences(state: CVGenState) -> dict:
    """
    Traite les expériences.
    """
    result = summarize_exps(state.experiences)
    return {"experiences": result}

def process_education(state: CVGenState) -> dict:
    """
    Traite les formations.
    """
    result = summarize_edus(state.education)
    return {"education": result}

def aggregate_results(state: CVGenState) -> dict:
    """
    Agrège tous les résultats en une sortie finale cohérente.
    """
    final_output = f"""
ANALYSE COMPLÈTE DU PROFIL

POSTE VISÉ
----------
{state.job_refined}

EXPÉRIENCES
----------
"""
    for exp in state.experiences:
        final_output += f"\n{exp.title_refined} - {exp.company_refined}"
        final_output += f"\n{exp.summary}\n"

    final_output += "\nFORMATION\n--------\n"
    for edu in state.education:
        final_output += f"\n{edu.degree_refined} - {edu.institution_refined}"
        final_output += f"\n{edu.summary}\n"

    return {"final_output": final_output}

def prioritize_experiences(state: CVGenState) -> dict:
    """
    Priorise les expériences.
    """
    result = prioritize_exp(state.job_refined, state.experiences)
    return {"experiences": result}

def prioritize_education(state: CVGenState) -> dict:
    """
    Priorise les formations.
    """
    result = prioritize_edu(state.job_refined, state.education)
    return {"education": result}

def generate_title(state: CVGenState) -> dict:
    """
    Génère un titre professionnel adapté en fonction de la fiche de poste.
    """
    llm = get_llm()
    
    prompt = f"""En te basant sur la fiche de poste suivante:
{state.job_refined}

Et le titre actuel du candidat:
{state.head.title_raw}

Génère un titre professionnel concis et percutant qui:
- Met en avant les compétences clés recherchées dans la fiche de poste
- Garde les éléments pertinents du titre actuel
- Est formulé de manière professionnelle
- Fait maximum 10 mots

Règles:
- Ne pas inclure le nom du candidat
- Ne pas inclure d'entreprises spécifiques
- Rester factuel et éviter les adjectifs superflus
- Se concentrer sur l'expertise technique principale
"""

    response = llm.invoke([
        SystemMessage(content="Tu es un expert RH qui optimise les titres professionnels pour les CV."),
        HumanMessage(content=prompt)
    ])
    
    state.head.title_generated = response.content.strip()
    
    return {"head": state.head}

class SkillsOutput(BaseModel):
    """Structure pour la sortie des compétences"""
    competences: Dict[str, List[str]] = Field(
        description="Dictionnaire des catégories de compétences avec leurs listes de compétences",
        default_factory=dict  # Valeur par défaut pour éviter l'erreur de validation
    )

def generate_skills(state: CVGenState) -> dict:
    """
    Génère une liste structurée de compétences à partir des compétences brutes et de la fiche de poste.
    """
    llm = get_llm().with_structured_output(SkillsOutput, method="function_calling")
    
    prompt = f"""Analyse les compétences brutes suivantes et la fiche de poste pour générer une liste structurée de compétences pertinentes pour le CV.

Compétences brutes:
{state.skills_raw}

Fiche de poste:
{state.job_refined}

Ta réponse doit être un objet JSON avec la structure suivante:
{{
  "competences": {{
    "Catégorie 1": ["Compétence 1", "Compétence 2", "Compétence 3"],
    "Catégorie 2": ["Compétence 4", "Compétence 5", "Compétence 6"]
  }}
}}

Instructions:
- Regroupe les compétences en 2-3 catégories maximum (ex: "Compétences techniques", "Outils & Technologies", etc.)
- Pour chaque catégorie, liste 4-6 compétences maximum
- Garde uniquement les compétences les plus pertinentes pour le poste
- Formule chaque compétence de manière concise (2-3 mots maximum)
- Exclus les langues étrangères qui sont traitées séparément
- Priorise les compétences techniques concrètes plutôt que les soft skills

Exemple de réponse correcte:
{{
  "competences": {{
    "Développement Web": ["React", "JavaScript", "HTML/CSS", "Node.js"],
    "DevOps": ["Docker", "CI/CD", "AWS", "Kubernetes"],
    "Outils": ["Git", "Jira", "VS Code", "Postman"]
  }}
}}
"""

    response = llm.invoke(prompt)
    
    # Si la réponse est vide, créer un dictionnaire par défaut
    if not response.competences:
        return {"competences": {"Compétences techniques": ["À compléter"]}}
    
    return {"competences": response.competences}

def translate_cv_node(state: CVGenState) -> dict:
    """
    Traduit le CV en fonction de la langue cible.
    Met à jour directement l'état du CV avec les traductions.
    
    Args:
        state: État actuel du CV
        
    Returns:
        dict: État mis à jour avec les traductions
    """
    # Appliquer la traduction et récupérer l'état mis à jour
    updated_state = translate_cv(state)
    
    # Retourner l'état complet pour mise à jour
    return updated_state.model_dump()

##############################################################################
# 2. Construction du graphe principal
##############################################################################

# Création du graphe
main_graph = StateGraph(CVGenState)

# Ajout des noeuds
main_graph.add_node("summarize_job", summarize_job)
main_graph.add_node("process_experiences", process_experiences)
main_graph.add_node("process_education", process_education)
main_graph.add_node("aggregate_results", aggregate_results)
main_graph.add_node("generate_title", generate_title)
main_graph.add_node("generate_skills", generate_skills)
main_graph.add_node("prioritize_experiences", prioritize_experiences)
main_graph.add_node("prioritize_education", prioritize_education)
main_graph.add_node("detect_language", detect_language)
main_graph.add_node("translate_cv_node", translate_cv_node)

# Configuration des transitions pour le parallélisme
main_graph.add_edge(START, "summarize_job")
main_graph.add_edge(START, "process_experiences")
main_graph.add_edge(START, "process_education")
main_graph.add_edge(START, "detect_language")

main_graph.add_edge("summarize_job", "aggregate_results")
main_graph.add_edge("process_experiences", "aggregate_results")
main_graph.add_edge("process_education", "aggregate_results")
main_graph.add_edge("aggregate_results", "generate_title")
main_graph.add_edge("aggregate_results", "generate_skills")
main_graph.add_edge("aggregate_results", "prioritize_experiences")
main_graph.add_edge("aggregate_results", "prioritize_education")

# Modification de la structure pour fusionner tous les résultats
def merge_results(state: CVGenState) -> dict:
    """
    Fusionne tous les résultats des différentes branches.
    """
    return state.model_dump()

main_graph.add_node("merge_results", merge_results)
main_graph.add_edge("prioritize_education", "merge_results")
main_graph.add_edge("prioritize_experiences", "merge_results")
main_graph.add_edge("generate_skills", "merge_results")
main_graph.add_edge("generate_title", "merge_results")

# Ajout des connexions pour la traduction
main_graph.add_edge("merge_results", "translate_cv_node")
main_graph.add_edge("detect_language", "translate_cv_node")
main_graph.add_edge("translate_cv_node", END)

# Compilation du workflow
compiled_gencv_graph = main_graph.compile()