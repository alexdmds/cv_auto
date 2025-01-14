import openai
from google.cloud import storage, secretmanager
from pathlib import Path

def get_openai_api_key(env, config):
    if env == "local":
        if not config.OPENAI_API_KEY:
            raise ValueError("La clé API OpenAI n'est pas définie dans les variables d'environnement.")
        return config.OPENAI_API_KEY
    else:
        # Récupérer la clé OpenAI depuis Secret Manager
        secret_manager_client = secretmanager.SecretManagerServiceClient()
        response = secret_manager_client.access_secret_version(request={"name": config.SECRET_NAME})
        return response.payload.data.decode("UTF-8")

def download_files_from_bucket(bucket_name, prefix, destination):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)

    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    for blob in blobs:
        if blob.name.endswith(".txt") or blob.name.endswith(".pdf"):
            blob.download_to_filename(destination / Path(blob.name).name)

def upload_to_bucket(bucket_name, destination_path, content):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_path)
    blob.upload_from_string(content, content_type="text/plain")

def save_text_to_file(exp_output, text):
    # Créer le chemin si nécessaire
    file_path = Path(exp_output)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Enregistrer le contenu dans le fichier cible
    file_path.write_text(text, encoding="utf-8")