import { storage } from "./firebase-config.js";
import { ref, uploadBytes, listAll, getDownloadURL, deleteObject } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-storage.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-auth.js";

const auth = getAuth();

onAuthStateChanged(auth, (user) => {
  if (user) {
    const userName = user.displayName || "Utilisateur";
    document.getElementById("welcome-message").textContent = `Bienvenue, ${userName}!`;

    const fileList = document.getElementById("file-list");

    // Fonction pour lister les fichiers
    const listFiles = async () => {
      const userFolderRef = ref(storage, `${user.uid}/sources/`);
      try {
        // Lister les fichiers dans le répertoire de l'utilisateur
        const result = await listAll(userFolderRef);

        // Effacer la liste actuelle
        fileList.innerHTML = "";

        // Afficher chaque fichier
        for (const itemRef of result.items) {
          const fileURL = await getDownloadURL(itemRef);
          const li = document.createElement("li");
          li.textContent = itemRef.name;

          // Ajouter un bouton "Supprimer"
          const deleteButton = document.createElement("button");
          deleteButton.textContent = "Supprimer";
          deleteButton.style.marginLeft = "10px";

          // Ajouter un événement pour supprimer le fichier
          deleteButton.addEventListener("click", async () => {
            try {
              await deleteObject(itemRef);
              listFiles(); // Rafraîchir la liste après suppression
              alert(`Fichier ${itemRef.name} supprimé avec succès.`);
            } catch (error) {
              console.error("Erreur lors de la suppression :", error);
              alert("Erreur lors de la suppression du fichier.");
            }
          });

          li.appendChild(deleteButton);
          fileList.appendChild(li);
        }
      } catch (error) {
        console.error("Erreur lors de la récupération des fichiers :", error);
        fileList.innerHTML = "<li>Impossible de récupérer les fichiers.</li>";
      }
    };

    // Appeler la fonction pour afficher les fichiers au chargement
    listFiles();

    // Gestion de l'upload des fichiers
    document.getElementById("upload-button").addEventListener("click", async () => {
      const fileInput = document.getElementById("file-uploader");
      const file = fileInput.files[0];

      if (!file) {
        document.getElementById("upload-status").textContent = "Aucun fichier sélectionné.";
        return;
      }

      if (file.type !== "application/pdf") {
        alert("Seuls les fichiers PDF sont autorisés.");
        return;
      }

      try {
        // Référence à l'emplacement dans le bucket Firebase Storage
        const fileRef = ref(storage, `${user.uid}/sources/${file.name}`);

        // Upload du fichier
        await uploadBytes(fileRef, file);

        // Rafraîchir la liste des fichiers
        listFiles();

        document.getElementById("upload-status").textContent = `Fichier ${file.name} uploadé avec succès.`;
      } catch (error) {
        console.error(error);
        document.getElementById("upload-status").textContent = "Erreur lors de l'upload.";
      }
    });
  } else {
    document.getElementById("welcome-message").textContent = "Aucun utilisateur connecté.";
  }
});