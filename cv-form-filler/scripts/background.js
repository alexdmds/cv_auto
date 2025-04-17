import { initializeApp } from '../node_modules/firebase/app';
import { getAuth, signInWithCredential, GoogleAuthProvider } from '../node_modules/firebase/auth';

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

console.log('Extension installée');

// Gérer l'authentification Google
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Message reçu dans le service worker:', request);
  
  if (request.action === 'initializeGoogleAuth') {
    chrome.identity.getAuthToken({ interactive: true }, async (token) => {
      console.log('Token reçu:', token);
      
      if (chrome.runtime.lastError || !token) {
        console.error('Erreur auth Chrome:', chrome.runtime.lastError);
        sendResponse({ success: false, error: chrome.runtime.lastError?.message || 'Pas de token reçu' });
        return;
      }

      try {
        // Créer un credential Firebase avec le token Google
        const credential = GoogleAuthProvider.credential(null, token);
        
        // Connecter à Firebase avec le credential
        const userCred = await signInWithCredential(auth, credential);
        console.log('Utilisateur connecté:', userCred.user);
        
        sendResponse({ 
          success: true, 
          token: token,
          user: {
            uid: userCred.user.uid,
            email: userCred.user.email,
            displayName: userCred.user.displayName
          }
        });
      } catch (error) {
        console.error('Erreur Firebase:', error);
        sendResponse({ success: false, error: error.message });
      }
    });
    
    // Retourner true pour indiquer que la réponse sera envoyée de manière asynchrone
    return true;
  }
}); 