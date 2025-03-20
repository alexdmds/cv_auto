from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import json


#Classes pour la génération globale du profile
class GeneralInfo(BaseModel):
    name: str = Field(default="", description="Nom complet du candidat")
    phone: str = Field(default="", description="Numéro de téléphone du candidat")
    email: str = Field(default="", description="Adresse email du candidat")
    general_title: str = Field(default="", description="Titre et description générale du profil")
    skills: str = Field(default="", description="Description détaillée des compétences techniques et professionnelles")
    langues: str = Field(default="", description="Description détaillée des langues parlées et niveaux")
    hobbies: str = Field(default="", description="Description détaillée des centres d'intérêt")

class GlobalExperience(BaseModel):
    intitule: str = Field(default="", description="Intitulé du poste")
    dates: str = Field(default="", description="Période d'emploi")
    etablissement: str = Field(default="", description="Nom de l'entreprise")
    lieu: str = Field(default="", description="Localisation")
    description: str = Field(default="", description="Description détaillée de l'expérience")

class GlobalEducation(BaseModel):
    intitule: str = Field(default="", description="Nom du diplôme")
    dates: str = Field(default="", description="Période de formation")
    etablissement: str = Field(default="", description="Nom de l'institution")
    lieu: str = Field(default="", description="Localisation")
    description: str = Field(default="", description="Description détaillée de la formation")

# Classes pour les listes (à utiliser avec JsonOutputParser)
class GlobalExperienceList(BaseModel):
    """Classe pour représenter une liste d'expériences pour le parsing JSON."""
    experiences: List[GlobalExperience] = Field(default_factory=list)

class GlobalEducationList(BaseModel):
    """Classe pour représenter une liste de formations pour le parsing JSON."""
    education: List[GlobalEducation] = Field(default_factory=list)

#Classes pour la génération du CV
class CVHead(BaseModel):
    name: str
    title_raw: str
    title_generated: str
    title_refined: str
    mail: str
    tel_raw: str
    tel_refined: str

class CVExperience(BaseModel):
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

class CVEducation(BaseModel):
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

class CVLanguage(BaseModel):
    language: str
    level: str

#Classes d'état pour le workflow
class ProfileState(BaseModel):
    experiences: List[GlobalExperience] = Field(default_factory=list, description="Liste des expériences professionnelles")
    education: List[GlobalEducation] = Field(default_factory=list, description="Liste des formations académiques")
    head: GeneralInfo = Field(default_factory=GeneralInfo, description="En-tête du profil")
    input_text: str = Field(default="", description="Texte brut d'entrée")

    @classmethod
    def from_input_text(cls, input_text: str) -> "ProfileState":
        """
        Crée une instance de ProfileState à partir d'un texte d'entrée.
        
        Args:
            input_text (str): Le texte brut d'entrée
            
        Returns:
            ProfileState: Une nouvelle instance de ProfileState
        """
        return cls(input_text=input_text)

    @classmethod
    def from_dict(cls, data: dict) -> "ProfileState":
        """
        Crée une instance de ProfileState à partir d'un dictionnaire.
        
        Args:
            data (dict): Dictionnaire contenant les données du profil
            
        Returns:
            ProfileState: Une nouvelle instance de ProfileState
        """
        # Initialiser les valeurs par défaut
        experiences = []
        education = []
        head = GeneralInfo()
        input_text = ""

        # Extraire les données du dictionnaire
        if "experiences" in data:
            experiences = [GlobalExperience(**exp) if isinstance(exp, dict) else exp for exp in data["experiences"]]
        
        if "education" in data:
            education = [GlobalEducation(**edu) if isinstance(edu, dict) else edu for edu in data["education"]]
        
        if "head" in data:
            head = GeneralInfo(**data["head"]) if isinstance(data["head"], dict) else data["head"]
        
        if "input_text" in data:
            input_text = data["input_text"]

        # Créer et retourner l'instance
        return cls(
            experiences=experiences,
            education=education,
            head=head,
            input_text=input_text
        )

class CVGenState(BaseModel):
    """État global du workflow."""
    head: CVHead
    sections: Dict[str, str]
    experiences: List[CVExperience]
    education: List[CVEducation]
    competences: Dict[str, List[str]]
    skills_raw: str
    langues: List[CVLanguage]
    hobbies_raw: str
    hobbies_refined: str
    job_raw: str
    job_refined: str

    @classmethod
    def from_json(cls, data: dict) -> "CVGenState":
        """
        Crée une instance de CVGenState à partir d'un dictionnaire JSON.
        
        Args:
            data: Dictionnaire contenant les données du CV
            
        Returns:
            Instance de CVGenState
        """
        # Conversion des sous-éléments
        head = CVHead(**data.get("head", {}))
        experiences = [CVExperience(**exp) for exp in data.get("experiences", [])]
        education = [CVEducation(**edu) for edu in data.get("education", [])]
        langues = [CVLanguage(**lang) for lang in data.get("langues", [])]
        
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
        
    @classmethod
    def from_user_document(cls, user_document, cv_name: str) -> Optional["CVGenState"]:
        """
        Crée une instance de CVGenState à partir d'un UserDocument et d'un nom de CV.
        
        Args:
            user_document: Instance de UserDocument contenant le profil et les CVs
            cv_name: Nom du CV à utiliser
            
        Returns:
            Instance de CVGenState ou None si le CV n'est pas trouvé
        """
        # Récupérer le CV spécifié
        cv = next((cv for cv in user_document.cvs if cv.cv_name == cv_name), None)
        if not cv:
            return None
            
        # Construire le Head à partir du profil et du CV
        profile = user_document.profile
        head_data = {
            "name": cv.cv_data.name or profile.head.name or "",
            "title_raw": cv.cv_data.title or profile.head.title or "",
            "title_generated": "",  # Champ à générer plus tard
            "title_refined": cv.cv_data.title or profile.head.title or "",
            "mail": cv.cv_data.mail or profile.head.mail or "",
            "tel_raw": cv.cv_data.phone or profile.head.phone or "",
            "tel_refined": cv.cv_data.phone or profile.head.phone or ""
        }
        head = CVHead(**head_data)
        
        # Construire les sections
        sections = {
            "experience": cv.cv_data.sections_name.experience_section_name,
            "education": cv.cv_data.sections_name.education_section_name,
            "skills": cv.cv_data.sections_name.skills_section_name,
            "languages": cv.cv_data.sections_name.languages_section_name,
            "hobbies": cv.cv_data.sections_name.hobbies_section_name
        }
        
        # Convertir les expériences
        experiences = []
        for idx, exp in enumerate(cv.cv_data.experiences or profile.experiences or []):
            # Choisir la source des données (CV ou profil)
            if hasattr(exp, 'company'):  # Expérience du CV
                bullets = exp.bullets if hasattr(exp, 'bullets') and exp.bullets else []
                exp_data = {
                    "title_raw": exp.title or "",
                    "title_refined": exp.title or "",
                    "company_raw": exp.company or "",
                    "company_refined": exp.company or "",
                    "location_raw": exp.location or "",
                    "location_refined": exp.location or "",
                    "dates_raw": exp.dates or "",
                    "dates_refined": exp.dates or "",
                    "description_raw": " ".join(bullets) if bullets else "",
                    "description_refined": " ".join(bullets) if bullets else "",
                    "summary": "",
                    "bullets": bullets,
                    "weight": 1.0,
                    "order": idx,
                    "nb_bullets": len(bullets)
                }
            else:  # Expérience du profil
                descriptions = exp.full_descriptions if hasattr(exp, 'full_descriptions') and exp.full_descriptions else []
                bullets = exp.bullets if hasattr(exp, 'bullets') and exp.bullets else []
                exp_data = {
                    "title_raw": exp.title or "",
                    "title_refined": exp.title or "",
                    "company_raw": exp.company or "",
                    "company_refined": exp.company or "",
                    "location_raw": exp.location or "",
                    "location_refined": exp.location or "",
                    "dates_raw": exp.dates or "",
                    "dates_refined": exp.dates or "",
                    "description_raw": " ".join(descriptions) if descriptions else " ".join(bullets) if bullets else "",
                    "description_refined": " ".join(descriptions) if descriptions else " ".join(bullets) if bullets else "",
                    "summary": "",
                    "bullets": bullets,
                    "weight": 1.0,
                    "order": idx,
                    "nb_bullets": len(bullets)
                }
            experiences.append(CVExperience(**exp_data))
        
        # Convertir les formations
        education_list = []
        for idx, edu in enumerate(cv.cv_data.educations or profile.educations or []):
            # Choisir la source des données (CV ou profil)
            if hasattr(edu, 'university'):  # Formation du CV
                edu_data = {
                    "degree_raw": edu.title or "",
                    "degree_refined": edu.title or "",
                    "institution_raw": edu.university or "",
                    "institution_refined": edu.university or "",
                    "location_raw": edu.location or "",
                    "location_refined": edu.location or "",
                    "dates_raw": edu.dates or "",
                    "dates_refined": edu.dates or "",
                    "description_raw": edu.description or "",
                    "description_generated": "",
                    "description_refined": edu.description or "",
                    "summary": "",
                    "weight": 1.0,
                    "order": idx,
                    "nb_mots": len(edu.description.split()) if edu.description else 0
                }
            else:  # Formation du profil
                description = edu.full_description or edu.description or ""
                edu_data = {
                    "degree_raw": edu.title or "",
                    "degree_refined": edu.title or "",
                    "institution_raw": edu.university or "",
                    "institution_refined": edu.university or "",
                    "location_raw": edu.location or "",
                    "location_refined": edu.location or "",
                    "dates_raw": edu.dates or "",
                    "dates_refined": edu.dates or "",
                    "description_raw": description,
                    "description_generated": "",
                    "description_refined": description,
                    "summary": "",
                    "weight": 1.0,
                    "order": idx,
                    "nb_mots": len(description.split()) if description else 0
                }
            education_list.append(CVEducation(**edu_data))
        
        # Convertir les compétences
        competences = {}
        skills_raw = ""
        if cv.cv_data.skills:
            for skill in cv.cv_data.skills:
                category = skill.category_name or "Général"
                skill_items = skill.skills.split(',') if skill.skills else []
                competences[category] = [item.strip() for item in skill_items]
                skills_raw += skill.skills + ", " if skill.skills else ""
        elif profile.skills:
            competences = profile.skills or {}
            skills_raw = ", ".join([", ".join(skills) for skills in profile.skills.values()]) if profile.skills else ""
            
        # Convertir les langues
        langues = []
        if cv.cv_data.languages:
            for lang in cv.cv_data.languages:
                langues.append(CVLanguage(language=lang.language or "", level=lang.level or ""))
        elif profile.languages:
            for lang in profile.languages:
                langues.append(CVLanguage(language=lang.get("language", ""), level=lang.get("level", "")))
        
        # Hobbies
        hobbies_raw = cv.cv_data.hobbies or profile.hobbies or ""
        
        # Construire l'instance GlobalState
        return cls(
            head=head,
            sections=sections,
            experiences=experiences,
            education=education_list,
            competences=competences,
            skills_raw=skills_raw.rstrip(", "),
            langues=langues,
            hobbies_raw=hobbies_raw,
            hobbies_refined=hobbies_raw,
            job_raw=cv.job_raw or "",
            job_refined=""
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
    exp: CVExperience
    job_summary: str
    choix_exp: str

class SelectEduState(BaseModel):
    edu: CVEducation
    job_summary: str
    choix_edu: str