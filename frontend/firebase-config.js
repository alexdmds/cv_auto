import { initializeApp } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-app.js";
import { getStorage } from "https://www.gstatic.com/firebasejs/9.21.0/firebase-storage.js";

// Configuration Firebase (remplacez avec vos paramètres Firebase)
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

// Exporter le stockage pour l'utiliser dans d'autres fichiers
export const storage = getStorage(app);