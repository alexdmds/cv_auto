from typing import List, Dict, Optional
from pydantic import BaseModel

class Head(BaseModel):
    name: str
    title_raw: str
    title_refined: str
    mail: str
    tel_raw: str
    tel_refined: str

class Experience(BaseModel):
    title_raw: str
    title_refined: str
    company_raw: str
    company_refined: str
    location_raw: str
    location_refined: str
    dates_raw: str
    dates_refined: str
    description_raw: str
    description_refined: str
    summary: str
    bullets: List[str]
    weight: float
    order: Optional[int]
    nb_bullets: int

    def __init__(self, **data):
        # Initialise les champs refined avec des valeurs par défaut vides
        data.setdefault('title_refined', '')
        data.setdefault('company_refined', '')
        data.setdefault('location_refined', '')
        data.setdefault('dates_refined', '')
        data.setdefault('description_refined', '')
        data.setdefault('summary', '')
        data.setdefault('bullets', [])
        data.setdefault('weight', 0.0)
        data.setdefault('order', None)
        data.setdefault('nb_bullets', 0)
        super().__init__(**data)

class Education(BaseModel):
    degree_raw: str
    degree_refined: str
    institution_raw: str
    institution_refined: str
    location_raw: str
    location_refined: str
    dates_raw: str
    dates_refined: str
    description_raw: str
    description_refined: str
    summary: str
    weight: float
    order: Optional[int]
    nb_bullets: int

class Language(BaseModel):
    language: str
    level: str

class GlobalState(BaseModel):
    """État global du workflow."""
    head: Head
    sections: Dict[str, str]
    experiences: List[Experience]
    education: List[Education]
    competences: Dict[str, List[str]]
    langues: List[Language]
    hobbies_raw: str
    hobbies_refined: str
    job_raw: str
    job_refined: str

class SelectExpState(BaseModel):
    exp: Experience
    job_summary: str
    choix_exp: str

class SelectEduState(BaseModel):
    edu: Education
    job_summary: str
    choix_edu: str