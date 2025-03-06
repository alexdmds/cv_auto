import firebase_admin
from firebase_admin import firestore
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_user_document(user_id):
    """
    Télécharge le document d'un utilisateur depuis Firestore
    et le convertit en format JSON.
    
    Args:
        user_id (str): ID de l'utilisateur à télécharger.
        
    Returns:
        dict: Données de l'utilisateur sous forme de dictionnaire.
    """
    try:
        # Initialisation de Firebase avec les credentials par défaut
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app()
            logger.info("Firebase Admin initialisé avec les credentials par défaut")

        # Connexion à Firestore
        db = firestore.Client()
        
        # Récupération des données de l'utilisateur
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            logger.error(f"Document pour l'utilisateur {user_id} non trouvé.")
            return None
        
        data = user_doc.to_dict()
        data['user_id'] = user_doc.id
        
        # Sauvegarde des données en format JSON
        with open(f"{user_id}_data.json", 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        
        logger.info(f"Données téléchargées et sauvegardées avec succès pour l'utilisateur {user_id}.")
        return data
        
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement des données: {str(e)}")
        raise

if __name__ == "__main__":
    user_id = "test_user"
    data = download_user_document(user_id)
    if data is not None:
        print("\nDonnées téléchargées :")
        print(data)
        print(f"\nDonnées sauvegardées dans {user_id}_data.json")
