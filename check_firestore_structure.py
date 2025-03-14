import json
import firebase_admin
from firebase_admin import credentials, firestore
import argparse
from colorama import Fore, Style, init

# Initialiser colorama pour les couleurs dans le terminal
init()

class FirestoreSchemaValidator:
    """
    Validateur de schéma Firestore qui vérifie si la structure de la base de données
    est conforme au schéma défini.
    """
    
    def __init__(self, schema_path, credential_path=None):
        """
        Initialise le validateur avec un chemin vers le schéma et éventuellement
        un chemin vers les identifiants Firebase.
        
        Args:
            schema_path (str): Chemin vers le fichier de schéma JSON
            credential_path (str, optional): Chemin vers le fichier d'identifiants Firebase
        """
        # Charger le schéma
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
        
        # Initialiser Firebase si ce n'est pas déjà fait
        if not firebase_admin._apps:
            if credential_path:
                cred = credentials.Certificate(credential_path)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()
        
        # Obtenir une référence à Firestore
        self.db = firestore.client()
        
        # Initialiser les compteurs pour les statistiques
        self.stats = {
            'collections_checked': 0,
            'collections_missing': 0,
            'fields_checked': 0,
            'fields_missing': 0,
            'fields_wrong_type': 0
        }
    
    def validate_type(self, value, expected_type):
        """
        Valide si une valeur est du type attendu selon le schéma.
        
        Args:
            value: La valeur à vérifier
            expected_type (str): Le type attendu ('string', 'number', 'array', etc.)
            
        Returns:
            bool: True si le type est correct, False sinon
        """
        if value is None:
            return False
        
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'number':
            return isinstance(value, (int, float))
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'array':
            return isinstance(value, list)
        elif expected_type == 'map':
            return isinstance(value, dict)
        elif expected_type == 'timestamp':
            # Pour Firestore, les timestamps sont convertis en objets datetime
            # par la bibliothèque Python
            from datetime import datetime
            return isinstance(value, datetime)
        
        return False
    
    def check_collection(self, collection_path, schema_def, parent_doc=None):
        """
        Vérifie si une collection correspond au schéma défini.
        
        Args:
            collection_path (str): Chemin de la collection
            schema_def (dict): Définition du schéma pour cette collection
            parent_doc (DocumentReference, optional): Document parent si c'est une sous-collection
            
        Returns:
            bool: True si la collection est conforme, False sinon
        """
        print(f"\n{Fore.BLUE}Vérification de la collection : {collection_path}{Style.RESET_ALL}")
        self.stats['collections_checked'] += 1
        
        # Obtenir la référence à la collection
        if parent_doc:
            collection_ref = parent_doc.collection(collection_path.split('/')[-1])
        else:
            collection_ref = self.db.collection(collection_path)
        
        # Vérifier si la collection existe
        documents = list(collection_ref.limit(1).stream())
        if not documents:
            print(f"{Fore.YELLOW}Attention : Collection {collection_path} vide ou inexistante{Style.RESET_ALL}")
            self.stats['collections_missing'] += 1
            return False
        
        # Vérifier un échantillon de documents
        sample_size = min(10, len(documents))
        sample_docs = list(collection_ref.limit(sample_size).stream())
        
        all_valid = True
        
        for doc in sample_docs:
            doc_data = doc.to_dict()
            print(f"  {Fore.CYAN}Document: {doc.id}{Style.RESET_ALL}")
            
            # Vérifier les champs
            fields_def = schema_def.get('fields', {})
            for field_name, field_type in fields_def.items():
                self.stats['fields_checked'] += 1
                
                if field_name not in doc_data:
                    print(f"    {Fore.RED}✗ Champ manquant: {field_name}{Style.RESET_ALL}")
                    self.stats['fields_missing'] += 1
                    all_valid = False
                    continue
                
                # Vérifier le type
                if not self.validate_type(doc_data[field_name], field_type):
                    print(f"    {Fore.RED}✗ Type incorrect pour {field_name}: attendu {field_type}{Style.RESET_ALL}")
                    self.stats['fields_wrong_type'] += 1
                    all_valid = False
                else:
                    print(f"    {Fore.GREEN}✓ {field_name}{Style.RESET_ALL}")
            
            # Vérifier les sous-collections
            subcollections_def = schema_def.get('subcollections', {})
            for subcoll_name, subcoll_def in subcollections_def.items():
                subcoll_path = f"{collection_path}/{doc.id}/{subcoll_name}"
                subcoll_valid = self.check_collection(subcoll_path, subcoll_def, parent_doc=doc.reference)
                all_valid = all_valid and subcoll_valid
        
        return all_valid
    
    def validate(self):
        """
        Valide toute la structure de la base de données selon le schéma.
        
        Returns:
            bool: True si tout est conforme, False sinon
        """
        print(f"{Fore.MAGENTA}=== Début de la validation du schéma Firestore ==={Style.RESET_ALL}")
        
        all_valid = True
        
        # Parcourir toutes les collections de premier niveau
        for collection_name, collection_def in self.schema['collections'].items():
            collection_valid = self.check_collection(collection_name, collection_def)
            all_valid = all_valid and collection_valid
        
        # Afficher les statistiques
        print(f"\n{Fore.MAGENTA}=== Résultats de la validation ==={Style.RESET_ALL}")
        print(f"Collections vérifiées: {self.stats['collections_checked']}")
        print(f"Collections manquantes: {self.stats['collections_missing']}")
        print(f"Champs vérifiés: {self.stats['fields_checked']}")
        print(f"Champs manquants: {self.stats['fields_missing']}")
        print(f"Champs avec type incorrect: {self.stats['fields_wrong_type']}")
        
        if all_valid:
            print(f"\n{Fore.GREEN}✓ La structure de la base de données est conforme au schéma.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}✗ La structure de la base de données présente des écarts par rapport au schéma.{Style.RESET_ALL}")
        
        return all_valid


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vérifier la structure de Firestore par rapport à un schéma défini")
    parser.add_argument('--schema', default='firestore_schema.json', help='Chemin vers le fichier de schéma JSON')
    parser.add_argument('--creds', help='Chemin vers le fichier d\'identifiants Firebase (facultatif)')
    
    args = parser.parse_args()
    
    validator = FirestoreSchemaValidator(args.schema, args.creds)
    validator.validate() 