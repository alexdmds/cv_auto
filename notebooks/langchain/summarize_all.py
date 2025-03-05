import operator
from typing import List, Dict
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from langchain_openai import ChatOpenAI

from summarize_exp import compiled_graph as exp_graph
from summarize_edu import compiled_graph as edu_graph
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
    Résume et structure la description du poste.
    """
    prompt = f"""
    Analyse cette description de poste et fournis une version structurée qui met en évidence :
    1. Les responsabilités principales
    2. Les compétences requises
    3. Les qualifications demandées
    4. Le contexte du poste
    
    Description originale :
    {state['job_raw']}
    """
    
    response = llm.invoke(prompt)
    return {"job_refined": response.content}

def process_experiences(state: GlobalState):
    """
    Traite et priorise les expériences via le graphe dédié.
    """
    prioritize_state = {
        "job_summary": state["job_refined"],
        "experiences": [
            {
                "titre": exp["title_raw"],
                "dates": exp["dates_raw"],
                "entreprise": exp["company_raw"],
                "lieu": exp["location_raw"],
                "description_raw": exp["description_raw"],
                "weight": 0,
                "bullets": [],
                "sumup": ""
            }
            for exp in state["experiences"]
        ],
        "final_output": ""
    }
    
    result = prioritize_graph.invoke(prioritize_state)
    
    updated_experiences = []
    for exp in state["experiences"]:
        matching_exp = next(
            (r for r in result["experiences"] if r["titre"] == exp["title_raw"]),
            None
        )
        
        if matching_exp:
            updated_exp = exp.copy()
            updated_exp["weight"] = matching_exp.get("weight", 0)
            updated_exp["bullets"] = matching_exp.get("bullets", [])
            updated_exp["order"] = len(updated_experiences)
            updated_experiences.append(updated_exp)
        else:
            updated_exp = exp.copy()
            updated_exp["weight"] = 0
            updated_exp["bullets"] = []
            updated_exp["order"] = len(updated_experiences)
            updated_experiences.append(updated_exp)
    
    return {"experiences": updated_experiences}

def process_education(state: GlobalState):
    """
    Traite les formations via le graphe dédié.
    """
    edu_state = {
        "educations": [
            {
                "titre": edu["degree_raw"],
                "dates": edu["dates_raw"],
                "etablissement": edu["institution_raw"],
                "lieu": edu["location_raw"],
                "description_raw": edu["description_raw"]
            }
            for edu in state["education"]
        ],
        "sumups": [],
        "final_synthesis": ""
    }
    
    result = edu_graph.invoke(edu_state)
    
    # Mettre à jour les formations avec les résultats
    updated_education = state["education"]
    for i, edu in enumerate(updated_education):
        edu["summary"] = result["sumups"][i] if i < len(result["sumups"]) else ""
        edu["order"] = i
    
    return {"education": updated_education}

def aggregate_results(state: GlobalState):
    """
    Agrège tous les résultats en une sortie finale cohérente.
    """
    # Trier les expériences par poids
    sorted_experiences = sorted(
        state["experiences"],
        key=lambda x: x.get("weight", 0),
        reverse=True
    )
    
    # Trier les formations par date
    sorted_education = sorted(
        state["education"],
        key=lambda x: x.get("dates_refined", ""),
        reverse=True
    )
    
    final_output = f"""
PROFIL COMPLET

{state['head']['name']}
{state['head']['title_refined']}
{state['head']['mail']} | {state['head']['tel_refined']}

ANALYSE DU POSTE VISÉ
--------------------
{state['job_refined']}

EXPÉRIENCES PROFESSIONNELLES
--------------------------
"""

    for exp in sorted_experiences:
        final_output += f"\n{exp['title_refined']} - {exp['company_refined']}"
        final_output += f"\n{exp['dates_refined']} | {exp['location_refined']}"
        for bullet in exp.get("bullets", []):
            final_output += f"\n• {bullet}"
        final_output += "\n"

    final_output += "\nFORMATION\n--------\n"
    for edu in sorted_education:
        final_output += f"\n{edu['degree_refined']} - {edu['institution_refined']}"
        final_output += f"\n{edu['dates_refined']} | {edu['location_refined']}"
        final_output += f"\n{edu['summary']}\n"

    if state["competences"]:
        final_output += "\nCOMPÉTENCES\n-----------\n"
        for category, skills in state["competences"].items():
            final_output += f"\n{category}: {', '.join(skills)}"

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