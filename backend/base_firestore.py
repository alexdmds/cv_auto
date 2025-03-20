import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from datetime import datetime
from typing import ClassVar, TypeVar, Type, Optional, Dict, Any, List, Generic
from pydantic import BaseModel, Field

# Type générique pour les modèles Firestore
T = TypeVar('T', bound='FirestoreModel')

class FirestoreModel(BaseModel):
    """Classe de base pour tous les modèles Firestore basée sur Pydantic"""
    
    id: Optional[str] = None
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
    def from_dict(cls: Type[T], data: Dict[str, Any], doc_id: Optional[str] = None) -> T:
        """Crée une instance de l'objet à partir d'un dictionnaire"""
        if doc_id:
            return cls(**data, id=doc_id)
        return cls(**data)
    
    @classmethod
    def from_doc_snapshot(cls: Type[T], doc) -> T:
        """Crée une instance à partir d'un DocumentSnapshot Firestore"""
        data = doc.to_dict()
        return cls.from_dict(data, doc.id)
    
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire pour stockage Firestore"""
        # Exclure id et les champs None
        data = self.model_dump(exclude={'id'}, exclude_none=True)
        return data
    
    def save(self, doc_id: Optional[str] = None) -> str:
        """Sauvegarde l'objet dans Firestore"""
        db = self.get_db()
        data = self.to_dict()
        
        if doc_id:
            # Sauvegarde avec un ID spécifique
            db.collection(self.collection_name).document(doc_id).set(data)
            self.id = doc_id
            return doc_id
        elif self.id:
            # Mise à jour d'un document existant
            db.collection(self.collection_name).document(self.id).set(data)
            return self.id
        else:
            # Création d'un nouveau document avec ID auto-généré
            doc_ref = db.collection(self.collection_name).add(data)[1]
            self.id = doc_ref.id
            return doc_ref.id

    @classmethod
    def list_all(cls: Type[T]) -> List[T]:
        """Récupère tous les documents d'une collection"""
        db = cls.get_db()
        docs = db.collection(cls.collection_name).stream()
        return [cls.from_doc_snapshot(doc) for doc in docs]
        
    @classmethod
    def query(cls: Type[T], field: str, operator: str, value: Any) -> List[T]:
        """Effectue une requête simple sur la collection"""
        db = cls.get_db()
        query = db.collection(cls.collection_name).where(field, operator, value)
        docs = query.stream()
        return [cls.from_doc_snapshot(doc) for doc in docs] 