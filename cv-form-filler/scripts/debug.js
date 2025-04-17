console.log('[DEBUG] Chargement du script de débogage');

// Fonction pour vérifier l'état des scripts
function checkScriptsStatus() {
  console.log('[DEBUG] Vérification des scripts:', {
    'debug.js': 'chargé',
    'firebase-init.js': window.firebase ? 'chargé' : 'non chargé',
    'firebase-auth': window.firebase?.auth ? 'chargé' : 'non chargé',
    'firebase-firestore': window.firebase?.firestore ? 'chargé' : 'non chargé',
    'popup.js': 'en cours de vérification'
  });
}

// Vérification au chargement
document.addEventListener('DOMContentLoaded', function() {
  console.log('[DEBUG] DOM Content Loaded dans debug.js');
  
  // Vérifier les éléments du DOM
  const elements = {
    loginButton: document.getElementById('login-button'),
    logoutButton: document.getElementById('logout-button'),
    userInfo: document.getElementById('user-info')
  };
  
  console.log('[DEBUG] État des éléments DOM:', {
    loginButton: !!elements.loginButton,
    logoutButton: !!elements.logoutButton,
    userInfo: !!elements.userInfo
  });

  // Ajouter un écouteur de test sur le bouton de connexion
  if (elements.loginButton) {
    elements.loginButton.addEventListener('click', function() {
      console.log('[DEBUG] Clic détecté par debug.js');
    });
  }

  // Vérifier l'état des scripts
  setTimeout(checkScriptsStatus, 1000); // Vérifier après un délai pour laisser le temps aux modules de charger
});

// Vérification finale
window.addEventListener('load', function() {
  console.log('[DEBUG] Tous les éléments chargés');
  setTimeout(checkScriptsStatus, 1000); // Vérifier après un délai pour laisser le temps aux modules de charger
}); 