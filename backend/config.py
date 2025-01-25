import os
from pathlib import Path
from google.cloud import secretmanager

class BaseConfig:
    # Valeurs communes à tous les environnements
    LOCAL_PROMPT_PATH = Path(__file__).parent / "cv_automation/prompts"
    TEMP_PATH = Path("/tmp")  # Chemin temporaire
    LOCAL_BASE_PATH = Path("data_local")  # Données locales par défaut

    # Placeholder pour les variables spécifiques
    ENV = None
    BUCKET_NAME = None
    OPENAI_API_KEY = None

class LocalConfig(BaseConfig):
    ENV = "local"
    BUCKET_NAME = None  # Pas de bucket en local
    OPENAI_API_KEY = OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class DevConfig(BaseConfig):
    ENV = "dev"
    BUCKET_NAME = "cv-generator-447314.firebasestorage.app"
    OPENAI_API_KEY = OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ProdConfig(BaseConfig):
    ENV = "prod"
    BUCKET_NAME = "cv-generator-447314.firebasestorage.app"
    secret_manager_client = secretmanager.SecretManagerServiceClient()
    response = secret_manager_client.access_secret_version(request={"name": "projects/177360827241/secrets/OPENAI_API_KEY/versions/1"})
    OPENAI_API_KEY = response.payload.data.decode("UTF-8")

def load_config():
    env = os.getenv("ENV", "local")
    if env == "dev":
        return DevConfig()
    elif env == "prod":
        return ProdConfig()
    else:
        return LocalConfig()