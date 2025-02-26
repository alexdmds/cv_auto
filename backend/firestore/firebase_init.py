import firebase_admin
from firebase_admin import credentials, db

# Vérifie si Firebase n'est pas déjà initialisé pour éviter les conflits
if not firebase_admin._apps:
    firebase_admin.initialize_app(
        options={
            "databaseURL": "https://cv-generator-447314-default-rtdb.europe-west1.firebasedatabase.app/"
        }
    )