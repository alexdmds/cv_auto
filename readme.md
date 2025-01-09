source venv/bin/activate

L’attribut alignment prend les valeurs suivantes :
	•	0 : Alignement à gauche.
	•	1 : Alignement centré.
	•	2 : Alignement à droite.
	•	4 : Justifié (aligné des deux côtés).

gsutil -m cp -r ./frontend/* gs://frontend_cv_generator/


###### DANS backend
gcloud builds submit --tag europe-west9-docker.pkg.dev/cv-generator-447314/backend-cv-automation/backend-flask:v1

gcloud run deploy backend-flask \
    --image europe-west9-docker.pkg.dev/cv-generator-447314/backend-cv-automation/backend-flask:v1 \
    --platform managed \
    --region europe-west9 \
    --allow-unauthenticated