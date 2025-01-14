import os
from pathlib import Path
import sys

class Config:
    ENV = os.getenv("ENV", "not_local")
    #ENV = os.getenv("ENV", "local")
    
    # Configuration OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SECRET_NAME = "projects/177360827241/secrets/OPENAI_API_KEY/versions/1"

    # Chemins locaux
    LOCAL_BASE_PATH = Path("data_local")
    LOCAL_PROMPT_PATH = Path(__file__).parent / "cv_automation/prompts"

    # Buckets Firebase Storage
    BUCKET_NAME = "cv-generator-447314.firebasestorage.app"
    TEMP_PATH = Path("/tmp")  # Chemin temporaire en backend