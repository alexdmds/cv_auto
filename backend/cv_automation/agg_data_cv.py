import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
ROOT_DIR = Path(__file__).resolve().parent.parent  # Chemin vers 'backend'
sys.path.append(str(ROOT_DIR))

import json
from utils import get_file, save_file

def aggregate_json_files(profil, cv):
    """
    Agrège les données JSON d'un CV et sauvegarde le résultat dans un fichier unique.

    :param profil: Nom du profil (sous-dossier dans `data_local`).
    :param cv: Nom du CV (sous-dossier dans `profil/cvs`).
    """
    # Chemin de base pour les fichiers JSON
    base_path = f"{profil}/cvs/{cv}"

    # Liste des fichiers JSON avec leurs clés
    input_files = [
        {"key": "head", "file": f"{base_path}/head.json"},
        {"key": "experiences", "file": f"{base_path}/exp.json"},
        {"key": "education", "file": f"{base_path}/edu.json"},
        {"key": "skills", "file": f"{base_path}/skills.json"},
        {"key": "hobbies", "file": f"{base_path}/hobbies.json"}
    ]

    # Conteneur pour les données agrégées
    aggregated_data = {}

    # Agrégation des fichiers JSON
    for file_info in input_files:
        key = file_info["key"]
        file_path = file_info["file"]
        print(f"Traitement du fichier : {file_path}")

        try:
            # Récupérer le fichier depuis les environnements via `get_file`
            file = get_file(file_path)  # La nouvelle version de `get_file` gère les fichiers uniques

            print(f"Chargement du fichier : {file}")

            # Charger le contenu du fichier JSON
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Contenu du fichier {file_path} : {data}")
                aggregated_data[key] = data
        except FileNotFoundError:
            print(f"Fichier non trouvé : {file_path}. Ignoré.")
        except json.JSONDecodeError as e:
            print(f"Erreur de format JSON dans {file_path}: {e}. Ignoré.")

    # Chemin de sortie pour le fichier agrégé
    output_file_path = f"{base_path}/data_cv.json"

    # Sauvegarder les données agrégées
    save_file(output_file_path, aggregated_data)
    print(f"Les données agrégées ont été sauvegardées dans : {output_file_path}")


if __name__ == "__main__":
    profil = "j4WSNb5TuQVwVwSpq65N7o06GC52"
    cv = "cv1"

    # Appel de la fonction principale
    try:
        aggregate_json_files(profil, cv)
    except Exception as e:
        print(f"Erreur : {e}")
        sys.exit(1)
