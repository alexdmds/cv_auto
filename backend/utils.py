import json
from pathlib import Path
from google.cloud import storage
from config import load_config

from pathlib import Path
from google.cloud import storage
from config import load_config

from firebase_init import db
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import tiktoken
from typing import Any, Dict

async def async_openai_call(user_id: str, client, **kwargs: Dict[str, Any]):
    """
    Appelle l'API OpenAI de manière asynchrone en utilisant run_in_executor et en enregistrant les tokens.

    :param user_id: ID de l'utilisateur pour enregistrer les tokens.
    :param client: Client OpenAI configuré.
    :param kwargs: Arguments pour l'appel de l'API OpenAI.
    :return: Résultat de l'appel à OpenAI.
    """
    loop = asyncio.get_event_loop()

    # Convertir la liste de messages en une chaîne pour compter les tokens
    try:
        messages = kwargs.get("messages", [])
        message_str = "\n".join(f"{msg['role']}: {msg['content']}" for msg in messages if "content" in msg)
        add_tokens_to_users(user_id, message_str)  # Compte et ajoute les tokens de l'entrée
    except Exception as e:
        print(f"Erreur lors du comptage des tokens pour l'utilisateur {user_id}: {e}")

    # Effectuer l'appel OpenAI dans un thread
    try:
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, 
                lambda: client.chat.completions.create(**kwargs)
            )
    except Exception as e:
        print(f"Erreur lors de l'appel OpenAI pour l'utilisateur {user_id}: {e}")
        raise  # Relève l'exception pour gestion ultérieure


def get_files_in_directory(chemin_relatif):
    """
    Récupère tous les fichiers dans un dossier donné selon l'environnement actif.

    :param chemin_relatif: Chemin relatif d'un dossier (ex: "profil/sources/").
    :return: Liste des chemins des fichiers trouvés dans le dossier.
    :raises FileNotFoundError: Si le dossier n'existe pas ou est vide.
    :raises ValueError: Si le chemin fourni n'est pas un dossier.
    """
    # Charger la configuration
    config = load_config()

    # Construire le chemin de base selon l'environnement
    if config.ENV == "local":
        base_path = config.LOCAL_BASE_PATH
        full_path = base_path / chemin_relatif
        if not full_path.is_dir():
            raise ValueError(f"Le chemin fourni n'est pas un dossier : {chemin_relatif}")

        # Lister les fichiers locaux
        files = [file.relative_to(base_path) for file in full_path.glob("*") if file.is_file()]
        if not files:
            raise FileNotFoundError(f"Aucun fichier trouvé dans le dossier : {chemin_relatif}")
        return files

    elif config.ENV in ["dev", "prod"]:
        storage_client = storage.Client()
        bucket = storage_client.bucket(config.BUCKET_NAME)
        blobs = list(bucket.list_blobs(prefix=chemin_relatif))

        # Filtrer uniquement les fichiers dans le dossier (pas les sous-dossiers)
        files = []
        for blob in blobs:
            blob_path = Path(blob.name)
            if blob_path.parent == Path(chemin_relatif) and not blob.name.endswith("/"):
                files.append(blob_path)

        if not files:
            raise FileNotFoundError(f"Aucun fichier trouvé dans le dossier : {chemin_relatif}")
        return files

    else:
        raise ValueError(f"Environnement inconnu : {config.ENV}")

def get_file(chemin_relatif):
    """
    Récupère un fichier unique selon l'environnement actif et un chemin relatif.

    :param chemin_relatif: Chemin relatif d'un fichier unique (ex: "profil/sources/file.pdf").
    :return: Chemin local du fichier.
    """
    # Charger la configuration
    config = load_config()

    # Construire le chemin de base selon l'environnement
    if config.ENV == "local":
        base_path = config.LOCAL_BASE_PATH
        full_path = base_path / chemin_relatif

        # Vérifier que le fichier existe localement
        if not full_path.exists() or not full_path.is_file():
            raise FileNotFoundError(f"Le fichier spécifié n'existe pas localement : {full_path}")

        return full_path

    elif config.ENV in ["dev", "prod"]:
        # Gestion en mode distant : télécharger depuis le bucket
        storage_client = storage.Client()
        bucket = storage_client.bucket(config.BUCKET_NAME)
        blob = bucket.blob(chemin_relatif)

        if not blob.exists():
            raise FileNotFoundError(f"Le fichier spécifié n'existe pas dans le bucket : {chemin_relatif}")

        # Télécharger le fichier vers /tmp
        temp_file = Path("/tmp") / Path(chemin_relatif).name
        temp_file.parent.mkdir(parents=True, exist_ok=True)  # Créer les répertoires si nécessaire
        blob.download_to_filename(temp_file)

        return temp_file

    else:
        raise ValueError(f"Environnement inconnu : {config.ENV}")


def save_file(chemin_relatif, content):
    """
    Enregistre un fichier selon l'environnement actif et un chemin relatif.

    :param chemin_relatif: Chemin relatif à partir du profil (ex: "profil/cvs/cv1/output.json").
    :param content: Contenu à enregistrer (décodé ou binaire).
    """
    # Charger la configuration
    config = load_config()

    # Construire le chemin complet selon l'environnement
    if config.ENV in ["local"]:
        base_path = config.LOCAL_BASE_PATH
        file_path = base_path / chemin_relatif
    elif config.ENV in ["prod", "dev"]:
        file_path = Path("/tmp") / chemin_relatif
    else:
        raise ValueError(f"Environnement inconnu : {config.ENV}")

    # Créer les répertoires nécessaires
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Enregistrer localement ou sur dev
    extension = file_path.suffix.lower()
    if config.ENV in ["local"]:
        if extension == ".json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=4)
        elif extension == ".txt":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        elif extension in [".jpg", ".pdf"]:
            with open(file_path, "wb") as f:
                f.write(content)
        else:
            raise ValueError(f"Format de fichier non pris en charge : {extension}")
        print(f"Fichier sauvegardé localement : {file_path}")

    # Enregistrer sur le bucket en dev/prod
    elif config.ENV in ["prod", "dev"]:
        storage_client = storage.Client()
        bucket = storage_client.bucket(config.BUCKET_NAME)
        blob = bucket.blob(chemin_relatif)
        
        # Déterminer le type de contenu
        if isinstance(content, dict):  # JSON
            content_str = json.dumps(content, indent=4)
            content_type = "application/json"
        elif isinstance(content, str):  # Texte brut
            content_str = content
            content_type = "text/plain"
        elif isinstance(content, bytes):  # Contenu binaire
            blob.upload_from_string(content, content_type="application/octet-stream")
            print(f"Fichier sauvegardé dans le bucket : {chemin_relatif}")
            return
        else:
            raise ValueError(f"Format de contenu non pris en charge : {type(content)}")

        # Envoyer le fichier au bucket
        blob.upload_from_string(content_str, content_type=content_type)
        print(f"Fichier sauvegardé dans le bucket : {chemin_relatif}")
        
def process_files(profil, file_extension, output_extension, process_function):
    """
    Traite les fichiers pour un profil donné en fonction d'une fonction de transformation.

    :param profil: Nom du profil.
    :param file_extension: Extension des fichiers à traiter (ex: ".pdf").
    :param output_extension: Extension de sortie des fichiers (ex: ".txt").
    :param process_function: Fonction qui transforme un fichier en un autre format.
    """
    # Charger la configuration
    config = load_config()

    # Chemin source et motif
    source_path = f"{profil}/sources/*{file_extension}"

    # Récupérer les fichiers correspondants
    source_files = get_file(source_path)
    if not isinstance(source_files, list):  # Convertir en liste si un seul fichier est trouvé
        source_files = [source_files]

    # Traiter chaque fichier
    for source_file in source_files:
        output_file_name = Path(source_file).with_suffix(output_extension).name
        output_file_path = f"{profil}/sources/{output_file_name}"

        # Lire et transformer le fichier
        content = process_function(source_file)

        # Sauvegarder le fichier transformé localement
        save_file(output_file_path, content)

        # Si en mode "dev", uploader le fichier dans le bucket
        if config.ENV == "dev" or config.ENV == "prod":
            storage_client = storage.Client()
            bucket = storage_client.bucket(config.BUCKET_NAME)
            blob = bucket.blob(output_file_path)
            if isinstance(content, str):  # Texte ou JSON
                blob.upload_from_string(content, content_type="text/plain")
            else:  # Binaire
                blob.upload_from_string(content, content_type="application/octet-stream")
            print(f"Fichier transformé renvoyé dans le bucket : {output_file_path}")

        print(f"Fichier transformé et sauvegardé localement : {output_file_path}")

def get_openai_api_key():
    """
    Récupère la clé API OpenAI en fonction de l'environnement actif.
    :return: Clé API OpenAI.
    """
    # Charger la configuration
    config = load_config()

    # Récupérer la clé API
    return config.OPENAI_API_KEY

def get_prompt(prompt_name):
    """
    Récupère un prompt à partir de son nom.
    :param prompt_name: Nom du prompt.
    :return: Contenu du prompt.
    """
    # Charger la configuration
    config = load_config()

    # Construire le chemin complet du prompt
    prompt_path = config.LOCAL_PROMPT_PATH / prompt_name

    # Lire le contenu du prompt
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()
    
def count_tokens(text, model="gpt-4"):
    """
    Compte le nombre de tokens dans un texte pour un modèle donné.
    """
    # Charger l'encodeur de tokens pour le modèle
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)

def add_tokens_to_users(user_id, text):
    """
    Ajoute le nombre de tokens calculé à l'utilisateur dans Firebase Realtime Database.
    """
    # Compter les tokens dans le texte
    token_count = count_tokens(text, model="gpt-4")
    print(f"Nombre de tokens dans le texte : {token_count}")

    # Référence Firebase pour l'utilisateur
    user_ref = db.reference(f"users/{user_id}")

    try:
        # Récupérer les données existantes pour cet utilisateur
        user_data = user_ref.get()
        if user_data and "total_tokens" in user_data:
            total_tokens = user_data["total_tokens"]
        else:
            total_tokens = 0

        # Ajouter les tokens calculés au total
        new_total = total_tokens + token_count
        user_ref.update({"total_tokens": new_total})

        print(f"Total mis à jour pour l'utilisateur {user_id} : {new_total}")
    except Exception as e:
        print(f"Erreur lors de la mise à jour des tokens pour l'utilisateur {user_id} : {e}")

def can_user_proceed(profil):
    """
    Vérifie si un utilisateur peut effectuer un nouvel appel.
    Conditions :
    - Au moins 20 secondes se sont écoulées depuis le dernier appel.
    - Le nombre total de tokens est inférieur à 100 000.
    """
    # Obtenir la référence Firebase pour l'utilisateur
    user_ref = db.reference(f"users/{profil}")
    
    try:
        # Récupérer les données existantes pour l'utilisateur
        user_data = user_ref.get()

        # Obtenir le timestamp actuel
        current_timestamp = int(time.time())

        # Vérifier si un timestamp précédent existe
        if user_data and "last_call_timestamp" in user_data:
            last_call_timestamp = user_data["last_call_timestamp"]
        else:
            last_call_timestamp = 0  # Par défaut, aucun appel précédent

        # Vérifier si le délai de 20 secondes est respecté
        if current_timestamp - last_call_timestamp < 20:
            print(f"Temps insuffisant depuis le dernier appel : {current_timestamp - last_call_timestamp} secondes")
            return False

        # Vérifier si le total des tokens est inférieur à 100 000
        total_tokens = user_data.get("total_tokens", 0) if user_data else 0
        if total_tokens >= 100_000:
            print(f"Nombre de tokens trop élevé : {total_tokens}")
            return False

        # Mettre à jour le timestamp de l'appel actuel
        user_ref.update({"last_call_timestamp": current_timestamp})
        print(f"Timestamp mis à jour pour l'utilisateur {profil} : {current_timestamp}")
        return True

    except Exception as e:
        print(f"Erreur lors de la vérification des conditions pour l'utilisateur {profil} : {e}")
        return False

if __name__ == "__main__":
    # Exemple d'utilisation de can_user_proceed
    print(can_user_proceed("j4WSNb5TuQVwVwSpq65N7o06GC52"))
    