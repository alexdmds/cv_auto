from typing import List, Dict, Optional, ClassVar
from pydantic import BaseModel
import json
class Head(BaseModel):
    name: str
    title_raw: str
    title_generated: str
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
    description_generated: str
    description_refined: str
    summary: str
    weight: float
    order: Optional[int]
    nb_mots: int

    def __init__(self, **data):
        # Initialise les champs refined avec des valeurs par défaut vides
        data.setdefault('degree_refined', '')
        data.setdefault('institution_refined', '')
        data.setdefault('location_refined', '')
        data.setdefault('dates_refined', '')
        data.setdefault('description_generated', '')
        data.setdefault('description_refined', '')
        data.setdefault('summary', '')
        data.setdefault('weight', 0.0)
        data.setdefault('order', None)
        data.setdefault('nb_mots', 0)  # Valeur par défaut pour nb_mots
        super().__init__(**data)

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
    skills_raw: str
    langues: List[Language]
    hobbies_raw: str
    hobbies_refined: str
    job_raw: str
    job_refined: str

    @classmethod
    def from_json(cls, data: dict) -> "GlobalState":
        """
        Crée une instance de GlobalState à partir d'un dictionnaire JSON.
        
        Args:
            data: Dictionnaire contenant les données du CV
            
        Returns:
            Instance de GlobalState
        """
        # Conversion des sous-éléments
        head = Head(**data.get("head", {}))
        experiences = [Experience(**exp) for exp in data.get("experiences", [])]
        education = [Education(**edu) for edu in data.get("education", [])]
        langues = [Language(**lang) for lang in data.get("langues", [])]
        
        # Construction de l'instance
        return cls(
            head=head,
            sections=data.get("sections", {}),
            experiences=experiences,
            education=education,
            competences=data.get("competences", {}),
            skills_raw=data.get("skills_raw", ""),
            langues=langues,
            hobbies_raw=data.get("hobbies_raw", ""),
            hobbies_refined=data.get("hobbies_refined", ""),
            job_raw=data.get("job_raw", ""),
            job_refined=data.get("job_refined", "")
        )

    def to_json(self, filepath: str) -> None:
        """
        Sauvegarde l'état global dans un fichier JSON.
        
        Args:
            filepath: Chemin du fichier de sortie
        """
        output_data = {
            "head": self.head.dict(),
            "sections": self.sections,
            "experiences": [exp.dict() for exp in self.experiences],
            "education": [edu.dict() for edu in self.education],
            "competences": self.competences,
            "skills_raw": self.skills_raw,
            "langues": [lang.dict() for lang in self.langues],
            "hobbies_raw": self.hobbies_raw,
            "hobbies_refined": self.hobbies_refined,
            "job_raw": self.job_raw,
            "job_refined": self.job_refined
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

class SelectExpState(BaseModel):
    exp: Experience
    job_summary: str
    choix_exp: str

class SelectEduState(BaseModel):
    edu: Education
    job_summary: str
    choix_edu: str