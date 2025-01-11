// Récupérer le nom de l'utilisateur depuis localStorage
const userName = localStorage.getItem("userName");

if (userName) {
  document.getElementById("welcome-message").textContent = `Bienvenue, ${userName}!`;
} else {
  document.getElementById("welcome-message").textContent = "Aucun utilisateur connecté.";
}

// Configurer Firebase Storage
const firebaseConfig = {
  apiKey: "AIzaSyD2ZmZ8y399YYyvUHWaKOux3tgAV4T6OLg",
  authDomain: "cv-generator-447314.firebaseapp.com",
  projectId: "cv-generator-447314",
  storageBucket: "cv-generator-447314.appspot.com",
};

const app = initializeApp(firebaseConfig);
const storage = getStorage(app);

// Gérer l'upload de fichiers
const uploadForm = document.getElementById("upload-form");
uploadForm.addEventListener("submit", (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("file-input");
  const file = fileInput.files[0];

  if (!file) {
    alert("Veuillez sélectionner un fichier.");
    return;
  }

  const storageRef = ref(storage, `users/${userName}/${file.name}`);
  const uploadTask = uploadBytesResumable(storageRef, file);

  uploadTask.on("state_changed", (snapshot) => {
    const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
    console.log(`Upload en cours : ${progress}%`);
  }, (error) => {
    console.error("Erreur d'upload :", error);
  }, () => {
    getDownloadURL(uploadTask.snapshot.ref).then((downloadURL) => {
      console.log("Fichier téléchargé à l'adresse :", downloadURL);
      document.getElementById("upload-status").textContent = `Fichier téléchargé avec succès !`;
    });
  });
});