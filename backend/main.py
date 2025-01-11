from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)

# Ajouter la gestion des CORS
CORS(app)

# Initialiser Firebase Admin avec les ADC
firebase_admin.initialize_app()

@app.route("/")
def home():
    return "Bienvenue sur le backend Flask avec Firebase !"

@app.route("/auth", methods=["POST"])
def authenticate():
    try:
        # Récupérer le token envoyé par le frontend
        data = request.get_json()
        if not data or "id_token" not in data:
            return jsonify({"error": "Aucun token reçu"}), 400

        id_token = data["id_token"]

        # Vérifier le token avec Firebase
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]

        # Envoyer les informations utilisateur
        return jsonify({"message": "Authentification réussie", "user_id": user_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)