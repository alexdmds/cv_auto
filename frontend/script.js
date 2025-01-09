document.getElementById("upload-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const fileInput = document.getElementById("file-input");
    if (fileInput.files.length === 0) {
        alert("Veuillez sélectionner un fichier !");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const response = await fetch("https://your-backend-url/upload", {
        method: "POST",
        body: formData,
    });

    if (response.ok) {
        alert("Fichier uploadé avec succès !");
    } else {
        alert("Erreur lors de l'upload.");
    }
});

async function generateCV() {
    const jobDescription = document.getElementById("job-description").value;
    if (!jobDescription) {
        alert("Veuillez coller une fiche de poste !");
        return;
    }

    const response = await fetch("https://your-backend-url/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ job_description: jobDescription }),
    });

    if (response.ok) {
        const data = await response.json();
        document.getElementById("result").innerHTML = `
            CV généré : <a href="${data.pdf_path}" target="_blank">Télécharger</a>
        `;
    } else {
        alert("Erreur lors de la génération du CV.");
    }
}