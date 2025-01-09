from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)
CORS(app)  # Active CORS pour toutes les routes

# Client ID Google
GOOGLE_CLIENT_ID = "177360827241-3g376bqaun1t2h5nhl8thnv5k9o64efh.apps.googleusercontent.com"

@app.route("/")
def home():
    return "Bienvenue sur le backend Flask pour l'authentification avec Google !"

@app.route("/auth", methods=["POST"])
def auth():
    try:
        # Récupérer le token envoyé par le frontend
        data = request.get_json()
        if not data or "id_token" not in data:
            return jsonify({"error": "Aucun token reçu"}), 400

        id_token_received = data["id_token"]

        # Valider le token avec Google
        decoded_token = id_token.verify_oauth2_token(
            id_token_received,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # Si le token est valide, extraire les informations de l'utilisateur
        user_info = {
            "id": decoded_token["sub"],
            "email": decoded_token["email"],
            "name": decoded_token.get("name", "Utilisateur"),
            "picture": decoded_token.get("picture", "")
        }

        return jsonify({"user": user_info}), 200

    except ValueError as e:
        # Le token est invalide
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)