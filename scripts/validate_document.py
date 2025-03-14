#!/usr/bin/env python3
import json
import sys

def valider_structure(doc, schema, chemin=""):
    erreurs = []
    # Si le schéma attend un dictionnaire
    if isinstance(schema, dict):
        if not isinstance(doc, dict):
            erreurs.append(f"À '{chemin or 'racine'}': attendu dict, obtenu {type(doc).__name__}")
        else:
            # Vérifier que chaque clé du schéma est présente dans le document
            for clé, sous_schema in schema.items():
                nouveau_chemin = f"{chemin}.{clé}" if chemin else clé
                if clé not in doc:
                    erreurs.append(f"Clé manquante '{clé}' à '{chemin or 'racine'}'")
                else:
                    erreurs.extend(valider_structure(doc[clé], sous_schema, nouveau_chemin))
            # Optionnel : avertir en cas de clés supplémentaires non définies dans le schéma
            for clé in doc:
                if clé not in schema:
                    erreurs.append(f"Clé inattendue '{clé}' à '{chemin or 'racine'}'")
    # Si le schéma attend une liste
    elif isinstance(schema, list):
        if not isinstance(doc, list):
            erreurs.append(f"À '{chemin}': attendu list, obtenu {type(doc).__name__}")
        else:
            if len(schema) == 0:
                return erreurs
            # Utiliser le premier élément du schéma comme modèle pour chaque élément de la liste
            modèle = schema[0]
            for i, élément in enumerate(doc):
                erreurs.extend(valider_structure(élément, modèle, f"{chemin}[{i}]"))
    # Cas des valeurs de base (ex : chaîne, entier...)
    else:
        if not isinstance(doc, type(schema)):
            erreurs.append(f"À '{chemin}': attendu {type(schema).__name__}, obtenu {type(doc).__name__}")
    return erreurs

def main():
    # Saisie interactive des paramètres
    collection = input("Entrez le nom de la collection (users, calls ou usage) : ").strip()
    doc_id = input("Entrez l'ID du document : ").strip()

    # Charger le schéma depuis le fichier firestore_schema.json
    try:
        with open("firestore_schema.json", "r", encoding="utf-8") as f:
            schema_data = json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement du schéma : {e}")
        sys.exit(1)

    if collection not in schema_data:
        print(f"La collection '{collection}' n'est pas définie dans le schéma.")
        sys.exit(1)
    schema_attendu = schema_data[collection]

    # Connexion à Firestore via firebase_admin
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError:
        print("Le module firebase_admin n'est pas installé. Installez-le via 'pip install firebase-admin'")
        sys.exit(1)

    # Initialisation de l'application Firebase (en supposant une configuration par défaut ou via GOOGLE_APPLICATION_CREDENTIALS)
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    # Récupérer le document dans la collection spécifiée
    doc_ref = db.collection(collection).document(doc_id)
    doc_snapshot = doc_ref.get()
    if not doc_snapshot.exists:
        print(f"Document '{doc_id}' non trouvé dans la collection '{collection}'.")
        sys.exit(1)
    doc_data = doc_snapshot.to_dict()

    # Valider la structure du document par rapport au schéma
    erreurs = valider_structure(doc_data, schema_attendu)
    if erreurs:
        print("Validation de la structure du document échouée :")
        for err in erreurs:
            print(" -", err)
    else:
        print("La structure du document est conforme au schéma.")

if __name__ == "__main__":
    main()