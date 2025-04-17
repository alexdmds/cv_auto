import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage
import json
import os
import tempfile
from datetime import datetime, UTC
from google.cloud.firestore_v1._helpers import DatetimeWithNanoseconds
from typing import Dict, List, Any, Optional, ClassVar, Type, TypeVar, Union
from pydantic import BaseModel, Field
from .base_firestore import FirestoreModel
from ai_module.lg_models import ProfileState
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from .cv_automation.gen_pdf.sections.header import create_header
from .cv_automation.gen_pdf.sections.education import create_education_section
from .cv_automation.gen_pdf.sections.experience import create_experience_section
from .cv_automation.gen_pdf.sections.skills import create_skills_section
from .cv_automation.gen_pdf.sections.hobbies import create_hobbies_section
from ai_module.lg_models import CVGenState
from PIL import Image
# Définir des types génériques pour les classes de modèle
T = TypeVar('T', bound='FirestoreModel')

# ====== Classes pour les nouveaux modèles Firestore ======

class EducationProfileNew(BaseModel):
    """Structure pour les données d'éducation dans un profil (nouvelle version)"""
    title: Optional[str] = None
    description: Optional[str] = None
    dates: Optional[str] = None
    university: Optional[str] = None

class ExperienceProfileNew(BaseModel):
    """Structure pour les données d'expérience dans un profil (nouvelle version)"""
    title: Optional[str] = None
    company: Optional[str] = None
    dates: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

class HeadProfileNew(BaseModel):
    """Structure pour les données d'en-tête dans un profil (nouvelle version)"""
    title: Optional[str] = None
    mail: Optional[str] = None
    linkedin_url: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None

class ProfileNew(BaseModel):
    """Structure complète d'un profil (nouvelle version)"""
    head: HeadProfileNew = Field(default_factory=HeadProfileNew)
    educations: List[EducationProfileNew] = Field(default_factory=list)
    experiences: List[ExperienceProfileNew] = Field(default_factory=list)
    languages: Optional[str] = None
    skills: Optional[str] = None
    hobbies: Optional[str] = None

class SectionNamesNew(BaseModel):
    """Noms des sections du CV (nouvelle version)"""
    experience_section_name: str = "Expérience Professionnelle"
    education_section_name: str = "Formation"
    skills_section_name: str = "Compétences"
    languages_section_name: str = "Langues"
    hobbies_section_name: str = "Centres d'intérêt"

class EducationCVNew(BaseModel):
    """Structure pour les données d'éducation dans un CV (nouvelle version)"""
    title: Optional[str] = None
    description: Optional[str] = None
    dates: Optional[str] = None
    university: Optional[str] = None
    location: Optional[str] = None

class ExperienceCVNew(BaseModel):
    """Structure pour les données d'expérience dans un CV (nouvelle version)"""
    title: Optional[str] = None
    company: Optional[str] = None
    dates: Optional[str] = None
    location: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

class SkillCVNew(BaseModel):
    """Structure pour les données de compétence dans un CV (nouvelle version)"""
    category_name: Optional[str] = None
    skills: List[str] = Field(default_factory=list)

class LanguageCVNew(BaseModel):
    """Structure pour les données de langue dans un CV (nouvelle version)"""
    language: Optional[str] = None
    level: Optional[str] = None

class CVDataNew(BaseModel):
    """Structure pour les données de CV (nouvelle version)"""
    name: Optional[str] = None
    title: Optional[str] = None
    mail: Optional[str] = None
    phone: Optional[str] = None
    lang_of_cv: str = "fr"
    section_names: SectionNamesNew = Field(default_factory=SectionNamesNew)
    experiences: List[ExperienceCVNew] = Field(default_factory=list)
    educations: List[EducationCVNew] = Field(default_factory=list)
    skills: List[SkillCVNew] = Field(default_factory=list)
    languages: List[LanguageCVNew] = Field(default_factory=list)
    hobbies: str = ""

    def to_pdf_data(self) -> dict:
        """Convertit les données du CV en format compatible avec le générateur de PDF"""
        # Convertir les compétences en dictionnaire
        skills_data = {}
        for skill in self.skills:
            if skill.category_name and skill.skills:
                skills_data[skill.category_name] = skill.skills

        # Convertir les langues en format attendu
        languages_data = []
        for lang in self.languages:
            if lang.language and lang.level:
                languages_data.append({
                    "nom": lang.language,
                    "niveau": lang.level
                })

        experiences_data = {
            "intitule_section": self.section_names.experience_section_name,
            "experiences": [
                {
                    "post": exp.title,
                    "company": exp.company,
                    "dates": exp.dates,
                    "location": exp.location,
                    "bullets": exp.bullets
                }
                for exp in self.experiences if exp.title
            ]
        }

        education_data = {
            "intitule_section": self.section_names.education_section_name,
            "educations": [
                {
                    "etablissement": edu.university,
                    "intitule": edu.title,
                    "dates": edu.dates,
                    "lieu": edu.location,
                    "description": edu.description
                }
                for edu in self.educations if edu.title
            ]
        }

        skills_section_data = {
            "intitule_section": self.section_names.skills_section_name,
            "skills": skills_data,
            "langues": languages_data
        }

        hobbies_data = {
            "intitule_section": self.section_names.hobbies_section_name,
            "hobbies": self.hobbies
        }

        return {
            "head": {
                "name": self.name,
                "general_title": self.title,
                "email": self.mail,
                "phone": self.phone
            },
            "experiences": experiences_data,
            "education": education_data,
            "skills": skills_section_data,
            "hobbies": hobbies_data
        }

    def generate_pdf(self, output_path: str, photo_path: Optional[str] = None, user_id: Optional[str] = None) -> str:
        """
        Génère un fichier PDF du CV.

        Args:
            output_path (str): Chemin où sauvegarder le PDF
            photo_path (Optional[str]): Chemin vers la photo de profil. Si None, tente de récupérer depuis Firebase Storage
            user_id (Optional[str]): ID de l'utilisateur pour récupérer la photo depuis Firebase Storage

        Returns:
            str: Chemin du fichier PDF généré
        """
        # Convertir les données au format attendu par le générateur de PDF
        data = self.to_pdf_data()

        # Gérer la photo
        if not photo_path and user_id:
            try:
                # Initialiser Firebase Storage
                bucket = storage.bucket("cv-generator-447314.firebasestorage.app")
                storage_path = f"{user_id}/profil/photo.jpg"
                blob = bucket.blob(storage_path)

                # Créer un fichier temporaire pour stocker la photo
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_photo:
                    blob.download_to_filename(temp_photo.name)
                    photo_path = temp_photo.name
            except Exception as e:
                print(f"Erreur lors de la récupération de la photo depuis Firebase Storage: {e}")
                # En cas d'erreur, utiliser la photo par défaut
                photo_path = None

        if not photo_path:
            ROOT_DIR = Path(__file__).resolve().parent
            photo_path = str(ROOT_DIR / "cv_automation" / "gen_pdf" / "sections" / "photo_default.jpg")
            if not Path(photo_path).exists():
                # Si la photo par défaut n'existe pas, on crée une image vide
                img = Image.new('RGB', (100, 100), color='white')
                photo_path = str(Path(output_path).parent / "photo_default.jpg")
                img.save(photo_path)
        
        # Créer le répertoire de sortie si nécessaire
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Initialiser le document PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1 * cm,
            leftMargin=1 * cm,
            topMargin=1 * cm,
            bottomMargin=1 * cm
        )
        elements = []

        # Générer les sections
        elements += create_header(data, photo_path)
        elements += create_experience_section(data)
        elements += create_education_section(data)
        elements += create_skills_section(data)
        elements += create_hobbies_section(data)

        # Générer le PDF
        doc.build(elements)

        # Nettoyer le fichier temporaire de la photo si nécessaire
        if user_id and photo_path and photo_path.endswith('.jpg') and 'temp' in photo_path.lower():
            try:
                os.unlink(photo_path)
            except Exception as e:
                print(f"Erreur lors de la suppression du fichier temporaire de la photo: {e}")

        return output_path

# ====== Documents Firestore ======

class CallDocument(FirestoreModel):
    """Modèle pour la collection 'calls'"""
    collection_name = "calls"
    
    user_id: str
    endpoint: Optional[str] = None
    call_time: datetime = Field(default_factory=datetime.now)
    usage_count: int = 1

    @classmethod
    def create_call(cls, user_id: str, endpoint: str) -> "CallDocument":
        """
        Crée un nouveau document d'appel dans Firestore.
        
        Args:
            user_id (str): ID de l'utilisateur
            endpoint (str): Nom de l'endpoint appelé
            
        Returns:
            CallDocument: Le document d'appel créé
        """
        call = cls(
            user_id=user_id,
            endpoint=endpoint
        )
        call.save()
        return call
    
class UsageDocument(FirestoreModel):
    """Modèle pour la collection 'usage'"""
    collection_name = "usage"
    
    user_id: str
    last_request_time: datetime = Field(default_factory=datetime.now)
    total_usage: int = 0

    @classmethod
    def get_or_create(cls, user_id: str) -> "UsageDocument":
        """
        Récupère ou crée un document d'utilisation pour un utilisateur.
        Utilise user_id comme ID du document Firestore.
        
        Args:
            user_id (str): ID de l'utilisateur
            
        Returns:
            UsageDocument: Le document d'utilisation
        """
        db = cls.get_db()
        doc_ref = db.collection(cls.collection_name).document(user_id)
        doc = doc_ref.get()
        
        if doc.exists:
            # Si le document existe, on récupère directement les données
            data = doc.to_dict()
            data['user_id'] = user_id  # S'assurer que l'ID est présent
            instance = cls(**data)
            instance.id = user_id  # Définir l'ID du document
            return instance
        else:
            # Si le document n'existe pas, on le crée avec les valeurs par défaut
            usage = cls(
                user_id=user_id,
                total_usage=0,
                last_request_time=datetime.now(UTC)
            )
            usage.id = user_id  # Définir l'ID du document
            usage.save()
            return usage
    
    def increment_usage(self, increment: int = 50000) -> None:
        """
        Incrémente le compteur d'utilisation et met à jour la date de dernière requête.
        
        Args:
            increment (int): Le nombre d'incréments à ajouter au compteur d'utilisation.
        """
        self.total_usage += increment
        self.last_request_time = datetime.now(UTC)
        self.save()

class ProfileDocument(FirestoreModel):
    """Modèle pour la collection 'profiles' dans Firestore"""
    collection_name = "profiles"
    id: str = Field(default="", description="ID du profil")
    educations: List[EducationProfileNew] = Field(default_factory=list)
    head: HeadProfileNew = Field(default_factory=HeadProfileNew)
    languages: Optional[str] = None
    skills: Optional[str] = None
    hobbies: Optional[str] = None
    experiences: List[ExperienceProfileNew] = Field(default_factory=list)

    @classmethod
    def from_firestore_id(cls, profile_id: str) -> Optional["ProfileDocument"]:
        """
        Construit un objet ProfileDocument directement à partir d'un ID Firestore.
        
        Args:
            profile_id (str): L'identifiant du document dans Firestore
            
        Returns:
            Optional[ProfileDocument]: L'objet ProfileDocument construit ou None si le document n'existe pas
        """
        db = cls.get_db()
        doc_ref = db.collection(cls.collection_name).document(profile_id)
        doc = doc_ref.get()
        
        if not doc.exists or not (raw_data := doc.to_dict()):
            return None
            
        try:
            instance = cls(**raw_data)
            instance.id = profile_id
            return instance
        except Exception as e:
            print(f"Erreur lors de la construction de l'objet ProfileDocument: {e}")
            return None

    def update_from_profile_state(self, profile_state: "ProfileState") -> "ProfileDocument":
        """
        Met à jour l'instance avec les données d'un ProfileState.
        
        Args:
            profile_state (ProfileState): L'état du profil à convertir
            
        Returns:
            ProfileDocument: L'instance mise à jour
        """
        # Mise à jour des informations de base
        self.head.name = profile_state.head.name
        self.head.title = profile_state.head.general_title
        self.head.mail = profile_state.head.email
        self.head.phone = profile_state.head.phone
        
        # Mise à jour des expériences
        self.experiences = [
            ExperienceProfileNew(
                title=exp.intitule,
                company=exp.etablissement,
                dates=exp.dates,
                location=exp.lieu,
                description=exp.description
            ) for exp in profile_state.experiences
        ]
        
        # Mise à jour des formations
        self.educations = [
            EducationProfileNew(
                title=edu.intitule,
                university=edu.etablissement,
                dates=edu.dates,
                description=edu.description
            ) for edu in profile_state.education
        ]
        
        # Mise à jour des compétences, langues et hobbies
        self.skills = profile_state.head.skills
        self.languages = profile_state.head.langues
        self.hobbies = profile_state.head.hobbies
        
        return self

    @classmethod
    def from_profile_state(cls, profile_state: "ProfileState", profile_id: str) -> "ProfileDocument":
        """
        Met à jour ou crée une instance de ProfileDocument à partir d'un ProfileState.
        
        Args:
            profile_state (ProfileState): L'état du profil à convertir
            profile_id (str): L'identifiant du profil
            
        Returns:
            ProfileDocument: L'instance de ProfileDocument mise à jour ou créée
        """
        # Récupérer l'instance existante ou en créer une nouvelle
        instance = cls.from_firestore_id(profile_id)
        if not instance:
            instance = cls(id=profile_id)
        
        # Mettre à jour l'instance avec les données du ProfileState
        return instance.update_from_profile_state(profile_state)

class CVDocument(FirestoreModel):
    """Modèle pour la collection 'cvs' dans Firestore"""
    collection_name = "cvs"
    id: str = Field(default="", description="ID du CV")
    user_id: str
    cv_url: Optional[str] = None
    job_raw: str = ""
    job_sumup: str = ""
    cv_name: str
    cv_data: CVDataNew = Field(default_factory=CVDataNew)

    @classmethod
    def from_firestore_id(cls, cv_id: str) -> Optional["CVDocument"]:
        """
        Construit un objet CVDocument directement à partir d'un ID Firestore.
        
        Args:
            cv_id (str): L'identifiant du document dans Firestore
            
        Returns:
            Optional[CVDocument]: L'objet CVDocument construit ou None si le document n'existe pas
        """
        db = cls.get_db()
        doc_ref = db.collection(cls.collection_name).document(cv_id)
        doc = doc_ref.get()
        
        if not doc.exists or not (raw_data := doc.to_dict()):
            return None
            
        try:
            instance = cls(**raw_data)
            instance.id = cv_id
            return instance
        except Exception as e:
            print(f"Erreur lors de la construction de l'objet CVDocument: {e}")
            return None

    def update_from_cv_state(self, cv_state: "CVGenState", save_to_firestore: bool = True) -> Optional[Dict[str, Any]]:
        """
        Met à jour un CV avec les données provenant d'un CVGenState
        
        Args:
            cv_state (CVGenState): État du CV contenant les nouvelles données
            save_to_firestore (bool): Si True, sauvegarde immédiatement les modifications dans Firestore
            
        Returns:
            Optional[Dict[str, Any]]: Informations sur la mise à jour
        """
        # Mise à jour des informations de base
        self.cv_data.name = cv_state.head.name
        self.cv_data.title = cv_state.head.title_refined
        self.cv_data.mail = cv_state.head.mail
        self.cv_data.phone = cv_state.head.tel_refined
        
        # Mise à jour des noms de sections
        self.cv_data.section_names.experience_section_name = cv_state.sections.get("experience", "Expérience Professionnelle")
        self.cv_data.section_names.education_section_name = cv_state.sections.get("education", "Formation")
        self.cv_data.section_names.skills_section_name = cv_state.sections.get("skills", "Compétences")
        self.cv_data.section_names.languages_section_name = cv_state.sections.get("languages", "Langues")
        self.cv_data.section_names.hobbies_section_name = cv_state.sections.get("hobbies", "Centres d'intérêt")
        
        # Mise à jour des expériences
        self.cv_data.experiences = [
            ExperienceCVNew(
                title=exp.title_refined,
                company=exp.company_refined,
                dates=exp.dates_refined,
                location=exp.location_refined,
                bullets=exp.bullets or []
            ) for exp in cv_state.experiences
        ]
        
        # Mise à jour des formations
        self.cv_data.educations = [
            EducationCVNew(
                title=edu.degree_refined,
                university=edu.institution_refined,
                dates=edu.dates_refined,
                location=edu.location_refined,
                description=edu.description_refined
            ) for edu in cv_state.education
        ]
        
        # Mise à jour des compétences
        self.cv_data.skills = [
            SkillCVNew(
                category_name=category,
                skills=skills
            ) for category, skills in cv_state.competences.items()
        ]
        
        # Mise à jour des langues
        self.cv_data.languages = [
            LanguageCVNew(
                language=lang.language,
                level=lang.level
            ) for lang in cv_state.langues
        ]
        
        # Mise à jour des centres d'intérêt et du poste
        self.cv_data.hobbies = cv_state.hobbies_refined
        self.job_raw = cv_state.job_raw
        self.job_sumup = cv_state.job_refined
        
        if save_to_firestore:
            self.save()
            
        return self._create_update_info()

    def _create_update_info(self) -> Dict[str, Any]:
        """Crée le dictionnaire d'informations sur la mise à jour"""
        return {
            "cv_name": self.cv_name,
            "updated": True,
            "name": self.cv_data.name,
            "title": self.cv_data.title,
            "experiences": len(self.cv_data.experiences),
            "educations": len(self.cv_data.educations),
            "skills": len(self.cv_data.skills),
            "languages": len(self.cv_data.languages),
            "hobbies_updated": bool(self.cv_data.hobbies),
            "job_updated": bool(self.job_raw)
        }

    @classmethod
    def from_cv_state(cls, cv_state: "CVGenState", user_id: str, cv_name: str) -> "CVDocument":
        """
        Crée une instance de CVDocument à partir d'un CVGenState.
        
        Args:
            cv_state (CVGenState): L'état du CV à convertir
            user_id (str): L'identifiant de l'utilisateur
            cv_name (str): Le nom du CV
            
        Returns:
            CVDocument: L'instance de CVDocument créée
        """
        # Créer l'instance de CVDocument
        instance = cls(
            user_id=user_id,
            cv_name=cv_name,
            job_raw=cv_state.job_raw,
            job_sumup=cv_state.job_refined,
            cv_data=CVDataNew()
        )
        
        # Mettre à jour les données du CV
        instance.update_from_cv_state(cv_state, save_to_firestore=False)
        
        return instance
