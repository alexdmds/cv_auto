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