import { initializeApp } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-auth.js";

// Configuration Firebase
const firebaseConfig = {
    apiKey: "AIzaSyD2ZmZ8y399YYyvUHWaKOux3tgAV4T6OLg",
    authDomain: "cv-generator-447314.firebaseapp.com",
    projectId: "cv-generator-447314",
    storageBucket: "cv-generator-447314.firebasestorage.app",
    messagingSenderId: "177360827241",
    appId: "1:177360827241:web:2eccbab9c11777f27203f8"
};

// Initialiser Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Vérifier l'état de connexion
onAuthStateChanged(auth, (user) => {
    if (user) {
        // Afficher le nom de l'utilisateur
        document.getElementById("welcome-message").textContent = `Bienvenue, ${user.displayName} !`;
    } else {
        // Rediriger si l'utilisateur n'est pas connecté
        window.location.href = "/frontend/index.html";
    }
});

// Déconnexion de l'utilisateur
document.getElementById("logout").addEventListener("click", async () => {
    try {
        await signOut(auth);
        alert("Vous avez été déconnecté.");
        window.location.href = "/frontend/index.html";
    } catch (error) {
        console.error("Erreur lors de la déconnexion :", error);
        alert("Une erreur est survenue lors de la déconnexion.");
    }
});