// Importer Firebase
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";
import { getAuth, signInWithPopup, GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-auth.js";

// Configuration Firebase
const firebaseConfig = {
  apiKey: "AIzaSyD2ZmZ8y399YYyvUHWaKOux3tgAV4T6OLg",
  authDomain: "cv-generator-447314.firebaseapp.com",
  projectId: "cv-generator-447314",
  storageBucket: "cv-generator-447314.firebasestorage.app",
  messagingSenderId: "177360827241",
  appId: "1:177360827241:web:2eccbab9c11777f27203f8"
};

// Initialisation Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

// Gestion de la connexion Google
document.addEventListener("DOMContentLoaded", () => {
  const loginButton = document.getElementById("login-google");

  if (loginButton) {
    loginButton.addEventListener("click", async () => {
      try {
        const result = await signInWithPopup(auth, provider);
        const user = result.user;

        console.log("Utilisateur connecté :", user);

        // Sauvegarder le nom de l'utilisateur dans localStorage
        localStorage.setItem("userName", user.displayName);

        // Rediriger vers la page profil.html
        window.location.href = "profil.html";
      } catch (error) {
        console.error("Erreur de connexion :", error);
        alert("Une erreur est survenue lors de la connexion.");
      }
    });
  } else {
    console.error("Le bouton de connexion Google est introuvable.");
  }
});