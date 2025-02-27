import os
from pathlib import Path
from google.cloud import secretmanager

import logging

def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,  # Capture tous les niveaux de log
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()  # Affiche tout dans la console
        ]
    )

    # S'assurer que le logger racine capture tout
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Configurer les modules tiers et enfants
    logging.getLogger("werkzeug").setLevel(logging.INFO)  # Ajustez si nécessaire
    logging.getLogger("cv_automation").setLevel(logging.DEBUG)


class BaseConfig:
    # Valeurs communes à tous les environnements
    TEMP_PATH = Path("/tmp")  # Chemin temporaire
    BUCKET_NAME = "cv-generator-447314.firebasestorage.app"
    ENV = None
    OPENAI_API_KEY = None
    CHECK_AUTH = True  # Valeur par défaut

class LocalConfig(BaseConfig):
    ENV = "local"
    MOCK_OPENAI = True
    CHECK_AUTH = False  # Désactive l'authentification en dev

class DevConfig(BaseConfig):
    ENV = "dev"
    MOCK_OPENAI = False
    CHECK_AUTH = False
    secret_manager_client = secretmanager.SecretManagerServiceClient()
    response = secret_manager_client.access_secret_version(request={"name": "projects/177360827241/secrets/OPENAI_API_KEY/versions/1"})
    OPENAI_API_KEY = response.payload.data.decode("UTF-8")

class ProdConfig(BaseConfig):
    ENV = "prod"
    MOCK_OPENAI = False
    CHECK_AUTH = True  # Active l'authentification en prod
    secret_manager_client = secretmanager.SecretManagerServiceClient()
    response = secret_manager_client.access_secret_version(request={"name": "projects/177360827241/secrets/OPENAI_API_KEY/versions/1"})
    OPENAI_API_KEY = response.payload.data.decode("UTF-8")

def load_config():
    env = os.getenv("ENV", "local")
    if env == "prod":
        return ProdConfig()
    elif env == "local":
        return LocalConfig()
    else:
        return DevConfig()
