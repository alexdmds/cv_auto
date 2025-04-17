import { db, auth } from "./firebase-init.js";

window.addEventListener('load', async () => {
  // attendre que l'utilisateur soit connecté
  auth.onAuthStateChanged(async (user) => {
    if (user) {
      const userDoc = await db.collection('users').doc(user.uid).get();
      const data = userDoc.data();
      if (data) {
        console.log('Données utilisateur:', data);
        // Exemple : remplir un formulaire
        document.querySelector('input[name="prenom"]').value = data.firstName || "";
        document.querySelector('input[name="nom"]').value = data.lastName || "";
        document.querySelector('input[name="email"]').value = data.email || "";
      }
    }
  });
}); 