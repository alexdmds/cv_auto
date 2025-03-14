import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import os
import datetime
from google.cloud.firestore_v1._helpers import DatetimeWithNanoseconds
from typing import Dict, List, Any, Optional, ClassVar, Type, TypeVar, Union

# Définir des types génériques pour les classes de modèle
T = TypeVar('T', bound='FirestoreModel')

class FirestoreModel:
    """Classe de base pour tous les modèles Firestore"""
    
    collection_name: ClassVar[str] = ""  # Doit être défini dans les sous-classes
    
    @classmethod
    def initialize_firebase(cls):
        """Initialise la connexion Firebase si ce n'est pas déjà fait"""
        if not firebase_admin._apps:
            try:
                cred = credentials.ApplicationDefault()
            except:
                if os.path.exists('serviceAccountKey.json'):
                    cred = credentials.Certificate('serviceAccountKey.json')
                else:
                    raise Exception("Aucune méthode d'authentification Firebase n'a été trouvée.")
            
            firebase_admin.initialize_app(cred)
    
    @classmethod
    def get_db(cls):
        """Récupère l'instance de la base de données Firestore"""
        cls.initialize_firebase()
        return firestore.client()
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any], doc_id: str = None) -> T:
        """Crée une instance de l'objet à partir d'un dictionnaire"""
        instance = cls()
        for key, value in data.items():
            setattr(instance, key, value)
        
        if doc_id:
            instance.id = doc_id
            
        return instance
    
    @classmethod
    def from_doc_snapshot(cls: Type[T], doc) -> T:
        """Crée une instance à partir d'un DocumentSnapshot Firestore"""
        data = doc.to_dict()
        return cls.from_dict(data, doc.id)
    
    @classmethod
    def get_by_id(cls: Type[T], doc_id: str) -> Optional[T]:
        """Récupère un document par son ID"""
        db = cls.get_db()
        doc_ref = db.collection(cls.collection_name).document(doc_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return cls.from_doc_snapshot(doc)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire pour stockage Firestore"""
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_') and key != 'id':
                result[key] = value
        return result
    
    def save(self, doc_id: Optional[str] = None) -> str:
        """Sauvegarde l'objet dans Firestore"""
        db = self.get_db()
        data = self.to_dict()
        
        if doc_id:
            # Sauvegarde avec un ID spécifique
            db.collection(self.collection_name).document(doc_id).set(data)
            self.id = doc_id
            return doc_id
        elif hasattr(self, 'id') and self.id:
            # Mise à jour d'un document existant
            db.collection(self.collection_name).document(self.id).set(data)
            return self.id
        else:
            # Création d'un nouveau document avec ID auto-généré
            doc_ref = db.collection(self.collection_name).add(data)[1]
            self.id = doc_ref.id
            return doc_ref.id

# Classes pour la structure des données utilisateur
class EducationData:
    """Structure pour les données d'éducation"""
    def __init__(self, title=None, description=None, full_description=None, dates=None, 
                 university=None, location=None, **kwargs):
        self.title = title  # titre de la formation
        self.description = description  # description courte (pour cv)
        self.full_description = full_description  # description complète (pour profile)
        self.dates = dates  # dates de la formation
        self.university = university  # université ou école
        self.location = location  # lieu de la formation
        
        # Champs supplémentaires pour compatibilité
        for key, value in kwargs.items():
            setattr(self, key, value)


class ExperienceData:
    """Structure pour les données d'expérience"""
    def __init__(self, title=None, company=None, dates=None, location=None, 
                 full_descriptions=None, bullets=None, **kwargs):
        self.title = title  # titre du poste
        self.company = company  # nom de l'entreprise
        self.dates = dates  # dates de l'emploi
        self.location = location  # lieu de l'emploi
        self.full_descriptions = full_descriptions  # description complète (pour profile)
        self.bullets = bullets  # points clés (pour cv)
        
        # Champs supplémentaires pour compatibilité
        for key, value in kwargs.items():
            setattr(self, key, value)


class HeadData:
    """Structure pour les données d'en-tête"""
    def __init__(self, name=None, title=None, mail=None, phone=None, linkedin_url=None, **kwargs):
        self.name = name  # nom complet
        self.title = title  # titre professionnel
        self.mail = mail  # email
        self.phone = phone  # téléphone
        self.linkedin_url = linkedin_url  # URL LinkedIn
        
        # Champs supplémentaires pour compatibilité
        for key, value in kwargs.items():
            setattr(self, key, value)


class LanguageData:
    """Structure pour les données de langue"""
    def __init__(self, language=None, level=None, **kwargs):
        self.language = language  # nom de la langue
        self.level = level  # niveau et certifications
        
        # Champs supplémentaires pour compatibilité
        for key, value in kwargs.items():
            setattr(self, key, value)


class SkillData:
    """Structure pour les données de compétence"""
    def __init__(self, skills=None, category_name=None, **kwargs):
        self.skills = skills  # compétences
        self.category_name = category_name  # nom de la catégorie
        
        # Champs supplémentaires pour compatibilité
        for key, value in kwargs.items():
            setattr(self, key, value)


class CvData:
    """Structure pour les données de CV"""
    def __init__(self, cv_name=None, job_raw=None, educations=None, experiences=None, 
                 skills=None, languages=None, hobbies=None, name=None, phone=None, 
                 mail=None, title=None, lang_of_cv=None, sections_name=None, **kwargs):
        self.cv_name = cv_name  # nom du CV
        self.job_raw = job_raw  # description brute du poste
        self.educations = educations or []  # formations
        self.experiences = experiences or []  # expériences
        self.skills = skills or []  # compétences
        self.languages = languages or []  # langues
        self.hobbies = hobbies  # loisirs
        self.name = name  # nom sur le CV
        self.phone = phone  # téléphone
        self.mail = mail  # email
        self.title = title  # titre du CV
        self.lang_of_cv = lang_of_cv  # langue du CV
        self.sections_name = sections_name or {}  # noms des sections
        
        # Champs supplémentaires pour compatibilité
        for key, value in kwargs.items():
            setattr(self, key, value)


class ProfileData:
    """Structure pour les données de profil"""
    def __init__(self, head=None, educations=None, experiences=None, 
                 skills=None, languages=None, hobbies=None, **kwargs):
        self.head = head or {}  # données d'en-tête
        self.educations = educations or []  # formations
        self.experiences = experiences or []  # expériences
        self.skills = skills  # compétences
        self.languages = languages  # langues
        self.hobbies = hobbies  # loisirs
        
        # Champs supplémentaires pour compatibilité
        for key, value in kwargs.items():
            setattr(self, key, value)


class UserModel(FirestoreModel):
    """Modèle pour la collection 'users'"""
    collection_name = "users"
    
    def __init__(self, cvs=None, profile=None, **kwargs):
        self.id = None
        # Suivre strictement la structure du schéma
        self.cvs = cvs or []  # Liste des CV
        self.profile = profile or {}  # Données de profil
        
        # Ne pas inclure d'autres champs qui ne sont pas dans le schéma
        # Les attributs comme 'email', 'name', 'created_at' ne doivent pas être dans le modèle
        # si nous voulons suivre strictement le schéma
    
    def update_cv_from_global_state(self, cv_name, result_state, save_to_firestore=False):
        """
        Met à jour un CV existant à partir d'un objet GlobalState
        
        Args:
            cv_name: Nom du CV à mettre à jour
            result_state: Objet GlobalState contenant les données traitées
            save_to_firestore: Si True, sauvegarde immédiatement dans Firestore
            
        Returns:
            dict: Informations sur le CV mis à jour, ou None si le CV n'est pas trouvé
        """
        # Trouver l'index du CV à mettre à jour
        cv_index = None
        for i, cv in enumerate(self.cvs):
            if cv.get('cv_name') == cv_name:
                cv_index = i
                break
        
        if cv_index is None:
            return None
        
        # Récupérer le CV existant
        existing_cv = self.cvs[cv_index]
        original_cv_data = existing_cv.get('cv_data', {})
        
        # Mettre à jour les données du CV en suivant strictement le schéma
        updated_cv = {
            'cv_name': cv_name,
            'job_raw': getattr(result_state, 'job_raw', existing_cv.get('job_raw', '')),
            # Supprimer les champs non présents dans le schéma
            # 'last_update': datetime.datetime.now().isoformat(),
            # 'creation_date': existing_cv.get('creation_date', datetime.datetime.now().isoformat()),
            'cv_data': {
                'name': result_state.head.name,
                'title': result_state.head.title_refined,
                'mail': result_state.head.mail,
                'phone': result_state.head.tel_refined,
                'lang_of_cv': original_cv_data.get('lang_of_cv', 'fr'),
                'sections_name': original_cv_data.get('sections_name', {
                    'experience_section_name': 'Expérience Professionnelle',
                    'education_section_name': 'Formation',
                    'skills_section_name': 'Compétences',
                    'languages_section_name': 'Langues',
                    'hobbies_section_name': 'Centres d\'intérêt'
                }),
                'experiences': [],
                'educations': [],
                'skills': [],
                'languages': [],
                'hobbies': ''
            }
        }
        
        # Ajouter les expériences
        if hasattr(result_state, 'experiences'):
            for exp in result_state.experiences:
                experience = {
                    'title': exp.title_refined,
                    'company': exp.company_refined,
                    'dates': exp.dates_refined,
                    'location': exp.location_refined,
                    'bullets': exp.bullets if hasattr(exp, 'bullets') and exp.bullets else []
                }
                updated_cv['cv_data']['experiences'].append(experience)
        
        # Ajouter les formations
        if hasattr(result_state, 'education'):
            for edu in result_state.education:
                education = {
                    'title': edu.degree_refined,
                    'university': edu.institution_refined,
                    'dates': edu.dates_refined,
                    'location': edu.location_refined,
                    'description': edu.description_refined
                }
                updated_cv['cv_data']['educations'].append(education)
        
        # Ajouter les compétences
        if hasattr(result_state, 'competences') and result_state.competences:
            for category, skills in result_state.competences.items():
                skill_category = {
                    'category_name': category,
                    'skills': ', '.join(skills) if isinstance(skills, list) else skills
                }
                updated_cv['cv_data']['skills'].append(skill_category)
        
        # Ajouter les langues
        if hasattr(result_state, 'langues'):
            for langue in result_state.langues:
                if hasattr(langue, 'language') and hasattr(langue, 'level'):
                    language = {
                        'language': getattr(langue, 'language', ''),
                        'level': getattr(langue, 'level', '')
                    }
                    updated_cv['cv_data']['languages'].append(language)
                elif isinstance(langue, dict):
                    language = {
                        'language': langue.get('language', ''),
                        'level': langue.get('level', '')
                    }
                    updated_cv['cv_data']['languages'].append(language)
        
        # Ajouter les hobbies
        if hasattr(result_state, 'hobbies_refined'):
            updated_cv['cv_data']['hobbies'] = result_state.hobbies_refined
        
        # Mettre à jour le CV dans la liste
        self.cvs[cv_index] = updated_cv
        
        # Sauvegarder si demandé
        if save_to_firestore:
            self.save()
        
        # Retourner les informations sur le CV mis à jour sans inclure les champs hors schéma
        return {
            "name": updated_cv['cv_name'],
            "experiences_count": len(updated_cv['cv_data']['experiences']),
            "education_count": len(updated_cv['cv_data']['educations']),
            "skills_count": len(updated_cv['cv_data']['skills'])
        }


class CallModel(FirestoreModel):
    """Modèle pour la collection 'calls'"""
    collection_name = "calls"
    
    def __init__(self, user_id=None, endpoint=None, call_time=None, usage_count=None, **kwargs):
        self.id = None
        self.user_id = user_id
        self.endpoint = endpoint
        self.call_time = call_time or datetime.datetime.now()
        self.usage_count = usage_count or 1
        
        # Pour compatibilité avec l'ancien format
        if 'timestamp' in kwargs:
            self.call_time = kwargs.pop('timestamp')
        if 'duration' in kwargs:
            self.duration = kwargs.pop('duration')
        if 'status' in kwargs:
            self.status = kwargs.pop('status')
            
        # Ajouter tous les autres attributs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def get_by_user_id(cls, user_id: str) -> List['CallModel']:
        """Récupère tous les appels d'un utilisateur"""
        db = cls.get_db()
        query = db.collection(cls.collection_name).where('user_id', '==', user_id)
        docs = query.stream()
        
        return [cls.from_doc_snapshot(doc) for doc in docs]


class UsageModel(FirestoreModel):
    """Modèle pour la collection 'usage'"""
    collection_name = "usage"
    
    def __init__(self, user_id=None, last_request_time=None, total_usage=None, **kwargs):
        self.id = None
        self.user_id = user_id
        self.last_request_time = last_request_time or datetime.datetime.now()
        self.total_usage = total_usage or 0
        
        # Pour compatibilité avec l'ancien format
        if 'quota' in kwargs:
            self.quota = kwargs.pop('quota')
        if 'used' in kwargs:
            self.total_usage = kwargs.pop('used')
        if 'last_update' in kwargs:
            self.last_request_time = kwargs.pop('last_update')
            
        # Ajouter tous les autres attributs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def get_by_user_id(cls, user_id: str) -> Optional['UsageModel']:
        """Récupère l'usage d'un utilisateur"""
        db = cls.get_db()
        query = db.collection(cls.collection_name).where('user_id', '==', user_id).limit(1)
        docs = query.stream()
        
        for doc in docs:
            return cls.from_doc_snapshot(doc)
        return None
    
    def increment_usage(self, amount: int = 1) -> 'UsageModel':
        """Incrémente le compteur d'utilisation"""
        self.total_usage = (self.total_usage or 0) + amount
        self.last_request_time = datetime.datetime.now()
        self.save()
        return self 