import { storage } from "./firebase-config.js";
import { ref, uploadBytes, listAll, getDownloadURL, deleteObject } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-storage.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-auth.js";

const auth = getAuth();

onAuthStateChanged(auth, (user) => {
  if (user) {
    const userName = user.displayName || "Utilisateur";
    document.getElementById("welcome-message").textContent = `Bienvenue, ${userName}!`;

    const fileList = document.getElementById("file-list");
    const userInfo = document.getElementById("user-info");
    const infoStatus = document.getElementById("info-status");

    // Référence pour le fichier texte
    const infoFileRef = ref(storage, `${user.uid}/sources/infos.txt`);

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

    // Fonction pour charger le contenu du fichier texte
    const loadUserInfo = async () => {
        try {
            // Tente d'obtenir l'URL du fichier
            const infoURL = await getDownloadURL(infoFileRef);
    
            // Récupère le contenu du fichier en une seule étape
            const response = await fetch(infoURL);
            if (response.ok) {
                const text = await response.text(); // Lit le contenu du fichier
                userInfo.value = text;             // Remplit la zone de texte
            } else {
                console.log("Aucun fichier infos.txt encore existant");
                userInfo.value = ""; // Si aucune info, on laisse la zone de texte vide
            }
        } catch (error) {
            // Vérifie si l'erreur est liée à un fichier manquant
            if (error.code === 'storage/object-not-found' || error.message.includes('404')) {
                console.log("Aucun fichier infos.txt encore existant");
                userInfo.value = ""; // Zone de texte vide si aucune info
            } else {
                console.error("Erreur lors du chargement :", error);
            }
        }
    };
    // Appeler la fonction pour afficher les fichiers et charger le texte au chargement
    listFiles();
    loadUserInfo();

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
    // Gestion de la sauvegarde du texte
    document.getElementById("save-info").addEventListener("click", async () => {
        const infoText = userInfo.value;
  
        try {
          const textBlob = new Blob([infoText], { type: "text/plain" });
          await uploadBytes(infoFileRef, textBlob);
          infoStatus.textContent = "Informations sauvegardées avec succès.";
        } catch (error) {
          console.error("Erreur lors de la sauvegarde des informations :", error);
          infoStatus.textContent = "Erreur lors de la sauvegarde des informations.";
        }
      });
  } else {
    document.getElementById("welcome-message").textContent = "Aucun utilisateur connecté.";
  }
});