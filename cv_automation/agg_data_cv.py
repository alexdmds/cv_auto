import json
import os
import sys
from pathlib import Path

def aggregate_json_files(profil, cv):
    # Chemin de base
    base_path = Path(f"data_local/{profil}/cvs/{cv}")
    if not base_path.exists():
        raise FileNotFoundError(f"Le chemin spécifié n'existe pas : {base_path}")

    # Liste des fichiers JSON avec leurs clés
    input_files = [
        {"key": "head", "file": base_path / "head.json"},
        {"key": "experiences", "file": base_path / "exp.json"},
        {"key": "education", "file": base_path / "edu.json"},
        {"key": "skills", "file": base_path / "skills.json"},
        {"key": "hobbies", "file": base_path / "hobbies.json"}
    ]

    # Conteneur pour les données agrégées
    aggregated_data = {}

    # Agrégation des fichiers JSON
    for file_info in input_files:
        key = file_info["key"]
        file_path = file_info["file"]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                aggregated_data[key] = data
        except FileNotFoundError:
            print(f"Fichier non trouvé : {file_path}. Ignoré.")
        except json.JSONDecodeError as e:
            print(f"Erreur de format JSON dans {file_path}: {e}. Ignoré.")

    # Chemin de sortie pour le fichier agrégé
    output_file = base_path / "data_cv.json"
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(aggregated_data, outfile, indent=4, ensure_ascii=False)

    print(f"Les données agrégées ont été sauvegardées dans {output_file}")

if __name__ == "__main__":

    profil = "Alexis1"
    cv = "poste1"

    # Appel de la fonction principale
    try:
        aggregate_json_files(profil, cv)
    except Exception as e:
        print(f"Erreur : {e}")
        sys.exit(1)