import json
from pathlib import Path
from google.cloud import storage
from config import load_config



def get_file(chemin_relatif):
    """
    Récupère un ou plusieurs fichiers selon l'environnement actif et un chemin relatif ou un motif.
    :param chemin_relatif: Chemin relatif ou motif de fichiers (ex: "profil/sources/*.pdf").
    :return: Liste des chemins correspondants ou contenu si un seul fichier est trouvé.
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
        blobs = list(bucket.list_blobs(prefix=Path(chemin_relatif).parent))
        downloaded_files = []
        for blob in blobs:
            if blob.name.endswith(Path(chemin_relatif).suffix):  # Filtrer selon l'extension
                temp_file = Path("/tmp") / Path(blob.name).name
                blob.download_to_filename(temp_file)
                downloaded_files.append(temp_file)
        if not downloaded_files:
            raise FileNotFoundError(f"Aucun fichier trouvé correspondant au motif : {chemin_relatif}")
        return downloaded_files

    # Environnements local : utiliser glob pour matcher les fichiers
    files = list(Path(full_path.parent).glob(full_path.name))
    if not files:
        raise FileNotFoundError(f"Aucun fichier trouvé correspondant au motif : {chemin_relatif}")
    return files if len(files) > 1 else files[0]


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
        file_path.parent.mkdir(parents=True, exist_ok=True)
    elif config.ENV in ["prod", "dev"]:
        file_path = Path("/tmp") / Path(chemin_relatif).name
    else:
        raise ValueError(f"Environnement inconnu : {config.ENV}")

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
        
        # Convertir le contenu en chaîne pour JSON ou texte
        if isinstance(content, dict):  # JSON
            content_str = json.dumps(content, indent=4)  # Convertir le dictionnaire en chaîne
            content_type = "application/json"
        elif isinstance(content, str):  # Texte brut
            content_str = content
            content_type = "text/plain"
        else:  # Contenu binaire
            content_str = content
            content_type = "application/octet-stream"

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
    # Exemple d'utilisation du save_file
    save_file("j4WSNb5TuQVwVwSpq65N7o06GC52/profil/edu.json", {"name": "John Doe", "age": 25})