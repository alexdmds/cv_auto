// Création du menu contextuel
chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installée - Création du menu contextuel');
  
  // Supprimer les menus existants pour éviter les doublons
  chrome.contextMenus.removeAll(() => {
    // Créer le nouveau menu
    chrome.contextMenus.create({
      id: "fillForm",
      title: "📝 Remplir avec CV Form Filler",
      contexts: ["editable"],
      type: "normal"
    }, () => {
      if (chrome.runtime.lastError) {
        console.error('Erreur création menu:', chrome.runtime.lastError);
      } else {
        console.log('Menu contextuel créé avec succès');
      }
    });
  });
});

// Gestion du clic sur le menu contextuel
chrome.contextMenus.onClicked.addListener((info, tab) => {
  console.log('Menu contextuel cliqué:', info);
  if (info.menuItemId === "fillForm") {
    chrome.tabs.sendMessage(tab.id, {
      action: "fillField"
    });
  }
}); 