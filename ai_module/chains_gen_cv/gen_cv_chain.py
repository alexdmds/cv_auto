from typing import List, Optional, Dict
from typing_extensions import TypedDict
import operator
import langdetect

from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from langgraph.checkpoint.memory import MemorySaver
from ai_module.lg_models import CVGenState, CVExperience, CVEducation
from ai_module.llm_config import get_llm
from typing_extensions import Annotated
from pydantic import BaseModel, Field
##############################################################################
# 1. Modèles de données
##############################################################################

class PrivateExpState(TypedDict):
    """
    État privé pour le sous-graphe de traitement d'une seule expérience.
    """
    experiences_raw: List[CVExperience]
    experiences_with_summary: Annotated[List[CVExperience], operator.add]

class PrivateEduState(TypedDict):
    """
    État privé pour le sous-graphe de traitement d'une seule expérience.
    """
    educations_raw: List[CVEducation]
    educations_with_summary: Annotated[List[CVEducation], operator.add]

class PrivateSelectExpState(TypedDict):
    """
    État privé pour le sous-graphe de sélection des expériences.
    """
    experiences_to_select: List[CVExperience]
    job_summary_private_exp: str
    markdown_selection: str
    experiences_with_nb_bullets: List[CVExperience]
    experiences_with_bullets: Annotated[List[CVExperience], operator.add]

class PrivateSelectEduState(TypedDict):
    """
    État privé pour le sous-graphe de sélection des éducations.
    """
    educations_to_select: List[CVEducation]
    educations_with_nb_mots: List[CVEducation]
    job_summary_private_edu: str
    educations_with_description: Annotated[List[CVEducation], operator.add]

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

def summarize_edu_orch(state: CVGenState) -> PrivateEduState:
    """
    Orchestrateur pour résumer les éducations.
    On ne fait que renvoyer la liste des éducations pour le routage.
    """
    return {"educations_raw": state.education} 

def route_educations(state: PrivateEduState):
    """
    Route chaque éducation vers `edu_worker`.
    Chaque envoi est indépendant => parallélisme par éducation.
    """
    return[
        Send(
            "edu_worker",
            {"education_raw": edu}
        )
        for edu in state['educations_raw']
    ]

def edu_worker(state: PrivateEduState) -> dict:
    """
    Traite une seule éducation, génère un résumé via LLM.
    """
    llm = get_llm()
    edu = state["education_raw"]
    
    prompt = (
        f"Résume l'éducation suivante en 50 mots maximum:\n\n"
        f"Diplôme : {edu.degree_raw}\n"
        f"Ecole : {edu.institution_raw}\n"
        f"Lieu : {edu.location_raw}\n"
        f"Dates : {edu.dates_raw}\n"
        f"Description : {edu.description_raw}\n\n"
        f"Ne donne que le résumé final."
    )
    
    response = llm.invoke(prompt)

    updated_edu = edu
    updated_edu.summary = response.content
    
    return {"educations_with_summary": [updated_edu]}

def synth_sumup_edu(state: PrivateEduState) -> dict:
    """
    Reçoit en entrée un champ `educations_with_summary`, qui est la concat
    de toutes les éducations résumées. On les range ensuite dans le champ
    `educations`.
    """
    return {
        "educations": state['educations_with_summary']
    }

def agg_sum(state: CVGenState) -> dict:
    """
    Agglomère les infos finales (langue détectée, job résumé, expériences résumées).
    Ici on ne fait qu'un simple "return", mais on pourrait formater la sortie.
    """
    return {
        "language_cv": state.language_cv,
        "job_refined": state.job_refined,
        "experiences": state.experiences,
    }


##############################################################################
# 2e partie du graphe
############################################################################## 

def select_exp(state: CVGenState) -> PrivateSelectExpState:
    """
    Sélectionne les expériences à inclure dans le CV et retourne un markdown avec les choix d'expériences.
    """
    llm = get_llm()
    
    experiences_text = "\n".join(
        f"- [ID: {exp.exp_id}] **{exp.title_refined}** chez **{exp.company_refined}** à **{exp.location_refined}** ({exp.dates_refined})\n  Résumé: {exp.summary}"
        for exp in state.experiences
    )
    
    prompt = (
        f"Voici les expériences professionnelles disponibles pour le CV:\n\n"
        f"{experiences_text}\n\n"
        f"Poste visé : {state.job_refined}\n\n"
        f"Veuillez sélectionner les expériences les plus pertinentes pour le poste visé, en étant sélectif car l'espace est limité. "
        f"Les expériences doivent être listées par ordre chronologique décroissant, sauf si un argument solide justifie un autre ordre. "
        f"Pour chaque expérience sélectionnée, mentionnez son ID."
    )
    
    response = llm.invoke(prompt)
    
    return {
        "experiences_to_select": state.experiences,
        "job_summary_private_exp": state.job_refined,
        "markdown_selection": response.content,
        "experiences_with_nb_bullets": [],  # Initialisé vide, sera rempli plus tard
        "experiences_with_bullets": []  # Initialisé vide, sera rempli plus tard
    }

def give_nb_bullets(state: PrivateSelectExpState) -> dict:
    """
    Donne le nombre de bullets à mettre dans chaque expérience.
    """

    class ExperienceWithNbBullets(BaseModel):
        """
        Expérience avec le nombre de bullets.
        """
        exp_id: str = Field(description="Identifiant unique de l'expérience")
        nb_bullets: int = Field(description="Nombre de bullets à mettre pour cette expérience")
        order: Optional[int] = Field(description="Ordre de l'expérience dans le CV", default=None)

    class OutputBullets(BaseModel):
        """
        Sortie de la LLM pour le nombre de bullets à mettre dans chaque expérience.
        """
        experiences: List[ExperienceWithNbBullets]

    llm = get_llm().with_structured_output(OutputBullets)
    
    prompt = (
        f"Voici le choix des expériences pour le CV:\n\n"
        f"{state['markdown_selection']}\n\n"
        f"Le CV total doit comporter exactement 12 bullets répartis entre les expériences sélectionnées.\n"
        f"Si une expérience a un poids trop faible, préférez la mettre à 0 plutôt que de lui attribuer seulement 1 bullet.\n"
        f"Veuillez donner l'ordre et le nombre de bullets à mettre pour chaque expérience en fonction de ce choix.\n"
        f"Pour chaque expérience, utilisez son ID pour l'identifier."
    ) 
    response = llm.invoke(prompt)

    experiences_with_nb_bullets = []
    for exp in state['experiences_to_select']:
        matched = False
        for exp_with_bullets in response.experiences:
            if exp.exp_id == exp_with_bullets.exp_id:
                exp.nb_bullets = exp_with_bullets.nb_bullets
                exp.order = exp_with_bullets.order
                experiences_with_nb_bullets.append(exp)
                matched = True
                break
        if not matched:
            exp.nb_bullets = 0
            exp.order = None
            experiences_with_nb_bullets.append(exp)
    
    return {
        "experiences_with_nb_bullets": experiences_with_nb_bullets,
    }

def route_bullets(state: PrivateSelectExpState) -> dict:
    """
    Route chaque expérience vers `give_bullets`.
    On ne route pas les expériences ayant nb_bullets égal à 0.
    """
    return [
        Send("write_bullets", {
            "experience_with_nb_bullets": exp,
            "job_summary_private_exp": state['job_summary_private_exp']
        })
        for exp in state['experiences_with_nb_bullets'] if exp.nb_bullets > 0
    ]

def write_bullets(state: PrivateSelectExpState) -> dict:
    """
    Donne les bullets à mettre dans une seule expérience et identifie chaque expérience retournée aux expériences de base.
    """
    llm = get_llm()
    
    class ExperienceWithBullets(BaseModel):
        """
        Expérience avec les bullets générées.
        """
        bullets: List[str] = Field(description="Liste des bullets pour cette expérience")

    llm = get_llm().with_structured_output(ExperienceWithBullets)
    
    exp = state['experience_with_nb_bullets']
    prompt = (
        f"Voici le résumé du poste et la description brute de l'expérience sélectionnée pour le CV:\n\n"
        f"Résumé du poste:\n{state['job_summary_private_exp']}\n\n"
        f"Titre: {exp.title_raw}\n"
        f"Entreprise: {exp.company_raw}\n"
        f"Description: {exp.description_raw}\n"
        f"Nombre de bullets: {exp.nb_bullets}\n\n"
        f"Veuillez générer les bullets pour cette expérience en fonction du nombre de bullets spécifié."
    )

    response = llm.invoke(prompt)

    exp.bullets = response.bullets
    return {
        "experiences_with_bullets": [exp],
    }

def synth_sumup_bullets(state: PrivateSelectExpState) -> dict:
    """
    Reçoit en entrée un champ `experiences_with_bullets`, qui est la concat
    de toutes les expériences avec les bullets générées. On les range ensuite dans le champ
    `experiences`.
    """
    return {
        "experiences": state['experiences_with_bullets']
    }

def select_edu_and_give_nb_mots(state: CVGenState) -> PrivateSelectEduState:
    """
    Sélectionne les éducations à inclure dans le CV et retourne un markdown avec les choix d'éducations.
    """
    llm = get_llm()
    
    educations_text = "\n".join(
        f"- [ID: {edu.edu_id}] **{edu.degree_refined}** à **{edu.institution_refined}** à **{edu.location_refined}** ({edu.dates_refined})\n  Résumé: {edu.summary}"
        for edu in state.education
    )
    
    prompt = (
        f"Voici les formations disponibles pour le CV:\n\n"
        f"{educations_text}\n\n"
        f"Poste visé : {state.job_refined}\n\n"
        f"Veuillez sélectionner les formations les plus pertinentes pour le poste visé, en attribuant un nb de mots et un ordre pour le CV final. "
        f"Si une formation n'est pas pertinente, attribuez-lui 0 mots et une place 'null' sur le CV. Pour chaque formation sélectionnée, mentionnez son ID."
    )

    class EduWithNbMots(BaseModel):
        """
        Éducation avec le nombre de mots à mettre dans chaque éducation.
        """
        edu_id: str = Field(description="Identifiant unique de l'éducation")
        nb_mots: int = Field(description="Nombre de mots à mettre pour cette éducation, entre 30 et 70. 0 si la formation n'est pas pertinente.")
        order: Optional[int] = Field(description="Ordre de l'éducation dans le CV, peut être null")

    class OutputEduWithNbMots(BaseModel):
        """
        Sortie de la LLM pour le nombre de mots à mettre dans chaque éducation.
        """
        education: List[EduWithNbMots]

    llm = get_llm().with_structured_output(OutputEduWithNbMots)

    response = llm.invoke(prompt)

    education_with_nb_mots = []
    for edu in state.education:
        for edu_with_nb_mots in response.education:
            if edu.edu_id == edu_with_nb_mots.edu_id:
                edu.nb_mots = edu_with_nb_mots.nb_mots
                edu.order = edu_with_nb_mots.order
                education_with_nb_mots.append(edu)
                break

    return {
        "educations_with_nb_mots": education_with_nb_mots,
        "job_summary_private_edu": state.job_refined
    }

def route_education(state: PrivateSelectEduState) -> dict:
    """
    Route chaque éducation vers `write_edu_description`.
    On ne route pas les edu ayant nb_mots égal à 0.
    """
    return [
        Send("write_edu_description", {
            "education_with_nb_mots": edu,
            "job_summary_private_edu": state['job_summary_private_edu']
        })
        for edu in state['educations_with_nb_mots'] if edu.nb_mots > 0
    ]

def write_edu_description(state: PrivateSelectEduState) -> dict:
    """
    Génère la description de l'éducation en fonction du résumé du poste et de la description brute de l'éducation et du nombre de mots à mettre.
    """
    llm = get_llm()

    edu = state['education_with_nb_mots']

    prompt = (
        f"Voici le résumé du poste et la description brute de l'éducation sélectionnée pour le CV:\n\n"
        f"Résumé du poste:\n{state['job_summary_private_edu']}\n\n"
        f"Description: {edu.description_raw}\n"
        f"Nombre de mots: {edu.nb_mots}\n\n"
        f"Veuillez générer la description de l'éducation pour le CV en fonction du nombre de mots spécifié. Donne uniquement la description, sans aucun commentaire."
    )

    response = llm.invoke(prompt)

    edu.description_generated = response.content
    return {
        "educations_with_description": [edu],
    }

def synth_sumup_edu_description(state: PrivateSelectEduState) -> dict:
    """
    Reçoit en entrée un champ `educations_with_description`, qui est la concat
    de toutes les éducations avec les descriptions générées. On les range ensuite dans le champ
    `education`.
    """
    return {
        "education": state['educations_with_description']
    }

def translate_and_harmonize_exp(state: CVGenState) -> dict:
    """
    Traduit et harmonise les expériences en fonction de la langue du CV.
    """

    class ExperienceWithTranslation(BaseModel):
        """
        Expérience avec la traduction et l'harmonisation.
        """
        exp_id: str = Field(description="Identifiant unique de l'expérience inchangé")
        title_refined: str = Field(description="Titre de l'expérience traduit et harmonisé, retourné dans la langue attendue")
        company_refined: str = Field(description="Entreprise de l'expérience traduit et harmonisé, retourné dans la langue attendue")
        location_refined: str = Field(description="Lieu de l'expérience traduit et harmonisé, retourné dans la langue attendue")
        dates_refined: str = Field(description="Dates de l'expérience traduit et harmonisé, retourné dans la langue attendue")
        bullets: List[str] = Field(description="Bullets de l'expérience traduits et harmonisés, retournés dans la langue attendue")
    class OutputTranslation(BaseModel):
        """
        Sortie de la LLM pour la traduction et l'harmonisation.
        """
        experiences: List[ExperienceWithTranslation]

    llm = get_llm(temperature=0.5).with_structured_output(OutputTranslation)

    experiences_text = "\n".join(
        f"- [ID: {exp.exp_id}] **{exp.title_raw}** chez **{exp.company_raw}** à **{exp.location_raw}** ({exp.dates_raw})\n"
        f"  Bullets:\n" + "\n".join(f"    - {bullet}" for bullet in exp.bullets)
        for exp in state.experiences
    )

    prompt = (
        f"Langue attendue: {state.language_cv}\n\n"
        f"Voici les expériences professionnelles disponibles pour le CV:\n\n"
        f"{experiences_text}\n\n"
        f"Veuillez traduire et harmoniser les expériences pour le CV en fonction de la langue du CV. "
        f"Il faut que tout soit retourné dans la langue attendue."
    )
    
    response = llm.invoke(prompt)

    experiences_with_translation = []
    for exp in state.experiences:
        for translated_exp in response.experiences:
            if exp.exp_id == translated_exp.exp_id:
                exp.title_refined = translated_exp.title_refined
                exp.company_refined = translated_exp.company_refined
                exp.location_refined = translated_exp.location_refined
                exp.dates_refined = translated_exp.dates_refined
                exp.bullets = translated_exp.bullets
                experiences_with_translation.append(exp)
                break

    return {
        "experiences": experiences_with_translation
    }

def translate_and_harmonize_edu(state: CVGenState) -> dict:
    """
    Traduit et harmonise les éducations en fonction de la langue du CV.
    """
    class EducationWithTranslation(BaseModel):
        """
        Éducation avec la traduction et l'harmonisation.
        """
        edu_id: str = Field(description="Identifiant unique de l'éducation inchangé")
        degree_refined: str = Field(description="Diplôme traduit et harmonisé, retourné dans la langue attendue")
        institution_refined: str = Field(description="Institution traduite et harmonisée, retournée dans la langue attendue")
        location_refined: str = Field(description="Lieu de l'éducation traduit et harmonisé, retourné dans la langue attendue")
        dates_refined: str = Field(description="Dates de l'éducation traduites et harmonisées, retournées dans la langue attendue")
        description_refined: str = Field(description="Description générée de l'éducation traduite et harmonisée, retournée dans la langue attendue")
    class OutputTranslation(BaseModel):
        """
        Sortie de la LLM pour la traduction et l'harmonisation.
        """
        educations: List[EducationWithTranslation]

    llm = get_llm(temperature=0.5).with_structured_output(OutputTranslation)

    educations_text = "\n".join(
        f"- [ID: {edu.edu_id}] **{edu.degree_raw}** à **{edu.institution_raw}** à **{edu.location_raw}** ({edu.dates_raw})\n  Description: {edu.description_generated}"
        for edu in state.education
    )

    prompt = (
        f"Langue attendue: {state.language_cv}\n\n"
        f"Voici les éducations disponibles pour le CV:\n\n"
        f"{educations_text}\n\n"
        f"Veuillez traduire et harmoniser les éducations pour le CV en fonction de la langue du CV. "
        f"Il faut que tout soit retourné dans la langue attendue."
    )
    
    response = llm.invoke(prompt)

    for edu in state.education:
        for translated_edu in response.educations:
            if edu.edu_id == translated_edu.edu_id:
                edu.degree_refined = translated_edu.degree_refined
                edu.institution_refined = translated_edu.institution_refined
                edu.location_refined = translated_edu.location_refined
                edu.dates_refined = translated_edu.dates_refined
                edu.description_refined = translated_edu.description_refined
                break

    return {
        "education": state.education
    }

def give_title(state: CVGenState) -> dict:
    """
    Génère un titre pour le CV adapté pour le candidat et la fiche de poste dans la bonne langue.
    """
    llm = get_llm(temperature=0.8)

    experiences_text = "\n".join(
        f"- Titre: {exp.title_refined}\n  Entreprise: {exp.company_refined}\n  Résumé: {exp.summary}\n"
        for exp in state.experiences
    )

    education_text = "\n".join(
        f"- Titre: {edu.degree_refined}\n  Institution: {edu.institution_refined}\n  Résumé: {edu.description_generated}\n"
        for edu in state.education
    )

    prompt = (
        f"Langue attendue: {state.language_cv}\n\n"
        f"Voici les informations sur le candidat:\n"
        f"Nom: {state.head.name}\n"
        f"Compétences: {state.skills_raw}\n"
        f"Langues: {state.langues_raw}\n"
        f"Centres d'intérêt: {state.hobbies_raw}\n\n"
        f"Expériences professionnelles:\n{experiences_text}\n"
        f"Formations:\n{education_text}\n"
        f"Voici la fiche de poste:\n{state.job_raw}\n\n"
        f"Veuillez générer un titre de 10 mots maximum pour le CV adapté pour le candidat et la fiche de poste dans la langue spécifiée. Il faut être adapté au poste mais rester fidèle au profil du candidat."
        f"Donner seulement le titre, sans aucun commentaire."
    )

    response = llm.invoke(prompt)

    state.head.title_refined = response.content

    return {
        "head": state.head
    }

def give_phone(state: CVGenState) -> dict:
    """
    Traduit le numéro de téléphone en fonction de la langue et le met en format international si nécessaire.
    """
    llm = get_llm(temperature=0.8)

    prompt = (
        f"Langue attendue: {state.language_cv}\n\n"
        f"Numéro de téléphone brut: {state.head.tel_raw}\n\n"
        f"Veuillez traduire le numéro de téléphone en fonction de la langue spécifiée et le mettre en format international si nécessaire."
        f"Donner seulement le numéro de téléphone, sans aucun commentaire."
    )

    response = llm.invoke(prompt)

    state.head.tel_refined = response.content

    return {
        "head": state.head
    }

def translate_sections(state: CVGenState) -> dict:
    """
    Traduit les titres des sections du CV en fonction de la langue spécifiée.
    """
    llm = get_llm(temperature=0.8)

    class SectionsOutput(BaseModel):
        """
        Sortie de la LLM pour les titres des sections du CV.
        """
        experience_section_name: str = Field(description="Titre de la section expérience professionnelle")
        skills_section_name: str = Field(description="Titre de la section compétences")
        education_section_name: str = Field(description="Titre de la section éducation")
        languages_section_name: str = Field(description="Titre de la section langues")
        hobbies_section_name: str = Field(description="Titre de la section centres d'intérêt")

    llm = llm.with_structured_output(SectionsOutput)

    prompt = (
        f"Langue attendue: {state.language_cv}\n\n"
        f"Voici les titres des sections du CV à traduire:\n"
        f"Expérience professionnelle: {state.sections['experience']}\n"
        f"Compétences: {state.sections['skills']}\n"
        f"Éducation: {state.sections['education']}\n"
        f"Langues: {state.sections['languages']}\n"
        f"Centres d'intérêt: {state.sections['hobbies']}\n\n"
        f"Veuillez traduire ces titres en fonction de la langue spécifiée."
    )

    response = llm.invoke(prompt)

    state.sections['experience'] = response.experience_section_name
    state.sections['skills'] = response.skills_section_name
    state.sections['education'] = response.education_section_name
    state.sections['languages'] = response.languages_section_name
    state.sections['hobbies'] = response.hobbies_section_name

    return {
        "sections": state.sections
    }

def translate_langues(state: CVGenState) -> dict:
    """
    Traduit la liste des langues à partir de la chaîne brute langues_raw en fonction de la langue spécifiée.
    """
    llm = get_llm(temperature=0.8)

    class LanguesOutput(BaseModel):
        """
        Sortie de la LLM pour les langues du CV.
        """
        langues: List[str] = Field(description="Liste des langues maîtrisées et leur niveau")

    llm = llm.with_structured_output(LanguesOutput)

    prompt = (
        f"Langue attendue: {state.language_cv}\n\n"
        f"Voici la description brute des langues à traduire:\n"
        f"{state.langues_raw}\n\n"
        f"Veuillez traduire et structurer cette description en fonction de la langue spécifiée."
    )

    response = llm.invoke(prompt)

    state.langues = response.langues

    return {
        "langues": state.langues
    }

def generate_hobbies_text(state: CVGenState) -> dict:
    """
    Génère un petit texte sur les hobbies pour le CV, dans la langue attendue pour le CV,
    en fonction de la fiche de poste et de hobbies_raw.
    """
    llm = get_llm(temperature=0.8)

    class HobbiesOutput(BaseModel):
        """
        Sortie de la LLM pour les hobbies du CV.
        """
        hobbies_text: str = Field(description="Texte généré pour les hobbies")

    llm = llm.with_structured_output(HobbiesOutput)

    prompt = (
        f"Langue attendue: {state.language_cv}\n\n"
        f"Voici la description brute des hobbies à traduire:\n"
        f"{state.hobbies_raw}\n\n"
        f"Voici la description du poste visé:\n"
        f"{state.job_raw}\n\n"
        f"Veuillez générer un petit texte sur les hobbies en fonction de la langue spécifiée et de la fiche de poste."
    )

    response = llm.invoke(prompt)

    state.hobbies_refined = response.hobbies_text

    return {
        "hobbies_refined": state.hobbies_refined
    }

def generate_skills_text(state: CVGenState) -> dict:
    """
    Génère un texte structuré sur les compétences pour le CV, dans la langue attendue pour le CV,
    en fonction de la fiche de poste, des compétences brutes, des expériences et de leurs résumés, 
    ainsi que des formations et de leurs résumés.
    """
    llm = get_llm(temperature=0.8)

    class SkillsOutput(BaseModel):
        """
        Sortie de la LLM pour les compétences du CV.
        """
        competences: Dict[str, List[str]] = Field(description="Compétences organisées par catégorie")

    llm = llm.with_structured_output(SkillsOutput)

    prompt = (
        f"Langue attendue: {state.language_cv}\n\n"
        f"Voici la description brute des compétences à traduire:\n"
        f"{state.skills_raw}\n\n"
        f"Voici la description du poste visé:\n"
        f"{state.job_raw}\n\n"
        f"Voici les expériences professionnelles et leurs résumés:\n"
        f"{[exp.summary for exp in state.experiences]}\n\n"
        f"Voici les formations académiques et leurs résumés:\n"
        f"{[edu.summary for edu in state.education]}\n\n"
        f"Veuillez générer un texte structuré sur les compétences en fonction de la langue spécifiée, de la fiche de poste, des compétences brutes, des expériences et de leurs résumés, ainsi que des formations et de leurs résumés."
    )

    response = llm.invoke(prompt)

    state.competences = response.competences

    return {
        "competences": state.competences
    }



def create_cv_chain() -> StateGraph:
    """
    Construit le graphe principal avec:
      - 3 nœuds en parallèle au départ : detect_language, summarize_job, summarize_exp_orch
      - route_experiences() pour router en parallèle vers le sous-graphe
      - synth_sumup_exp pour consolider
      - agg_sum pour la sortie finale
    """
    
    chain = StateGraph(CVGenState)
    
    # Ajout des nœuds principaux
    chain.add_node("detect_language", detect_language)
    chain.add_node("summarize_job", summarize_job)
    chain.add_node("summarize_exp_orch", summarize_exp_orch)
    chain.add_node("exp_worker", exp_worker)
    chain.add_node("synth_sumup_exp", synth_sumup_exp)
    chain.add_node("summarize_edu_orch", summarize_edu_orch)
    chain.add_node("edu_worker", edu_worker)
    chain.add_node("synth_sumup_edu", synth_sumup_edu)
    chain.add_node("agg_sum", agg_sum)

    chain.add_node("select_exp", select_exp)
    chain.add_node("give_nb_bullets", give_nb_bullets)
    chain.add_node("write_bullets", write_bullets)
    chain.add_node("synth_sumup_bullets", synth_sumup_bullets)

    chain.add_node("select_edu_and_give_nb_mots", select_edu_and_give_nb_mots)
    chain.add_node("write_edu_description", write_edu_description)
    chain.add_node("synth_sumup_edu_description", synth_sumup_edu_description)

    chain.add_node("translate_and_harmonize_exp", translate_and_harmonize_exp)
    chain.add_node("translate_and_harmonize_edu", translate_and_harmonize_edu)

    chain.add_node("translate_sections", translate_sections)
    chain.add_node("give_title", give_title)
    chain.add_node("give_phone", give_phone)

    chain.add_node("generate_hobbies_text", generate_hobbies_text)

    # 1) Au départ, on lance en parallèle ces trois nœuds
    chain.add_edge(START, "detect_language")
    chain.add_edge(START, "summarize_job")
    chain.add_edge(START, "summarize_exp_orch")
    chain.add_edge(START, "summarize_edu_orch")
    # 2) Orchestration des expériences vers le sous-graphe
    chain.add_conditional_edges(
        "summarize_exp_orch",
        route_experiences,
        ["exp_worker"]
    )
    chain.add_conditional_edges(
        "summarize_edu_orch",
        route_educations,
        ["edu_worker"]
    )
    # 3) Lorsque chaque sous-graphe se termine, on va vers synth_sumup_exp
    chain.add_edge("exp_worker", "synth_sumup_exp")
    chain.add_edge("edu_worker", "synth_sumup_edu")
    
    # 4) Quand detect_language, summarize_job et synth_sumup_exp sont terminés,
    #    on passe à l'agrégation finale (agg_sum)
    chain.add_edge(["detect_language", "summarize_job", "synth_sumup_exp", "synth_sumup_edu"], "agg_sum")
    
    # 5) 2e partie du graphe
    chain.add_edge("agg_sum", "select_exp")
    chain.add_edge("select_exp", "give_nb_bullets")

    chain.add_conditional_edges(
        "give_nb_bullets",
        route_bullets,
        ["write_bullets"]
    )

    chain.add_edge("write_bullets", "synth_sumup_bullets")

    chain.add_edge("agg_sum", "select_edu_and_give_nb_mots")
    chain.add_conditional_edges(
        "select_edu_and_give_nb_mots",
        route_education,
        ["write_edu_description"]
    )
    chain.add_edge("write_edu_description", "synth_sumup_edu_description")

    chain.add_edge("synth_sumup_edu_description", "translate_and_harmonize_edu")
    chain.add_edge("translate_and_harmonize_edu", END)

    chain.add_edge("synth_sumup_bullets", "translate_and_harmonize_exp")
    chain.add_edge("translate_and_harmonize_exp", END)

    chain.add_edge("agg_sum", "translate_sections")
    chain.add_edge("translate_sections", "give_title")
    chain.add_edge("give_title", "give_phone")
    chain.add_edge("give_phone", END)

    chain.add_edge("agg_sum", "generate_hobbies_text")
    chain.add_edge("generate_hobbies_text", END)


    return chain
