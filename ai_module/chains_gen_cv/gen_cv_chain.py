from langgraph.graph import StateGraph, START, END
from typing import Dict, List
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from ai_module.llm_config import get_llm
from ai_module.lg_models import CVGenState, CVHead, CVExperience, CVEducation
import langdetect

##############################################################################
# 1. Définition des modèles de données
##############################################################################

class SkillsOutput(BaseModel):
    """Structure pour la sortie des compétences"""
    competences: Dict[str, List[str]] = Field(
        description="Dictionnaire des catégories de compétences avec leurs listes de compétences",
        default_factory=dict
    )

##############################################################################
# 2. Définition des noeuds du graphe
##############################################################################

def detect_language(state: CVGenState) -> dict:
    """Détecte la langue du CV."""
    detected_language = langdetect.detect(state.job_raw)
    return {"language_cv": detected_language}

def summarize_job(state: CVGenState) -> dict:
    """Résume la description du poste."""
    llm = get_llm()
    prompt = f"""
    Fait un résumé du poste en 100 mots maximum :
    {state.job_raw}
    """
    response = llm.invoke(prompt)
    return {"job_refined": response.content}

def process_experiences(state: CVGenState) -> dict:
    """Traite et résume les expériences."""
    llm = get_llm()
    processed_exps = []
    
    for exp in state.experiences:
        prompt = f"""
        Résume cette expérience professionnelle de manière concise et percutante.
        Titre: {exp.title_raw}
        Entreprise: {exp.company_raw}
        
        Format attendu:
        - Un titre raffiné (max 5 mots)
        - Un nom d'entreprise raffiné (max 3 mots)
        - Un résumé impactant (max 50 mots)
        """
        
        response = llm.invoke(prompt)
        
        # Mise à jour de l'expérience
        exp.title_refined = exp.title_raw  # À remplacer par le parsing de la réponse
        exp.company_refined = exp.company_raw  # À remplacer par le parsing de la réponse
        exp.summary = response.content
        processed_exps.append(exp)
    
    return {"experiences": processed_exps}

def process_education(state: CVGenState) -> dict:
    """Traite et résume les formations."""
    llm = get_llm()
    processed_edu = []
    
    for edu in state.education:
        prompt = f"""
        Résume cette formation de manière concise et percutante.
        Diplôme: {edu.degree_raw}
        Institution: {edu.institution_raw}
        
        Format attendu:
        - Un diplôme raffiné (max 5 mots)
        - Un nom d'institution raffiné (max 3 mots)
        - Un résumé impactant (max 50 mots)
        """
        
        response = llm.invoke(prompt)
        
        # Mise à jour de la formation
        edu.degree_refined = edu.degree_raw  # À remplacer par le parsing de la réponse
        edu.institution_refined = edu.institution_raw  # À remplacer par le parsing de la réponse
        edu.summary = response.content
        processed_edu.append(edu)
    
    return {"education": processed_edu}

def generate_title(state: CVGenState) -> dict:
    """Génère un titre professionnel adapté."""
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
    
    head = state.head
    head.title_generated = response.content.strip()
    
    return {"head": head}

def generate_skills(state: CVGenState) -> dict:
    """Génère une liste structurée de compétences."""
    llm = get_llm().with_structured_output(SkillsOutput)
    
    prompt = f"""Analyse les compétences brutes suivantes et la fiche de poste pour générer une liste structurée de compétences pertinentes pour le CV.

Compétences brutes:
{state.skills_raw}

Fiche de poste:
{state.job_refined}

Instructions:
- Regroupe les compétences en 2-3 catégories maximum (ex: "Compétences techniques", "Outils & Technologies", etc.)
- Pour chaque catégorie, liste 4-6 compétences maximum
- Garde uniquement les compétences les plus pertinentes pour le poste
- Formule chaque compétence de manière concise (2-3 mots maximum)
- Exclus les langues étrangères qui sont traitées séparément
- Priorise les compétences techniques concrètes plutôt que les soft skills
"""

    response = llm.invoke(prompt)
    
    if not response.competences:
        return {"competences": {"Compétences techniques": ["À compléter"]}}
    
    return {"competences": response.competences}

def aggregate_results(state: CVGenState) -> dict:
    """Agrège tous les résultats en une sortie finale cohérente."""
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

    final_output += "\nCOMPÉTENCES\n-----------\n"
    for category, skills in state.competences.items():
        final_output += f"\n{category}:"
        final_output += f"\n- {', '.join(skills)}\n"

    return {"final_output": final_output}

##############################################################################
# 3. Construction du graphe
##############################################################################

def create_cv_chain():
    """Crée et retourne la chaîne de traitement du CV."""
    
    # Création du graphe
    chain = StateGraph(CVGenState)
    
    # Ajout des noeuds
    chain.add_node("detect_language", detect_language)
    chain.add_node("summarize_job", summarize_job)
    chain.add_node("process_experiences", process_experiences)
    chain.add_node("process_education", process_education)
    chain.add_node("generate_title", generate_title)
    chain.add_node("generate_skills", generate_skills)
    chain.add_node("aggregate_results", aggregate_results)
    
    # Configuration des transitions
    chain.add_edge(START, "detect_language")
    chain.add_edge(START, "summarize_job")
    chain.add_edge(START, "process_experiences")
    chain.add_edge(START, "process_education")
    
    chain.add_edge("summarize_job", "generate_title")
    chain.add_edge("summarize_job", "generate_skills")
    
    chain.add_edge("process_experiences", "aggregate_results")
    chain.add_edge("process_education", "aggregate_results")
    chain.add_edge("generate_title", "aggregate_results")
    chain.add_edge("generate_skills", "aggregate_results")
    chain.add_edge("detect_language", "aggregate_results")
    
    chain.add_edge("aggregate_results", END)
    
    return chain.compile()
