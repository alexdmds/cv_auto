import json
from pathlib import Path
from google.cloud import storage
from config import load_config

from pathlib import Path
from google.cloud import storage
from config import load_config

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
    if config.ENV in ["local", "dev"]:
        base_path = config.LOCAL_BASE_PATH if config.ENV == "local" else config.TEMP_PATH
        full_path = base_path / chemin_relatif
    elif config.ENV == "prod":
        full_path = Path("/tmp") / chemin_relatif
    else:
        raise ValueError(f"Environnement inconnu : {config.ENV}")

    # Vérifier si c'est un dossier
    if config.ENV in ["local", "dev"]:
        if not full_path.is_dir():
            raise ValueError(f"Le chemin fourni n'est pas un dossier : {chemin_relatif}")

        # Lister les fichiers dans le dossier
        files = list(full_path.glob("*"))  # Récupérer tous les fichiers et dossiers
        files = [file for file in files if file.is_file()]  # Filtrer uniquement les fichiers
        if not files:
            raise FileNotFoundError(f"Aucun fichier trouvé dans le dossier : {chemin_relatif}")
        return files

    # Gestion en mode "prod" : liste des fichiers depuis le bucket
    elif config.ENV == "prod":
        storage_client = storage.Client()
        bucket = storage_client.bucket(config.BUCKET_NAME)
        blobs = list(bucket.list_blobs(prefix=chemin_relatif))

        # Filtrer uniquement les fichiers dans le dossier (pas les sous-dossiers)
        files = []
        for blob in blobs:
            blob_path = Path(blob.name)
            if blob_path.parent == Path(chemin_relatif) and not blob.name.endswith("/"):
                temp_file = Path("/tmp") / blob_path.name
                blob.download_to_filename(temp_file)
                files.append(temp_file)

        if not files:
            raise FileNotFoundError(f"Aucun fichier trouvé dans le dossier : {chemin_relatif}")
        return files


def get_file(chemin_relatif):
    """
    Récupère un fichier unique selon l'environnement actif et un chemin relatif.
    :param chemin_relatif: Chemin relatif d'un fichier unique (ex: "profil/sources/file.pdf").
    :return: Chemin local du fichier.
    """
    # Charger la configuration
    config = load_config()

    # Construire le chemin de base selon l'environnement
    if config.ENV in ["local", "dev"]:
        base_path = config.LOCAL_BASE_PATH if config.ENV == "local" else config.TEMP_PATH
        full_path = base_path / chemin_relatif
    elif config.ENV == "prod":
        full_path = Path("/tmp") / chemin_relatif
    else:
        raise ValueError(f"Environnement inconnu : {config.ENV}")

    # Gestion en mode "dev" et "prod" : téléchargement depuis le bucket
    if config.ENV in ["dev", "prod"]:
        storage_client = storage.Client()
        bucket = storage_client.bucket(config.BUCKET_NAME)
        blob = bucket.blob(chemin_relatif)
        
        if not blob.exists():
            raise FileNotFoundError(f"Le fichier spécifié n'existe pas dans le bucket : {chemin_relatif}")

        # Téléchargement du fichier vers /tmp
        temp_file = Path("/tmp") / Path(chemin_relatif).name
        blob.download_to_filename(temp_file)
        return temp_file

    # Environnements local : vérifier que le fichier existe
    if not full_path.exists() or not full_path.is_file():
        raise FileNotFoundError(f"Le fichier spécifié n'existe pas : {full_path}")

    return full_path


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

if __name__ == "__main__":
    # Exemple d'utilisation du get_file
    file_path = "j4WSNb5TuQVwVwSpq65N7o06GC52/cvs/cv1/head.json"
    file = get_file(file_path)
    print(file)