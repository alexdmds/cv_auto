import { auth, signInWithGoogle } from '../scripts/firebase-init.js';

console.log('[POPUP] Chargement du popup.js');

// Fonction pour afficher les messages de statut
function updateStatusMessage(message, isError = false) {
  console.log(`[POPUP] Status message: ${message} (${isError ? 'error' : 'info'})`);
  const statusElement = document.getElementById('status-message');
  statusElement.textContent = message;
  statusElement.className = `status-message ${isError ? 'error' : 'success'}`;
}

// Fonction pour mettre à jour l'interface
function updateUI(user) {
  console.log("[POPUP] Mise à jour UI avec user:", user?.email);
  const userInfo = document.getElementById('user-info');
  const loginButton = document.getElementById('login-button');
  const logoutButton = document.getElementById('logout-button');

  if (!userInfo || !loginButton || !logoutButton) {
    console.error("[POPUP] Éléments UI manquants");
    return;
  }

  if (user) {
    userInfo.innerHTML = `
      <p>Connecté en tant que: ${user.email}</p>
      ${user.photoURL ? `<img src="${user.photoURL}" alt="Photo de profil" class="profile-pic">` : ''}
    `;
    loginButton.classList.add('hidden');
    logoutButton.classList.remove('hidden');
  } else {
    userInfo.innerHTML = '<p>Non connecté</p>';
    loginButton.classList.remove('hidden');
    logoutButton.classList.add('hidden');
  }
}

// Fonction pour gérer la connexion Google
async function handleLogin() {
  console.log('[POPUP] Tentative de connexion Google');
  updateStatusMessage('Connexion en cours...');

  try {
    const user = await signInWithGoogle();
    updateStatusMessage('Connexion réussie !');
    console.log('Utilisateur connecté:', user);
  } catch (error) {
    console.error('Erreur de connexion:', error);
    updateStatusMessage('Erreur de connexion: ' + error.message, true);
  }
}

// Fonction pour gérer la déconnexion
async function handleLogout() {
  console.log('[POPUP] Tentative de déconnexion');
  try {
    await auth.signOut();
    updateStatusMessage('Déconnexion réussie !');
  } catch (error) {
    console.error('Erreur de déconnexion:', error);
    updateStatusMessage('Erreur de déconnexion: ' + error.message, true);
  }
}

// Initialisation au chargement du document
document.addEventListener('DOMContentLoaded', () => {
  console.log('[POPUP] DOMContentLoaded - Initialisation du popup');
  
  const loginButton = document.getElementById('login-button');
  const logoutButton = document.getElementById('logout-button');

  if (!loginButton || !logoutButton) {
    console.error('[POPUP] Boutons non trouvés dans le DOM');
    return;
  }

  // Ajouter les écouteurs d'événements
  loginButton.addEventListener('click', handleLogin);
  logoutButton.addEventListener('click', handleLogout);

  // Observer les changements d'état d'authentification
  auth.onAuthStateChanged((user) => {
    console.log('[POPUP] Changement d\'état d\'authentification:', user?.email);
    updateUI(user);
  });

  // État initial
  updateUI(auth.currentUser);
});

// Gestion des erreurs globales
window.addEventListener('error', (event) => {
  console.error('Erreur globale:', event.error);
  updateStatusMessage('Une erreur est survenue: ' + event.error.message, true);
});