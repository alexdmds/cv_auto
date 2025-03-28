import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import os
from datetime import datetime, UTC
from google.cloud.firestore_v1._helpers import DatetimeWithNanoseconds
from typing import Dict, List, Any, Optional, ClassVar, Type, TypeVar, Union
from pydantic import BaseModel, Field
from .base_firestore import FirestoreModel
from ai_module.lg_models import ProfileState
# Définir des types génériques pour les classes de modèle
T = TypeVar('T', bound='FirestoreModel')

# ====== Classes pour les CV ======

class SectionsName(BaseModel):
    """Noms des sections du CV"""
    experience_section_name: str = "Expérience Professionnelle"
    education_section_name: str = "Formation"
    skills_section_name: str = "Compétences"
    languages_section_name: str = "Langues"
    hobbies_section_name: str = "Centres d'intérêt"
    
class EducationCV(BaseModel):
    """Structure pour les données d'éducation dans un CV"""
    title: Optional[str] = None
    university: Optional[str] = None
    dates: Optional[str] = None  
    location: Optional[str] = None
    description: Optional[str] = None

class ExperienceCV(BaseModel):
    """Structure pour les données d'expérience dans un CV"""
    title: Optional[str] = None
    company: Optional[str] = None
    dates: Optional[str] = None
    location: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

class SkillCV(BaseModel):
    """Structure pour les données de compétence dans un CV"""
    category_name: Optional[str] = None
    skills: Optional[str] = None  # String avec compétences séparées par des virgules

class LanguageCV(BaseModel):
    """Structure pour les données de langue dans un CV"""
    language: Optional[str] = None
    level: Optional[str] = None

class CVData(BaseModel):
    """Structure pour les données de CV"""
    name: Optional[str] = None
    title: Optional[str] = None  
    mail: Optional[str] = None
    phone: Optional[str] = None
    lang_of_cv: str = "fr"
    sections_name: SectionsName = Field(default_factory=SectionsName)
    experiences: List[ExperienceCV] = Field(default_factory=list)
    educations: List[EducationCV] = Field(default_factory=list)
    skills: List[SkillCV] = Field(default_factory=list)
    languages: List[LanguageCV] = Field(default_factory=list)
    hobbies: str = ""

class CV(BaseModel):
    """Structure complète d'un CV"""
    cv_name: str
    job_raw: Optional[str] = None
    cv_data: CVData = Field(default_factory=CVData)

# ====== Classes pour le profil ======

class EducationProfile(BaseModel):
    """Structure pour les données d'éducation dans un profil"""
    title: Optional[str] = None
    full_description: Optional[str] = None
    dates: Optional[str] = None
    university: Optional[str] = None

class ExperienceProfile(BaseModel):
    """Structure pour les données d'expérience dans un profil"""
    title: Optional[str] = None
    company: Optional[str] = None
    dates: Optional[str] = None
    location: Optional[str] = None
    full_descriptions: Optional[str] = None

class HeadProfile(BaseModel):
    """Structure pour les données d'en-tête dans un profil"""
    title: Optional[str] = None
    mail: Optional[str] = None
    linkedin_url: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None

class Profile(BaseModel):
    """Structure complète d'un profil"""
    head: HeadProfile = Field(default_factory=HeadProfile)
    educations: List[EducationProfile] = Field(default_factory=list)
    experiences: List[ExperienceProfile] = Field(default_factory=list)
    languages: Optional[Union[str, List[Dict[str, str]]]] = None
    skills: Optional[Union[str, Dict[str, List[str]]]] = None
    hobbies: Optional[str] = None

# ====== Documents Firestore ======

class UserDocument(FirestoreModel):
    """Modèle pour la collection 'users'"""
    collection_name = "users"
    id: str = Field(default="", description="ID de l'utilisateur")
    cvs: List[CV] = Field(default_factory=list)
    profile: Profile = Field(default_factory=Profile)
    
    @classmethod
    def from_firestore_id(cls, user_id: str) -> Optional["UserDocument"]:
        """
        Construit un objet UserDocument directement à partir d'un ID Firestore.
        
        Args:
            user_id (str): L'identifiant du document dans Firestore
            
        Returns:
            Optional[UserDocument]: L'objet UserDocument construit ou None si le document n'existe pas
        """
        # Initialiser la connexion Firestore
        db = cls.get_db()
        doc_ref = db.collection(cls.collection_name).document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        # Récupérer et prétraiter les données brutes de Firestore
        raw_data = doc.to_dict()
        if not raw_data:
            return None
        
        # Créer une copie des données pour ne pas modifier l'original
        processed_data = dict(raw_data)
        
        # Traiter les données du profil si elles existent
        if "profile" in processed_data:
            profile = processed_data["profile"]
            
            # Traiter les expériences
            if "experiences" in profile and profile["experiences"]:
                for exp in profile["experiences"]:
                    # Ne plus convertir full_descriptions en liste
                    if "full_descriptions" in exp and isinstance(exp["full_descriptions"], list):
                        # Si c'est une liste, prendre le premier élément ou une chaîne vide
                        exp["full_descriptions"] = exp["full_descriptions"][0] if exp["full_descriptions"] else ""
            
            # Traiter les compétences
            if "skills" in profile and isinstance(profile["skills"], str):
                # Si skills est une chaîne, créer un dictionnaire par défaut
                profile["skills"] = {"General": [profile["skills"]]}
            
            # Traiter les langues
            if "languages" in profile and isinstance(profile["languages"], str):
                # Si languages est une chaîne, créer une liste avec un dictionnaire par défaut
                profile["languages"] = [{"language": profile["languages"], "level": ""}]
        
        try:
            # Créer l'instance sans ajouter l'ID comme champ
            instance = cls(**processed_data)
            # Définir l'ID directement sur l'instance
            instance.id = user_id
            return instance
        except Exception as e:
            print(f"Erreur lors de la construction de l'objet UserDocument: {e}")
            return None

    @classmethod
    def from_profile_state(cls, profile_state: "ProfileState", user_id: str) -> "UserDocument":
        """
        Crée une instance de UserDocument à partir d'un ProfileState.
        
        Args:
            profile_state (ProfileState): L'état du profil à convertir
            user_id (str): L'identifiant de l'utilisateur
            
        Returns:
            UserDocument: Une nouvelle instance de UserDocument
        """
        # Créer le profil de base
        profile = Profile(
            head=HeadProfile(
                name=profile_state.head.name,
                title=profile_state.head.general_title,
                mail=profile_state.head.email,
                phone=profile_state.head.phone,
                linkedin_url=""  # Champ obligatoire selon le schéma
            )
        )
        
        # Convertir les expériences
        profile.experiences = []
        for exp in profile_state.experiences:
            profile.experiences.append(ExperienceProfile(
                title=exp.intitule,
                company=exp.etablissement,
                dates=exp.dates,
                location=exp.lieu,
                full_descriptions=exp.description
            ))
        
        # Convertir les formations
        profile.educations = []
        for edu in profile_state.education:
            profile.educations.append(EducationProfile(
                title=edu.intitule,
                university=edu.etablissement,
                dates=edu.dates,
                full_description=edu.description
            ))
        
        # Traiter les compétences - maintenant en tant que chaîne de caractères
        if profile_state.head.skills:
            profile.skills = profile_state.head.skills  # Garder en tant que chaîne
        
        # Traiter les langues - maintenant en tant que chaîne de caractères
        if profile_state.head.langues:
            # Conserver la chaîne brute au lieu de la convertir en liste
            profile.languages = profile_state.head.langues
        
        # Traiter les hobbies
        if profile_state.head.hobbies:
            profile.hobbies = profile_state.head.hobbies
        
        # Créer et retourner le UserDocument
        return cls(
            id=user_id,
            profile=profile,
            cvs=[]  # Liste vide de CVs par défaut
        )
    
    def update_cv_from_global_state(self, cv_name: str, result_state, save_to_firestore: bool = True) -> Optional[Dict[str, Any]]:
        """
        Met à jour un CV existant avec les données provenant d'un GlobalState
        
        Args:
            cv_name (str): Nom du CV à mettre à jour
            result_state: Instance de GlobalState contenant les résultats du traitement
            save_to_firestore (bool): Si True, sauvegarde immédiatement les modifications dans Firestore
            
        Returns:
            Optional[Dict[str, Any]]: Informations sur la mise à jour ou None si le CV n'a pas été trouvé
        """
        # Trouver le CV correspondant au nom fourni
        cv_index = next((i for i, cv in enumerate(self.cvs) if cv.cv_name == cv_name), None)
        if cv_index is None:
            return None
        
        # Récupérer le CV existant
        cv = self.cvs[cv_index]
        
        # Mise à jour des informations de base du CV
        cv.cv_data.name = result_state.head.name
        cv.cv_data.title = result_state.head.title_refined
        cv.cv_data.mail = result_state.head.mail
        cv.cv_data.phone = result_state.head.tel_refined
        
        # Mise à jour des noms de sections
        if result_state.sections:
            cv.cv_data.sections_name.experience_section_name = result_state.sections.get("experience", "Expérience Professionnelle")
            cv.cv_data.sections_name.education_section_name = result_state.sections.get("education", "Formation")
            cv.cv_data.sections_name.skills_section_name = result_state.sections.get("skills", "Compétences")
            cv.cv_data.sections_name.languages_section_name = result_state.sections.get("languages", "Langues")
            cv.cv_data.sections_name.hobbies_section_name = result_state.sections.get("hobbies", "Centres d'intérêt")
        
        # Mise à jour des expériences
        if result_state.experiences:
            cv.cv_data.experiences = []
            for exp in result_state.experiences:
                cv.cv_data.experiences.append(ExperienceCV(
                    title=exp.title_refined,
                    company=exp.company_refined,
                    dates=exp.dates_refined,
                    location=exp.location_refined,
                    bullets=exp.bullets or []
                ))
        
        # Mise à jour des formations
        if result_state.education:
            cv.cv_data.educations = []
            for edu in result_state.education:
                cv.cv_data.educations.append(EducationCV(
                    title=edu.degree_refined,
                    university=edu.institution_refined,
                    dates=edu.dates_refined,
                    location=edu.location_refined,
                    description=edu.description_refined
                ))
        
        # Mise à jour des compétences
        if result_state.competences:
            cv.cv_data.skills = []
            for category_name, skills_list in result_state.competences.items():
                skills_str = ", ".join(skills_list)
                cv.cv_data.skills.append(SkillCV(
                    category_name=category_name,
                    skills=skills_str
                ))
        
        # Mise à jour des langues
        if result_state.langues:
            cv.cv_data.languages = []
            for lang in result_state.langues:
                cv.cv_data.languages.append(LanguageCV(
                    language=lang.language,
                    level=lang.level
                ))
        
        # Mise à jour des hobbies
        if result_state.hobbies_refined:
            cv.cv_data.hobbies = result_state.hobbies_refined
        
        # Mise à jour de la description du poste
        if result_state.job_refined:
            cv.job_raw = result_state.job_refined
        
        # Sauvegarder dans Firestore si demandé
        if save_to_firestore:
            self.save()
        
        # Retourner des informations sur la mise à jour
        return {
            "cv_name": cv_name,
            "updated": True,
            "name": cv.cv_data.name,
            "title": cv.cv_data.title,
            "experiences": len(cv.cv_data.experiences),
            "educations": len(cv.cv_data.educations),
            "skills": len(cv.cv_data.skills),
            "languages": len(cv.cv_data.languages),
            "hobbies_updated": bool(cv.cv_data.hobbies),
            "job_updated": bool(cv.job_raw)
        }
    
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
