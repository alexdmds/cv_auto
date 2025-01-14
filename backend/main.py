from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth

#importer les fonctions de cv_automation
from cv_automation.pdf_to_text import convert_source_pdf_to_txt
from cv_automation.profile_edu import profile_edu
from cv_automation.profile_exp import profile_exp
from cv_automation.profile_pers import profile_pers
from cv_automation.refine_post import refine_job_description
from cv_automation.get_head import get_head
from cv_automation.get_exp import get_exp
from cv_automation.get_edu import get_edu
from cv_automation.get_skills import get_skills

import logging

# Configurer le logger
logging.basicConfig(
    level=logging.DEBUG,  # Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()  # Envoyer les logs à la sortie standard
    ]
)

logger = logging.getLogger(__name__)


app = Flask(__name__)

# Ajouter la gestion des CORS
CORS(app)

# Initialiser Firebase Admin avec les ADC
firebase_admin.initialize_app()

@app.route("/")
def home():
    return "Bienvenue sur le backend Flask avec Firebase !"

@app.route("/generate-profile", methods=["POST"])
def generate_profile():
    logger.debug("Requête reçue sur /generate-profile")

    # Vérification du token Firebase ID
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Authorization header is missing or invalid")
        return jsonify({"error": "Authorization header missing or invalid"}), 401

    id_token = auth_header.split(" ")[1]

    try:
        # Vérifier et décoder le token
        logger.debug("Vérification du token Firebase ID")
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]  # Récupérer l'UID utilisateur
        logger.info(f"Token décodé avec succès. UID utilisateur : {user_id}")
    except Exception as e:
        logger.error("Erreur de validation du token Firebase", exc_info=True)
        return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401

    try:
        # Appeler les fonctions en utilisant l'UID utilisateur
        logger.debug(f"Lancement du traitement pour l'utilisateur {user_id}")
        convert_source_pdf_to_txt(user_id)
        logger.info("Conversion des PDFs terminée")
        profile_edu(user_id)
        logger.info("Profil éducatif généré")
        profile_exp(user_id)
        logger.info("Profil professionnel généré")
        profile_pers(user_id)
        logger.info("Profil personnel généré")

        logger.info(f"Profil généré avec succès pour l'utilisateur {user_id}")
        return jsonify({"success": True}), 200

    except Exception as e:
        # Gérer les erreurs lors de l'exécution des fonctions
        logger.error("Erreur lors de la génération du profil", exc_info=True)
        return jsonify({"error": "Failed to generate profile", "details": str(e)}), 500
    
@app.route("/generate-cv", methods=["POST"])
def generate_profile():
    logger.debug("Requête reçue sur /generate-profile")

    # Vérification du token Firebase ID
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Authorization header is missing or invalid")
        return jsonify({"error": "Authorization header missing or invalid"}), 401

    id_token = auth_header.split(" ")[1]

    try:
        # Vérifier et décoder le token
        logger.debug("Vérification du token Firebase ID")
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]  # Récupérer l'UID utilisateur
        logger.info(f"Token décodé avec succès. UID utilisateur : {user_id}")
    except Exception as e:
        logger.error("Erreur de validation du token Firebase", exc_info=True)
        return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401

    #recuperer le nom du cv a generer
    cv_name = request.json.get("cv_name")

    try:
        # Appeler les fonctions en utilisant l'UID utilisateur et le cv_name
        logger.debug(f"Lancement du traitement pour l'utilisateur {user_id}")



        return jsonify({"success": True}), 200

    except Exception as e:
        # Gérer les erreurs lors de l'exécution des fonctions
        logger.error("Erreur lors de la génération du profil", exc_info=True)
        return jsonify({"error": "Failed to generate profile", "details": str(e)}), 500
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)