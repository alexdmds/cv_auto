import { storage } from "./firebase-config.js";
import { ref, listAll } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-storage.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-auth.js";

// Fonction pour récupérer les CVs d'un utilisateur
async function fetchCVs(userId) {
  const cvPath = `${userId}/cvs/`;
  const listRef = ref(storage, cvPath);
  const cvList = document.getElementById("cv-list");

  try {
    const res = await listAll(listRef);

    if (res.prefixes.length === 0 && res.items.length === 0) {
      displayNoCVMessage();
      return;
    }

    // Parcourir les préfixes (dossiers)
    for (const folderRef of res.prefixes) {
      const li = document.createElement("li");
      li.textContent = folderRef.name;

      // Ajouter un bouton pour accéder à la page de génération du CV
      const viewButton = document.createElement("button");
      viewButton.textContent = "Ouvrir";
      viewButton.addEventListener("click", () => {
        // Redirection vers la page generate-cv.html avec le nom du CV
        window.location.href = `./generate-cv.html?cv=${folderRef.name}`;
      });

      li.appendChild(viewButton);
      cvList.appendChild(li);
    }
  } catch (error) {
    console.error("Erreur lors de la récupération des CVs :", error);
    displayErrorMessage();
  }
}

// Afficher un message s'il n'y a aucun CV
function displayNoCVMessage() {
  const cvList = document.getElementById("cv-list");
  cvList.innerHTML = "<li>Aucun CV généré pour l'instant.</li>";
}

// Afficher un message d'erreur
function displayErrorMessage() {
  const cvList = document.getElementById("cv-list");
  cvList.innerHTML = "<li>Erreur lors de la récupération des CVs.</li>";
}

// Charger la liste des CVs après authentification
const auth = getAuth();
onAuthStateChanged(auth, (user) => {
  if (user) {
    fetchCVs(user.uid);
  } else {
    console.error("Aucun utilisateur connecté.");
  }
});