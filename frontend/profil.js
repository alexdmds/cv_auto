import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-auth.js";
import { storage } from "./firebase-config.js";
import { ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-storage.js";

const auth = getAuth();

onAuthStateChanged(auth, (user) => {
  if (user) {
    const userName = user.displayName || "Utilisateur";
    document.getElementById("welcome-message").textContent = `Bienvenue, ${userName}!`;

    document.getElementById("upload-button").addEventListener("click", async () => {
      const fileInput = document.getElementById("file-uploader");
      const file = fileInput.files[0];

      if (!file) {
        document.getElementById("upload-status").textContent = "Aucun fichier sélectionné.";
        return;
      }

      try {
        // Référence à l'emplacement dans le bucket Firebase Storage
        const fileRef = ref(storage, `${user.uid}/${file.name}`);

        // Upload du fichier
        await uploadBytes(fileRef, file);

        // Récupérer l'URL de téléchargement
        const downloadURL = await getDownloadURL(fileRef);
        document.getElementById("upload-status").textContent = `Fichier uploadé avec succès : ${downloadURL}`;
      } catch (error) {
        console.error(error);
        document.getElementById("upload-status").textContent = "Erreur lors de l'upload.";
      }
    });
  } else {
    document.getElementById("welcome-message").textContent = "Aucun utilisateur connecté.";
  }
});