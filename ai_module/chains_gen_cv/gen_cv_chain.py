from typing import List, Optional
from typing_extensions import TypedDict
import operator
import langdetect

from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from langgraph.checkpoint.memory import MemorySaver
from ai_module.lg_models import CVGenState, CVExperience
from ai_module.llm_config import get_llm
from typing_extensions import Annotated
##############################################################################
# 1. Modèles de données
##############################################################################

class PrivateExpState(TypedDict):
    """
    État privé pour le sous-graphe de traitement d'une seule expérience.
    """
    experiences_raw: List[CVExperience]
    experiences_with_summary: Annotated[List[CVExperience], operator.add]


##############################################################################
# 2. Fonctions "nœuds" du graphe principal
##############################################################################

def detect_language(state: CVGenState) -> dict:
    """Détecte la langue du CV."""
    detected_language = langdetect.detect(state.job_raw)
    return {"language_cv": detected_language}

def summarize_job(state: CVGenState) -> dict:
    """Résume la description du poste."""
    llm = get_llm()
    prompt = f"Fais un résumé du poste en 100 mots maximum:\n{state.job_raw}"
    response = llm.invoke(prompt)
    return {"job_refined": response.content}

def summarize_exp_orch(state: CVGenState) -> PrivateExpState:
    """
    Orchestrateur pour résumer les expériences.
    On ne fait que renvoyer la liste des expériences pour le routage.
    """
    return {"experiences_raw": state.experiences}

def route_experiences(state: PrivateExpState):
    """
    Route chaque expérience vers `exp_worker`.
    Chaque envoi est indépendant => parallélisme par expérience.
    """
    return[
        Send(
            # Nom du nœud (sous-graphe) vers lequel on envoie
            "exp_worker",
            # Payload qu'on lui transmet
            {"experience_raw": exp}
        )
        for exp in state['experiences_raw']
    ]

def synth_sumup_exp(state: PrivateExpState) -> dict:
    """
    Reçoit en entrée un champ `experiences_with_summary`, qui est la concat
    de toutes les expériences résumées. On les range ensuite dans le champ
    `experiences`.
    """
    # Dans le mode de routing en parallèle, `state["experiences_with_summary"]`
    # contient déjà la liste agrégée de toutes les expériences (gérée par langGraph).
    return {
        "experiences": state['experiences_with_summary']
    }

def agg_sum(state: CVGenState) -> dict:
    """
    Agglomère les infos finales (langue détectée, job résumé, expériences résumées).
    Ici on ne fait qu’un simple "return", mais on pourrait formater la sortie.
    """
    return {
        "language_cv": state.language_cv,
        "job_refined": state.job_refined,
        "experiences": state.experiences,
    }

##############################################################################
# 3. Fonctions "nœuds" du sous-graphe (pour UNE expérience)
##############################################################################

def exp_worker(state: PrivateExpState) -> dict:
    """
    Traite une seule expérience, génère un résumé via LLM.
    """
    llm = get_llm()
    exp = state["experience_raw"]
    
    prompt = (
        f"Résume l'expérience suivante en 50 mots maximum:\n\n"
        f"Poste : {exp.title_raw}\n"
        f"Entreprise : {exp.company_raw}\n"
        f"Lieu : {exp.location_raw}\n"
        f"Dates : {exp.dates_raw}\n"
        f"Description : {exp.description_raw}\n\n"
        f"Ne donne que le résumé final."
    )
    
    response = llm.invoke(prompt)
    
    # Mettre à jour le champ summary
    updated_exp = exp
    updated_exp.summary = response.content
    
    # Retourne la liste, même si c'est pour un seul élément,
    # car langGraph va agréger tous ces retours en un seul champ experiences_with_summary
    return {"experiences_with_summary": [updated_exp]}


##############################################################################
# 5. Construction et compilation du graphe principal
##############################################################################

def create_cv_chain():
    """
    Construit le graphe principal avec:
      - 3 nœuds en parallèle au départ : detect_language, summarize_job, summarize_exp_orch
      - route_experiences() pour router en parallèle vers le sous-graphe
      - synth_sumup_exp pour consolider
      - agg_sum pour la sortie finale
    """
    # Pour sauvegarder/reprendre l'état si besoin
    memory = MemorySaver()
    
    chain = StateGraph(CVGenState)
    
    # Ajout des nœuds principaux
    chain.add_node("detect_language", detect_language)
    chain.add_node("summarize_job", summarize_job)
    chain.add_node("summarize_exp_orch", summarize_exp_orch)
    chain.add_node("exp_worker", exp_worker)
    
    chain.add_node("synth_sumup_exp", synth_sumup_exp)
    chain.add_node("agg_sum", agg_sum)

    # 1) Au départ, on lance en parallèle ces trois nœuds
    chain.add_edge(START, "detect_language")
    chain.add_edge(START, "summarize_job")
    chain.add_edge(START, "summarize_exp_orch")
    
    # 2) Orchestration des expériences vers le sous-graphe
    chain.add_conditional_edges(
        "summarize_exp_orch",
        route_experiences,
        ["exp_worker"]
    )
    
    # 3) Lorsque chaque sous-graphe se termine, on va vers synth_sumup_exp
    chain.add_edge("exp_worker", "synth_sumup_exp")
    
    # 4) Quand detect_language, summarize_job et synth_sumup_exp sont terminés,
    #    on passe à l'agrégation finale (agg_sum)
    chain.add_edge(["detect_language", "summarize_job", "synth_sumup_exp"], "agg_sum")
    
    # 5) Fin
    chain.add_edge("agg_sum", END)
    
    return chain.compile(checkpointer=memory)
