from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_init import db
from firebase_admin import auth

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
from cv_automation.get_hobbies import get_hobbies
from cv_automation.agg_data_cv import aggregate_json_files
from cv_automation.gen_pdf.main import build_pdf

from utils import can_user_proceed

import logging
import asyncio

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

@app.route("/")
def home():
    return "Bienvenue sur le backend Flask avec Firebase !"

@app.route("/generate-profile", methods=["POST"])
async def generate_profile():
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

    # Vérifier si l'utilisateur peut poursuivre
    if not can_user_proceed(user_id):
        logger.warning("L'utilisateur ne peut pas poursuivre")
        return jsonify({"error": "User cannot proceed"}), 403

    try:
        # Appeler les fonctions en utilisant l'UID utilisateur
        logger.debug(f"Lancement du traitement pour l'utilisateur {user_id}")
        convert_source_pdf_to_txt(user_id)
        # Appeler les fonctions asynchrones en parallèle
        logger.debug("Lancement des analyses en parallèle")
        await asyncio.gather(
            profile_edu(user_id),
            profile_exp(user_id),
            profile_pers(user_id),
        )
        logger.info(f"Profil généré avec succès pour l'utilisateur {user_id}")

        logger.info(f"Profil généré avec succès pour l'utilisateur {user_id}")
        return jsonify({"success": True}), 200

    except Exception as e:
        # Gérer les erreurs lors de l'exécution des fonctions
        logger.error("Erreur lors de la génération du profil", exc_info=True)
        return jsonify({"error": "Failed to generate profile", "details": str(e)}), 500
    
@app.route("/generate-cv", methods=["POST"])
def generate_cv():
    logger.debug("Requête reçue sur /generate-cv")

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

    # Vérifier si l'utilisateur peut poursuivre
    if not can_user_proceed(user_id):
        logger.warning("L'utilisateur ne peut pas poursuivre")
        return jsonify({"error": "User cannot proceed"}), 403
    try:
        # Appeler les fonctions en utilisant l'UID utilisateur et le cv_name
        logger.debug(f"Lancement du traitement pour l'utilisateur {user_id}")
        refine_job_description(user_id, cv_name)
        logger.info("Description de poste raffinée")
        get_head(user_id, cv_name)
        logger.info("En-tête récupéré")
        get_exp(user_id, cv_name)
        logger.info("Expériences professionnelles récupérées")
        get_edu(user_id, cv_name)
        logger.info("Formations récupérées")
        get_skills(user_id, cv_name)
        logger.info("Compétences techniques récupérées")
        get_hobbies(user_id, cv_name)
        logger.info("Centres d'intérêt récupérés")
        aggregate_json_files(user_id, cv_name)
        logger.info("Données agrégées")
        build_pdf(user_id, cv_name)
        logger.info("CV généré")

        return jsonify({"success": True}), 200

    except Exception as e:
        # Gérer les erreurs lors de l'exécution des fonctions
        logger.error("Erreur lors de la génération du profil", exc_info=True)
        return jsonify({"error": "Failed to generate profile", "details": str(e)}), 500


@app.route("/get-total-tokens", methods=["GET"])
def get_total_tokens():
    """
    Endpoint pour récupérer le nombre total de tokens d'un utilisateur.
    """
    logger.debug("Requête reçue sur /get-total-tokens")

    # Récupérer l'ID utilisateur depuis les paramètres de la requête
    user_id = request.args.get("user_id")
    if not user_id:
        logger.warning("Paramètre user_id manquant")
        return jsonify({"error": "Missing user_id parameter"}), 400

    try:
        # Référence Firebase pour l'utilisateur
        user_ref = db.reference(f"users/{user_id}")
        user_data = user_ref.get()

        if not user_data or "total_tokens" not in user_data:
            logger.warning(f"Aucun total_tokens trouvé pour l'utilisateur {user_id}")
            return jsonify({"user_id": user_id, "total_tokens": 0}), 200

        # Retourner le total des tokens
        total_tokens = user_data["total_tokens"]
        logger.info(f"Total des tokens récupéré pour l'utilisateur {user_id}: {total_tokens}")
        return jsonify({"user_id": user_id, "total_tokens": total_tokens}), 200

    except Exception as e:
        logger.error("Erreur lors de la récupération du total des tokens", exc_info=True)
        return jsonify({"error": "Failed to retrieve total_tokens", "details": str(e)}), 500
    
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)