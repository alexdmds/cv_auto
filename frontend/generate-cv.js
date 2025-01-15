import { storage } from "./firebase-config.js";
import { ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-storage.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-auth.js";

// Extraire le nom du CV depuis l'URL
const params = new URLSearchParams(window.location.search);
const cvName = params.get("cv");

// Vérification de `cvName`
if (!cvName) {
  alert("Aucun CV spécifié. Veuillez vérifier l'URL.");
  throw new Error("Aucun CV spécifié.");
}

// Initialisation de la page
document.getElementById("cv-title").textContent = `Génération de CV : ${cvName}`;

// Gestion des boutons de navigation
document.getElementById("back-to-profile").addEventListener("click", () => {
  window.location.href = "./profil.html";
});

document.getElementById("back-to-cvs").addEventListener("click", () => {
  window.location.href = "./mes-cvs.html";
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

// Générer le CV en appelant le backend
document.getElementById("generate-cv").addEventListener("click", async () => {
  if (!auth.currentUser) {
    alert("Aucun utilisateur connecté. Veuillez vous connecter pour générer un CV.");
    return;
  }

  try {
    const userId = auth.currentUser.uid; // Identifier l'utilisateur connecté
    const idToken = await auth.currentUser.getIdToken(); // Obtenir le token Firebase ID

    const headers = new Headers();
    headers.append("Authorization", `Bearer ${idToken}`);
    headers.append("Content-Type", "application/json");

    const response = await fetch("https://backend-flask-177360827241.europe-west9.run.app/generate-cv", {
      method: "POST",
      headers: headers,
      body: JSON.stringify({
        profil: userId, // Profil utilisateur
        cv_name: cvName, // Nom du CV (pour correspondre au backend)
      }),
    });

    if (response.ok) {
      const data = await response.json();
      if (data && data.success) {
        document.getElementById("save-status").textContent = "CV généré avec succès.";
        alert("Le CV a été généré avec succès. Consultez le dossier Firebase pour le récupérer.");
      } else {
        alert("La génération du CV a échoué.");
      }
    } else {
      const error = await response.text();
      console.error("Erreur lors de la génération du CV :", error);
      alert("Une erreur est survenue lors de la génération du CV.");
    }
  } catch (error) {
    console.error("Erreur inattendue :", error);
    alert("Une erreur inattendue est survenue.");
  }
});