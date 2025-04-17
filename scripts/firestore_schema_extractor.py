import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import os
import datetime
from firebase_admin.firestore import DocumentReference
from google.cloud.firestore_v1._helpers import DatetimeWithNanoseconds

class FirestoreEncoder(json.JSONEncoder):
    """Encodeur JSON personnalisé pour gérer les types spéciaux de Firestore"""
    def default(self, obj):
        if isinstance(obj, DatetimeWithNanoseconds):
            return obj.isoformat()
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, DocumentReference):
            return str(obj.path)
        elif isinstance(obj, bytes):
            return obj.decode('utf-8')
        return super().default(obj)

def extraire_schema_firestore():
    # Vérifier si Firebase est déjà initialisé
    if not firebase_admin._apps:
        # Initialiser Firebase Admin SDK
        # Supposant que vous avez un fichier de clé de service
        # Si vous utilisez une autre méthode d'authentification, veuillez l'adapter
        try:
            cred = credentials.ApplicationDefault()
        except:
            # Chercher un fichier serviceAccountKey.json dans le répertoire courant
            if os.path.exists('serviceAccountKey.json'):
                cred = credentials.Certificate('serviceAccountKey.json')
            else:
                print("Erreur: Aucune méthode d'authentification Firebase n'a été trouvée.")
                print("Veuillez fournir un fichier serviceAccountKey.json ou configurer les variables d'environnement.")
                return

        firebase_admin.initialize_app(cred)

    # Se connecter à Firestore
    db = firestore.client()
    
    # Liste des collections à récupérer
    collections = ["users", "calls", "usage"]
    
    # Dictionnaire qui va contenir tous les schémas
    all_schemas = {}
    
    # Récupérer le document "model" de chaque collection
    for collection_name in collections:
        doc_ref = db.collection(collection_name).document('model')
        doc = doc_ref.get()
        
        if doc.exists:
            # Convertir le document en dictionnaire
            document_data = doc.to_dict()
            # Ajouter au dictionnaire général
            all_schemas[collection_name] = document_data
            print(f"Schéma du document 'model' de la collection '{collection_name}' récupéré avec succès")
        else:
            print(f"Attention: Le document 'model' n'existe pas dans la collection '{collection_name}'")
            # Ajouter une entrée vide pour cette collection
            all_schemas[collection_name] = None
    
    # Écrire le dictionnaire combiné dans un fichier JSON
    with open('firestore_schema.json', 'w', encoding='utf-8') as f:
        json.dump(all_schemas, f, ensure_ascii=False, indent=4, cls=FirestoreEncoder)
    
    print("Tous les schémas ont été enregistrés avec succès dans firestore_schema.json")

if __name__ == "__main__":
    extraire_schema_firestore() 