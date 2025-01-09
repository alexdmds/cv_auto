import subprocess
import os

def run_cv_automation(profil, cv):
    """
    Orchestrer les scripts dans cv_automation en fonction du profil et du CV.

    Args:
        profil (str): Nom du profil.
        cv (str): Nom du CV.
    """
    # Définir le chemin vers cv_automation
    cv_automation_path = "./cv_automation"

    # Liste des scripts à exécuter dans l'ordre
    scripts = [
        "preprocess_data.py",  # Exemple : Prétraitement des données
        "call_openai.py",      # Exemple : Appel à l'API OpenAI
        "generate_pdf.py"      # Exemple : Génération du PDF
    ]

    for script in scripts:
        script_path = os.path.join(cv_automation_path, script)

        # Vérifier si le script existe
        if not os.path.exists(script_path):
            print(f"Le script {script} est introuvable. Vérifiez sa présence.")
            continue

        # Construire la commande
        command = ["python", script_path, profil, cv]

        try:
            # Exécuter le script
            print(f"Exécution du script : {script}")
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution du script {script}: {e}")
            break
        except Exception as e:
            print(f"Une erreur inattendue est survenue : {e}")
            break

    print("Tous les scripts ont été exécutés.")

# Exemple d'utilisation
if __name__ == "__main__":
    profil = "Alexis1"
    cv = "cv1"
    run_cv_automation(profil, cv)