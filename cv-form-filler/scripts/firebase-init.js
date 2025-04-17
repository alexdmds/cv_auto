import { initializeApp } from 'firebase/app';
import { getAuth, signInWithCredential, GoogleAuthProvider } from 'firebase/auth/web-extension';
import { getFirestore } from 'firebase/firestore/lite';

// Configuration Firebase
const firebaseConfig = {
  apiKey: "AIzaSyD2ZmZ8y399YYyvUHWaKOux3tgAV4T6OLg",
  authDomain: "cv-generator-447314.firebaseapp.com",
  databaseURL: "https://cv-generator-447314-default-rtdb.europe-west1.firebasedatabase.app",
  projectId: "cv-generator-447314",
  storageBucket: "cv-generator-447314.firebasestorage.app",
  messagingSenderId: "177360827241",
  appId: "1:177360827241:web:97d252e97413cacf7203f8"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

// Fonction pour gérer l'authentification Google
export async function signInWithGoogle() {
  return new Promise((resolve, reject) => {
    console.log('Demande de token Google via chrome.identity');
    chrome.identity.getAuthToken({ interactive: true }, async (token) => {
      console.log('Token reçu:', !!token);
      
      if (chrome.runtime.lastError || !token) {
        const errorMessage = chrome.runtime.lastError?.message || 'Pas de token reçu';
        console.error('Erreur obtention token:', errorMessage);
        reject(new Error(errorMessage));
        return;
      }

      try {
        // Créer un credential Firebase avec le token Google
        const credential = GoogleAuthProvider.credential(null, token);
        
        // Connecter à Firebase avec le credential
        const userCred = await signInWithCredential(auth, credential);
        console.log('Utilisateur connecté:', userCred.user);
        resolve(userCred.user);
      } catch (error) {
        console.error('Erreur lors de l\'authentification Firebase:', error);
        reject(new Error(error.message || 'Erreur lors de l\'authentification Firebase'));
      }
    });
  });
}

// Fonction pour la déconnexion
export async function signOut() {
  try {
    await auth.signOut();
    // Révoquer également le token Chrome
    chrome.identity.removeCachedAuthToken({ token: await chrome.identity.getAuthToken({ interactive: false }) });
  } catch (error) {
    console.error("Erreur lors de la déconnexion:", error);
    throw error;
  }
}

// Export des instances et fonctions nécessaires
export { auth, db, GoogleAuthProvider, signInWithCredential }; 