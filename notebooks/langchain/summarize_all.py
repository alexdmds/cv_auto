import operator
from typing import List, Dict
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from langchain_openai import ChatOpenAI

from summarize_exp import compiled_exp_graph
from summarize_edu import compiled_edu_graph
from prioritize_exp import compiled_graph as prioritize_graph
from data_structures import GlobalState, Experience, Education

llm = ChatOpenAI(
    model="gpt-4o-mini",
)

##############################################################################
# 1. Définition des noeuds du graphe
##############################################################################

def summarize_job(state: GlobalState):
    """
    Résume la description du poste.
    """
    prompt = f"""
    Analyse cette description de poste :
    {state['job_raw']}
    """
    
    response = llm.invoke(prompt)
    return {"job_refined": response.content}

def process_experiences(state: GlobalState):
    """
    Traite les expériences.
    """
    exp_state = {
        "experiences": state["experiences"],
        "sumups": [],
        "final_synthesis": ""
    }
    result = compiled_exp_graph.invoke(exp_state)
    
    # Mise à jour des expériences avec leurs résumés
    updated_experiences = state["experiences"]
    for exp, sumup in zip(updated_experiences, result["sumups"]):
        exp["summary"] = sumup
    
    return {"experiences": updated_experiences}

def process_education(state: GlobalState):
    """
    Traite les formations.
    """
    edu_state = {
        "education": state["education"],
        "sumups": [],
        "final_synthesis": ""
    }
    result = compiled_edu_graph.invoke(edu_state)
    
    # Mise à jour des formations avec leurs résumés
    updated_education = state["education"]
    for edu, sumup in zip(updated_education, result["sumups"]):
        edu["summary"] = sumup
    
    return {"education": updated_education}

def aggregate_results(state: GlobalState):
    """
    Agrège tous les résultats en une sortie finale cohérente.
    """
    final_output = f"""
ANALYSE COMPLÈTE DU PROFIL

POSTE VISÉ
----------
{state['job_refined']}

EXPÉRIENCES
----------
"""
    for exp in state["experiences"]:
        final_output += f"\n{exp['title_refined']} - {exp['company_refined']}"
        final_output += f"\n{exp['summary']}\n"

    final_output += "\nFORMATION\n--------\n"
    for edu in state["education"]:
        final_output += f"\n{edu['degree_refined']} - {edu['institution_refined']}"
        final_output += f"\n{edu['summary']}\n"

    return {"final_output": final_output}

##############################################################################
# 3. Construction du graphe principal
##############################################################################

# Création du graphe
main_graph = StateGraph(GlobalState)

# Ajout des noeuds
main_graph.add_node("summarize_job", summarize_job)
main_graph.add_node("process_experiences", process_experiences)
main_graph.add_node("process_education", process_education)
main_graph.add_node("aggregate_results", aggregate_results)

# Définition des transitions
main_graph.add_edge(START, "summarize_job")
main_graph.add_edge("summarize_job", "process_experiences")
main_graph.add_edge("process_experiences", "process_education")
main_graph.add_edge("process_education", "aggregate_results")
main_graph.add_edge("aggregate_results", END)

# Compilation du workflow
compiled_main_graph = main_graph.compile()

##############################################################################
# 5. Exécution du workflow
##############################################################################

if __name__ == "__main__":
    # Exemple d'input avec les noms de champs corrects selon GlobalState
    initial_state = {
        "head": {
            "name": "John Doe",
            "title_raw": "Développeur Senior",
            "title_refined": "Développeur Senior Full Stack",
            "mail": "john@example.com",
            "tel_raw": "0612345678",
            "tel_refined": "+33 6 12 34 56 78"
        },
        "experiences": [
            {
                "title_raw": "Lead Developer",
                "title_refined": "",
                "company_raw": "TechCorp",
                "company_refined": "",
                "location_raw": "Paris",
                "location_refined": "",
                "dates_raw": "2020 - 2023",
                "dates_refined": "",
                "description_raw": "Direction d'une équipe de 5 développeurs...",
                "description_refined": "",
                "summary": "",
                "bullets": [],
                "weight": 0,
                "order": None
            }
        ],
        "education": [
            {
                "degree_raw": "Master en Informatique",
                "degree_refined": "",
                "institution_raw": "Université de Paris",
                "institution_refined": "",
                "location_raw": "Paris",
                "location_refined": "",
                "dates_raw": "2018 - 2020",
                "dates_refined": "",
                "description_raw": "Formation en intelligence artificielle...",
                "description_refined": "",
                "summary": "",
                "weight": 0,
                "order": None
            }
        ],
        "sections": {
            "experiences": "Expériences Professionnelles",
            "education": "Formation",
            "competences": "Compétences",
            "hobbies": "Centres d'intérêt"
        },
        "competences": {},
        "langues": [],
        "hobbies_raw": "",
        "hobbies_refined": "",
        "job_raw": """
        Nous recherchons un Lead Developer expérimenté pour diriger notre équipe technique.
        Responsabilités : architecture logicielle, management d'équipe, développement full-stack.
        Requis : 5 ans d'expérience, maîtrise de Python et JavaScript, capacités de leadership.
        """,
        "job_refined": "",
        "final_output": ""
    }

    # Invocation
    result_state = compiled_main_graph.invoke(initial_state)
    print(result_state["final_output"]) 