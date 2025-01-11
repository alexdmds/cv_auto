function handleCredentialResponse(response) {
    // Récupérer l'ID token
    const id_token = response.credential;

    // Envoyer l'ID token au backend
    fetch("https://backend-flask-177360827241.europe-west9.run.app/auth", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ id_token })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error("Erreur:", data.error);
            alert("Échec de l'authentification : " + data.error);
        } else {
            console.log("Utilisateur authentifié:", data.user);
            // Redirigez l'utilisateur ou affichez ses informations
            alert(`Bienvenue, ${data.user.name}!`);
            window.location.href = "https://storage.googleapis.com/frontend_cv_generator/authenticated.html";
        }
    })
    .catch(error => console.error("Erreur réseau:", error));
}

window.onload = function () {
    google.accounts.id.initialize({
        client_id: "177360827241-3g376bqaun1t2h5nhl8thnv5k9o64efh.apps.googleusercontent.com",
        callback: handleCredentialResponse
    });
    google.accounts.id.renderButton(
        document.querySelector(".g_id_signin"),
        { theme: "outline", size: "large" }
    );
};