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
    """État global du workflow de génération de CV."""
    head: CVHead = Field(
        default_factory=lambda: CVHead(
            name="",
            title_raw="",
            title_generated="",
            title_refined="",
            mail="",
            tel_raw="",
            tel_refined=""
        ),
        description="En-tête du CV contenant les informations personnelles"
    )
    sections: Dict[str, str] = Field(
        default_factory=lambda: {
            "experience": "Expérience Professionnelle",
            "education": "Formation",
            "skills": "Compétences",
            "languages": "Langues",
            "hobbies": "Centres d'Intérêt"
        },
        description="Titres des sections du CV"
    )
    experiences: List[CVExperience] = Field(
        default_factory=list,
        description="Liste des expériences professionnelles"
    )
    education: List[CVEducation] = Field(
        default_factory=list,
        description="Liste des formations"
    )
    competences: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Compétences organisées par catégorie"
    )
    skills_raw: str = Field(
        default="",
        description="Compétences brutes non structurées"
    )
    langues: List[CVLanguage] = Field(
        default_factory=list,
        description="Liste des langues maîtrisées"
    )
    langues_raw: str = Field(
        default="",
        description="Langues brutes non structurées"
    )
    hobbies_raw: str = Field(
        default="",
        description="Centres d'intérêt bruts"
    )
    hobbies_refined: str = Field(
        default="",
        description="Centres d'intérêt raffinés et traduits"
    )
    job_raw: str = Field(
        default="",
        description="Description brute du poste visé"
    )
    job_refined: str = Field(
        default="",
        description="Description raffinée du poste visé"
    )
    language_cv: str = Field(
        default="",
        description="Langue cible du CV (fr, en, etc.)"
    )

    @classmethod
    def from_dict(cls, data: dict) -> "CVGenState":
        """
        Crée une instance de CVGenState à partir d'un dictionnaire.
        Utile pour convertir le résultat de invoke() en instance CVGenState.
        
        Args:
            data (dict): Dictionnaire contenant les données du CV
            
        Returns:
            CVGenState: Une nouvelle instance de CVGenState
        """
        # Initialiser les valeurs par défaut
        head = CVHead(**data.get("head", {})) if isinstance(data.get("head"), dict) else data.get("head", CVHead(
            name="",
            title_raw="",
            title_generated="",
            title_refined="",
            mail="",
            tel_raw="",
            tel_refined=""
        ))
        
        experiences = []
        if "experiences" in data:
            experiences = [
                CVExperience(**exp) if isinstance(exp, dict) else exp 
                for exp in data["experiences"]
            ]
        
        education = []
        if "education" in data:
            education = [
                CVEducation(**edu) if isinstance(edu, dict) else edu 
                for edu in data["education"]
            ]
        
        langues = []
        if "langues" in data:
            langues = [
                CVLanguage(**lang) if isinstance(lang, dict) else lang 
                for lang in data["langues"]
            ]

        # Créer et retourner l'instance
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
            job_refined=data.get("job_refined", ""),
            language_cv=data.get("language_cv", "")
        )

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
            job_refined=data.get("job_refined", ""),
            language_cv=data.get("language_cv", "")
        )
        
    @classmethod
    def from_user_document(cls, user_document, cv_name: str) -> Optional["CVGenState"]:
        """
        Crée une nouvelle instance de CVGenState à partir d'un UserDocument et d'un nom de CV.
        Cette méthode crée un nouveau CV en utilisant les données du profil et le job_raw du CV existant.
        
        Args:
            user_document: Instance de UserDocument contenant le profil et les CVs
            cv_name: Nom du CV à utiliser pour récupérer le job_raw
            
        Returns:
            Instance de CVGenState
        """
        profile = user_document.profile
        
        # Récupérer uniquement le job_raw du CV existant
        cv = next((cv for cv in user_document.cvs if cv.cv_name == cv_name), None)
        job_raw = cv.job_raw if cv and hasattr(cv, 'job_raw') else ""
        
        # Construire le Head à partir du profil
        head_data = {
            "name": profile.head.name or "",
            "title_raw": profile.head.title or "",
            "title_generated": "",  # Champ à générer plus tard
            "title_refined":  "",
            "mail": profile.head.mail or "",
            "tel_raw": profile.head.phone or "",
            "tel_refined":  ""
        }
        head = CVHead(**head_data)
        
        # Sections par défaut
        sections = {
            "experience": "Expérience Professionnelle",
            "education": "Formation",
            "skills": "Compétences",
            "languages": "Langues",
            "hobbies": "Centres d'Intérêt"
        }
        
        # Convertir les expériences
        experiences = []
        for exp in profile.experiences:
            exp_data = {
                "title_raw": exp.title or "",
                "title_refined": "",
                "company_raw": exp.company or "",
                "company_refined":  "",
                "location_raw": exp.location or "",
                "location_refined": "",
                "dates_raw": exp.dates or "",
                "dates_refined": "",
                "description_raw": exp.full_descriptions or "",
                "description_refined":  "",
                "summary": "",
                "bullets": [],
                "weight": 0.0,
                "order": 0,
                "nb_bullets": 0
            }
            experiences.append(CVExperience(**exp_data))
        
        # Convertir les formations
        education_list = []
        for edu in profile.educations:
            edu_data = {
                "degree_raw": edu.title or "",
                "degree_refined": "",
                "institution_raw": edu.university or "",
                "institution_refined": "",
                "location_raw": "",
                "location_refined":"",
                "dates_raw": edu.dates or "",
                "dates_refined":  "",
                "description_raw": edu.full_descriptions or "",
                "description_generated": "",
                "description_refined": "",
                "summary": "",
                "weight": 0.0,
                "order": 0,
                "nb_mots": 0
            }
            education_list.append(CVEducation(**edu_data))
        
        # Convertir les compétences
        competences =  {}
        skills_raw = profile.skills or ""
            
        # Convertir les langues
        langues = []
        langues_raw = profile.languages or ""
        # Hobbies
        hobbies_raw = profile.hobbies or ""
        
        # Construire l'instance GlobalState
        return cls(
            head=head,
            sections=sections,
            experiences=experiences,
            education=education_list,
            competences=competences,
            skills_raw=skills_raw.rstrip(", "),
            langues=langues,
            langues_raw=langues_raw,
            hobbies_raw=hobbies_raw,
            hobbies_refined=hobbies_raw,
            job_raw=job_raw,
            job_refined="",
            language_cv=""
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
            "job_refined": self.job_refined,
            "language_cv": self.language_cv
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
