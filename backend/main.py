from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Bienvenue sur le backend Flask !"

@app.route("/process", methods=["POST"])
def process():
    # Exemple : Traitement des données reçues
    data = request.get_json()
    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400
    # Effectuez ici le traitement des données
    result = {"message": "Données traitées avec succès", "received": data}
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)