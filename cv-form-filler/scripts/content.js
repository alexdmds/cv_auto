console.log('Content script chargé');

// Mapping des champs courants
const FIELD_MAPPING = {
  'linkedin': ['linkedin', 'linkedin-url', 'linkedin-id'],
  'github': ['github', 'github-id', 'github-url'],
  'country': ['country', 'pays', 'location'],
  'availability': ['availability', 'time-availability', 'disponibilite'],
  'experience': ['experience', 'domain-experience']
};

// Fonction pour détecter le type de champ
function detectFieldType(element) {
  if (!element) return null;

  const id = (element.id || '').toLowerCase();
  const name = (element.name || '').toLowerCase();
  const placeholder = (element.placeholder || '').toLowerCase();
  
  for (const [fieldType, keywords] of Object.entries(FIELD_MAPPING)) {
    if (keywords.some(keyword => 
      id.includes(keyword) || 
      name.includes(keyword) || 
      placeholder.includes(keyword)
    )) {
      return fieldType;
    }
  }
  return null;
}

// Écouter les messages du background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Message reçu dans le content script');
  
  if (message.action === "fillField") {
    const element = document.activeElement;
    const fieldType = detectFieldType(element);
    
    if (fieldType) {
      // Données de test pour le développement
      const testData = {
        linkedin: 'https://www.linkedin.com/in/alexis-de-monts-61328a175',
        github: 'alexdmds',
        country: 'France',
        availability: '20 hours per week',
        experience: '5 years of experience in data science'
      };
      
      element.value = testData[fieldType] || '';
      element.dispatchEvent(new Event('change', { bubbles: true }));
      element.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }
}); 