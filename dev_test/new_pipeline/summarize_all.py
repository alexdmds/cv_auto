from langgraph.graph import StateGraph, START, END
from dev_test.models_langchain.llm_config import get_llm
import json
from pathlib import Path
import sys
from os.path import dirname, abspath
from pydantic import BaseModel, Field
from typing import Dict, List
import os

from summarize_exp import summarize_exps
from summarize_edu import summarize_edus
from data_structures import GlobalState
from prioritize_edu import prioritize_edu
from prioritize_exp import prioritize_exp
from langchain_core.messages import SystemMessage, HumanMessage
# Ajout du répertoire parent au PYTHONPATH
root_dir = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root_dir)

##############################################################################
# 1. Définition des noeuds du graphe
##############################################################################

def summarize_job(state: GlobalState) -> dict:
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

def process_experiences(state: GlobalState) -> dict:
    """
    Traite les expériences.
    """
    result = summarize_exps(state.experiences)
    return {"experiences": result}

def process_education(state: GlobalState) -> dict:
    """
    Traite les formations.
    """
    result = summarize_edus(state.education)
    return {"education": result}

def aggregate_results(state: GlobalState) -> dict:
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

def prioritize_experiences(state: GlobalState) -> dict:
    """
    Priorise les expériences.
    """
    result = prioritize_exp(state.job_refined, state.experiences)
    return {"experiences": result}

def prioritize_education(state: GlobalState) -> dict:
    """
    Priorise les formations.
    """
    result = prioritize_edu(state.job_refined, state.education)
    return {"education": result}

def generate_title(state: GlobalState) -> dict:
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

def generate_skills(state: GlobalState) -> dict:
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

##############################################################################
# 2. Construction du graphe principal
##############################################################################

# Création du graphe
main_graph = StateGraph(GlobalState)

# Ajout des noeuds
main_graph.add_node("summarize_job", summarize_job)
main_graph.add_node("process_experiences", process_experiences)
main_graph.add_node("process_education", process_education)
main_graph.add_node("aggregate_results", aggregate_results)
main_graph.add_node("generate_title", generate_title)
main_graph.add_node("generate_skills", generate_skills)
main_graph.add_node("prioritize_experiences", prioritize_experiences)
main_graph.add_node("prioritize_education", prioritize_education)

# Configuration des transitions pour le parallélisme
main_graph.add_edge(START, "summarize_job")
main_graph.add_edge(START, "process_experiences")
main_graph.add_edge(START, "process_education")
main_graph.add_edge("summarize_job", "aggregate_results")
main_graph.add_edge("process_experiences", "aggregate_results")
main_graph.add_edge("process_education", "aggregate_results")
main_graph.add_edge("aggregate_results", "generate_title")
main_graph.add_edge("aggregate_results", "generate_skills")
main_graph.add_edge("aggregate_results", "prioritize_experiences")
main_graph.add_edge("aggregate_results", "prioritize_education")
main_graph.add_edge("prioritize_education", END)
main_graph.add_edge("prioritize_experiences", END)
main_graph.add_edge("generate_skills", END)
main_graph.add_edge("generate_title", END)

# Compilation du workflow
compiled_main_graph = main_graph.compile()

##############################################################################
# 3. Test du workflow
##############################################################################

if __name__ == "__main__":
    import os
    import json
    from data_structures import GlobalState
    from data_converter import convert_to_global_state

    # Obtenir le chemin absolu du répertoire du script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "data_test.json")
    output_path = os.path.join(script_dir, "output.json")
    job_path = os.path.join(script_dir, "poste_trading.txt")
    
    # Ouvrir le fichier en utilisant le chemin absolu
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Lire la fiche de poste
    with open(job_path, "r", encoding="utf-8") as f:
        job_raw = f.read()

    # Conversion en GlobalState
    initial_state = convert_to_global_state(data, job_raw)

    # Exécution du workflow
    result_dict = compiled_main_graph.invoke(initial_state)
    
    # Convertir le dictionnaire de résultats en objet GlobalState
    final_state = GlobalState(
        head=result_dict["head"],
        sections=initial_state.sections,  # Reprendre les sections d'origine
        experiences=result_dict["experiences"],
        education=result_dict["education"],
        competences=result_dict["competences"],
        skills_raw=initial_state.skills_raw,  # Reprendre les données brutes d'origine
        langues=initial_state.langues,  # Pas modifié par le workflow
        hobbies_raw=initial_state.hobbies_raw,
        hobbies_refined=initial_state.hobbies_refined,
        job_raw=initial_state.job_raw,
        job_refined=result_dict.get("job_refined", initial_state.job_refined)
    )

    # Sauvegarde dans un fichier JSON en utilisant la méthode to_json
    final_state.to_json(output_path)
    print(f"Résultats sauvegardés dans {output_path}")
