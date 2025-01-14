import { getAuth } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-auth.js";

const auth = getAuth();

export const generateProfile = () => {
  const generateButton = document.getElementById("generate-profile");
  const statusDiv = document.getElementById("generation-status");
  const outputDiv = document.getElementById("profile-output");

  generateButton.addEventListener("click", async () => {
    statusDiv.textContent = "Génération en cours...";
    outputDiv.textContent = "";

    try {
      const user = auth.currentUser;

      if (!user) {
        statusDiv.textContent = "Aucun utilisateur connecté. Veuillez vous connecter.";
        return;
      }

      // Obtenir le token Firebase ID
      const idToken = await user.getIdToken();

      // Construire l'en-tête d'autorisation
      const headers = new Headers();
      headers.append("Authorization", `Bearer ${idToken}`);
      headers.append("Content-Type", "application/json"); // Si un corps est nécessaire (facultatif ici)

      // Envoyer la requête HTTP
      const url = `https://backend-flask-177360827241.europe-west9.run.app/generate-profile`;
      const response = await fetch(url, {
        method: "POST", // Utilisation de POST au lieu de GET
        headers: headers,
      });

      if (!response.ok) {
        throw new Error(`Erreur : ${response.statusText}`);
      }

      // Affichage du JSON retourné
      const result = await response.json();
      statusDiv.textContent = "Profil généré avec succès.";
      outputDiv.textContent = JSON.stringify(result, null, 2);
    } catch (error) {
      console.error("Erreur lors de la génération du profil :", error);
      statusDiv.textContent = "Erreur lors de la génération du profil.";
    }
  });
};