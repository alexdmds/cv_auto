import operator
from typing import List, Dict
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from dev_test.models_langchain.llm_config import get_llm
import json
from pathlib import Path
import sys
from os.path import dirname, abspath

from summarize_exp import summarize_exps
from summarize_edu import compiled_edu_graph, summarize_edus
from data_structures import GlobalState

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

# Configuration des transitions pour le parallélisme
main_graph.add_edge(START, "summarize_job")
main_graph.add_edge(START, "process_experiences")
main_graph.add_edge(START, "process_education")
main_graph.add_edge("summarize_job", "aggregate_results")
main_graph.add_edge("process_experiences", "aggregate_results")
main_graph.add_edge("process_education", "aggregate_results")
main_graph.add_edge("aggregate_results", END)

# Compilation du workflow
compiled_main_graph = main_graph.compile()

##############################################################################
# 5. Exécution du workflow
##############################################################################

def convert_to_json_serializable(obj):
    """
    Convertit un objet en format JSON sérialisable.
    """
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    return obj

if __name__ == "__main__":
    import json
    from pathlib import Path
    from data_converter import convert_to_global_state

    # Utilisation de Path pour construire les chemins relatifs depuis ce fichier
    current_dir = Path(__file__).parent
    
    # Lecture du fichier JSON
    json_path = current_dir / "data_test.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Lecture de la fiche de poste
    fiche_poste_path = current_dir / "fiche_poste.txt"
    with open(fiche_poste_path, "r", encoding="utf-8") as f:
        job_summary = f.read()

    # Conversion des données en GlobalState
    global_state = convert_to_global_state(data)
    global_state.job_raw = job_summary  # Ajout du résumé du poste

    # Invocation
    result_state = compiled_main_graph.invoke(global_state)
    print(result_state)

    # Sauvegarde du résultat dans un fichier JSON
    output_path = current_dir / "result_state.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json_data = convert_to_json_serializable(dict(result_state))
        json.dump(json_data, f, ensure_ascii=False, indent=2)