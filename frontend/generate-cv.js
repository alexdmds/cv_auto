import { storage } from "./firebase-config.js";
import { ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-storage.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-auth.js";

// Extraire le nom du CV depuis l'URL
const params = new URLSearchParams(window.location.search);
const cvName = params.get("cv");

// Initialisation de la page
document.getElementById("cv-title").textContent = `Génération de CV : ${cvName}`;

// Gestion des boutons de navigation
document.getElementById("back-to-profile").addEventListener("click", () => {
  window.location.href = "./profil.html"; // Retour à la page profil
});

document.getElementById("back-to-cvs").addEventListener("click", () => {
  window.location.href = "./mes-cvs.html"; // Retour à la page des CVs
});

// Référence Firebase pour la fiche de poste
let jobRef;

// Charger l'utilisateur connecté
const auth = getAuth();
onAuthStateChanged(auth, async (user) => {
  if (user) {
    const userId = user.uid;
    jobRef = ref(storage, `${userId}/cvs/${cvName}/source_raw.txt`);

    // Charger la fiche de poste si elle existe
    try {
      const jobURL = await getDownloadURL(jobRef);
      const response = await fetch(jobURL);
      if (response.ok) {
        const jobText = await response.text();
        document.getElementById("job-description").value = jobText;
      }
    } catch (error) {
      console.log("Aucune fiche de poste existante.");
    }
  } else {
    console.error("Aucun utilisateur connecté.");
  }
});

// Sauvegarder la fiche de poste
document.getElementById("save-job-description").addEventListener("click", async () => {
  const jobDescription = document.getElementById("job-description").value;
  if (!jobDescription) {
    document.getElementById("save-status").textContent = "Veuillez entrer une fiche de poste.";
    return;
  }

  try {
    const blob = new Blob([jobDescription], { type: "text/plain" });
    await uploadBytes(jobRef, blob);
    document.getElementById("save-status").textContent = "Fiche de poste sauvegardée avec succès.";
  } catch (error) {
    console.error("Erreur lors de la sauvegarde :", error);
    document.getElementById("save-status").textContent = "Erreur lors de la sauvegarde.";
  }
});

// Générer le CV (logique à définir plus tard)
document.getElementById("generate-cv").addEventListener("click", () => {
  alert(`Génération du CV pour ${cvName}...`);
});