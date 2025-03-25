from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json
from ai_module.lg_models import CVGenState
from ai_module.llm_config import get_llm

class HeadTranslation(BaseModel):
    """Traduction des informations d'en-tête du CV."""
    
    title_refined: str = Field(..., description="Titre du CV traduit")
    tel_refined: str = Field(..., description="Numéro de téléphone formaté selon la langue cible")

class ExperienceTranslation(BaseModel):
    """Traduction d'une expérience professionnelle."""
    
    title_refined: str = Field(..., description="Titre du poste traduit")
    company_refined: str = Field(..., description="Nom de l'entreprise traduit ou adapté")
    location_refined: str = Field(..., description="Localisation traduite")
    dates_refined: str = Field(..., description="Dates formatées selon la langue cible")
    description_refined: str = Field(..., description="Description du poste traduite")
    bullets: List[str] = Field(default_factory=list, description="Points clés de l'expérience traduits")

class EducationTranslation(BaseModel):
    """Traduction d'une formation."""
    
    degree_refined: str = Field(..., description="Diplôme traduit")
    institution_refined: str = Field(..., description="Établissement traduit")
    location_refined: str = Field(..., description="Localisation traduite")
    dates_refined: str = Field(..., description="Dates formatées selon la langue cible")
    description_refined: str = Field(..., description="Description de la formation traduite")

class TranslationOutput(BaseModel):
    """Structure complète de la traduction du CV."""

    head: HeadTranslation = Field(..., description="Traduction de l'en-tête")
    experiences: List[ExperienceTranslation] = Field(default_factory=list, description="Liste des expériences traduites")
    education: List[EducationTranslation] = Field(default_factory=list, description="Liste des formations traduites")
    hobbies: str = Field(..., description="Centres d'intérêt traduits")
    language_target: Optional[str] = Field(description="Langue cible de la traduction")
    metadata: Optional[Dict[str, str]] = Field(description="Métadonnées additionnelles sur la traduction")


def translate_cv(state: CVGenState) -> CVGenState:
    """
    Traduit l'ensemble du CV dans la langue détectée (language_cv).
    Met à jour les champs 'refined' avec les traductions.
    
    Args:
        state: État actuel du CV à traduire
        
    Returns:
        CVGenState: État du CV avec les traductions mises à jour
    """

    llm = get_llm().with_structured_output(TranslationOutput)
    
    prompt = f"""Tu es un traducteur professionnel spécialisé dans les CV.
Je vais te donner un CV à traduire en {state.language_cv}.
Tu dois :
1. Garder un style professionnel adapté au marché du travail visé
2. Harmoniser les champs entre eux (dates, titres, entreprises, diplômes)
3. Adapter les expressions idiomatiques à la culture cible
4. Maintenir la cohérence terminologique
5. Respecter les conventions de format de la langue cible

Voici le CV à traduire :

# EN-TÊTE
Titre : {state.head.title_generated}
Téléphone : {state.head.tel_raw}

# EXPÉRIENCES PROFESSIONNELLES
{json.dumps([{
    'title': exp.title_raw,
    'company': exp.company_raw,
    'location': exp.location_raw,
    'dates': exp.dates_raw,
    'description': exp.description_raw,
    'bullets': exp.bullets
} for exp in state.experiences], ensure_ascii=False, indent=2)}

# FORMATIONS
{json.dumps([{
    'degree': edu.degree_raw,
    'institution': edu.institution_raw,
    'location': edu.location_raw,
    'dates': edu.dates_raw,
    'description': edu.description_generated
} for edu in state.education], ensure_ascii=False, indent=2)}

# COMPÉTENCES
{json.dumps(state.competences, ensure_ascii=False, indent=2)}

# CENTRES D'INTÉRÊT
{state.hobbies_raw}
"""

    # Obtenir la traduction structurée via TranslationOutput
    translation = llm.invoke(prompt)
    
    # Mettre à jour l'état avec les traductions
    state.head.title_refined = translation.head.title_refined
    state.head.tel_refined = translation.head.tel_refined
    
    for i, exp in enumerate(state.experiences):
        if i < len(translation.experiences):
            exp.title_refined = translation.experiences[i].title_refined
            exp.company_refined = translation.experiences[i].company_refined
            exp.location_refined = translation.experiences[i].location_refined
            exp.dates_refined = translation.experiences[i].dates_refined
            exp.description_refined = translation.experiences[i].description_refined
            exp.bullets = translation.experiences[i].bullets
    
    for i, edu in enumerate(state.education):
        if i < len(translation.education):
            edu.degree_refined = translation.education[i].degree_refined
            edu.institution_refined = translation.education[i].institution_refined
            edu.location_refined = translation.education[i].location_refined
            edu.dates_refined = translation.education[i].dates_refined
            edu.description_refined = translation.education[i].description_refined
    
    state.hobbies_refined = translation.hobbies
    
    return state