import json
import sys
from pathlib import Path
from backend.models import UserDocument

def download_user(user_id: str, output_dir: str = "data") -> None:
    """
    Télécharge un document utilisateur à partir de son ID et l'enregistre en JSON.
    
    Args:
        user_id (str): L'ID de l'utilisateur à télécharger
        output_dir (str): Le répertoire où sauvegarder le fichier JSON
    """
    # Créer le répertoire de sortie s'il n'existe pas
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Récupérer le document utilisateur
    user_doc = UserDocument.from_firestore_id(user_id)
    
    if user_doc is None:
        print(f"Erreur: Aucun utilisateur trouvé avec l'ID {user_id}")
        sys.exit(1)
    
    # Convertir le document en dictionnaire
    user_dict = user_doc.model_dump()
    
    # Créer le nom du fichier de sortie
    output_file = output_path / f"user_{user_id}.json"
    
    # Sauvegarder en JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(user_dict, f, ensure_ascii=False, indent=2)
    
    print(f"Document utilisateur sauvegardé dans {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_user.py <user_id> [output_dir]")
        sys.exit(1)
    
    user_id = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "data"
    
    download_user(user_id, output_dir)

