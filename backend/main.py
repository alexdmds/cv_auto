from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth

#importer les fonctions de cv_automation
from cv_automation.pdf_to_text import convert_source_pdf_to_txt
from cv_automation.profile_edu import profile_edu
from cv_automation.profile_exp import profile_exp
from cv_automation.profile_pers import profile_pers


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
    # Vérification du token Firebase ID
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authorization header missing or invalid"}), 401

    id_token = auth_header.split(" ")[1]

    try:
        # Vérifier et décoder le token
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]  # Récupérer l'UID utilisateur
    except Exception as e:
        return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401

    try:
        # Appeler les fonctions en utilisant l'UID utilisateur
        pdf_text = convert_source_pdf_to_txt(user_id)
        education = profile_edu(user_id)
        experience = profile_exp(user_id)
        personal_info = profile_pers(user_id)

        # Générer le profil complet
        profile = {
            "userID": user_id,
            "text_extraction": pdf_text,
            "education": education,
            "experience": experience,
            "personal_info": personal_info,
        }

        return jsonify({"success": True, "profile": profile}), 200

    except Exception as e:
        # Gérer les erreurs lors de l'exécution des fonctions
        return jsonify({"error": "Failed to generate profile", "details": str(e)}), 500
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)