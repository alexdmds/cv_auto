// Service worker pour l'extension
console.log('Extension installée');

// Gérer l'authentification Google
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Message reçu dans le service worker:', request);
  
  if (request.action === 'initializeGoogleAuth') {
    chrome.identity.getAuthToken({ 
      interactive: true,
      scopes: [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
      ]
    }, (token) => {
      console.log('Token reçu:', token);
      
      if (chrome.runtime.lastError || !token) {
        console.error('Erreur auth Chrome:', chrome.runtime.lastError);
        sendResponse({ success: false, error: chrome.runtime.lastError });
        return;
      }

      // Envoyer le token au popup qui gèrera l'authentification Firebase
      sendResponse({ 
        success: true, 
        token: token
      });
    });
    
    // Retourner true pour indiquer que la réponse sera envoyée de manière asynchrone
    return true;
  }
}); 