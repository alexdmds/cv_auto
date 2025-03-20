#!/usr/bin/env python3
import sys
import firebase_admin
from firebase_admin import credentials, firestore

def main():
    # Initialisation de l'application Firebase
    try:
        firebase_admin.get_app()
    except ValueError:
        # Utilisation des identifiants par défaut (assurez-vous que GOOGLE_APPLICATION_CREDENTIALS est configuré)
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()

    # Saisie interactive de l'ID du document source et de destination
    source_doc_id = input("Entrez l'ID du document à copier dans la collection 'users' : ").strip()
    dest_doc_id = input("Entrez l'ID du nouveau document dans la collection 'users' : ").strip()

    # Récupération du document source
    source_ref = db.collection("users").document(source_doc_id)
    source_doc = source_ref.get()
    if not source_doc.exists:
        print(f"Le document '{source_doc_id}' n'existe pas dans la collection 'users'.")
        sys.exit(1)
    data = source_doc.to_dict()

    # Vérifier si le document de destination existe déjà
    dest_ref = db.collection("users").document(dest_doc_id)
    if dest_ref.get().exists:
        confirmation = input(f"Le document '{dest_doc_id}' existe déjà. Voulez-vous l'écraser ? (oui/non) : ").strip().lower()
        if confirmation != "oui":
            print("Opération annulée.")
            sys.exit(0)

    # Copier le document dans le nouveau document
    dest_ref.set(data)
    print(f"Le document '{source_doc_id}' a été copié vers '{dest_doc_id}' dans la collection 'users'.")

if __name__ == "__main__":
    main()