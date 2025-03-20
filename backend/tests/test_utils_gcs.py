import pytest
from backend.utils.utils_gcs import get_concatenated_text_files, get_linkedin_profile_content
from google.cloud import storage
from backend.config import load_config
import logging
from backend.models import UserDocument, Profile, HeadProfile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_test_user_document():
    """Crée un UserDocument de test"""
    profile = Profile(
        head=HeadProfile(
            name="Test User",
            title="Test Title",
            mail="test@example.com",
            phone="+33612345678",
            linkedin_url="https://linkedin.com/in/testuser"
        )
    )
    return UserDocument(id="test_user", profile=profile)

def test_get_linkedin_profile_content():
    """Test de la récupération du contenu LinkedIn (actuellement désactivé)"""
    # Test avec un profil LinkedIn réel
    linkedin_url = "https://www.linkedin.com/in/alexis-de-monts-61328a175/"
    content = get_linkedin_profile_content(linkedin_url)
    
    print("\nTest de la fonction get_linkedin_profile_content...")
    print(f"URL testée : {linkedin_url}")
    
    # Vérifier que le contenu est vide (comportement actuel voulu)
    assert content == "", "La fonction devrait retourner une chaîne vide car la récupération LinkedIn est désactivée"

def test_get_concatenated_text_files(caplog):
    caplog.set_level(logging.DEBUG)
    
    # Test direct d'accès au bucket
    config = load_config()
    print(f"\nUtilisation du bucket: {config.BUCKET_NAME}")
    
    try:
        # Créer le client Storage avec l'authentification par défaut
        storage_client = storage.Client()
        bucket = storage_client.bucket(config.BUCKET_NAME)
        
        # Lister les fichiers
        print("\nTentative de listage des fichiers...")
        blobs = list(bucket.list_blobs(prefix="test_user/sources/"))
        print(f"Nombre de fichiers trouvés : {len(blobs)}")
        
        for blob in blobs:
            print(f"\nFichier trouvé : {blob.name}")
            try:
                content = blob.download_as_bytes()
                print(f"Contenu du fichier {blob.name}: {content[:100]}...")  # Afficher les 100 premiers caractères
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier {blob.name}: {str(e)}")
                
    except Exception as e:
        print(f"\nErreur lors de l'accès direct au bucket: {str(e)}")
        raise
    
    # Test de la fonction
    print("\nTest de la fonction get_concatenated_text_files...")
    user_doc = create_test_user_document()
    result = get_concatenated_text_files(user_doc)
    
    # Vérifier que le résultat n'est pas vide et afficher le contenu
    print("\nContenu récupéré du bucket:")
    print(result)
    
    assert result != "", "Aucun contenu n'a été récupéré du bucket"

def test_get_concatenated_text_files_empty():
    # Utiliser un ID utilisateur qui n'existe pas
    user_doc = UserDocument(id="nonexistent_user")
    
    # Vérifier que le résultat est une chaîne vide
    result = get_concatenated_text_files(user_doc)
    assert result == "" 