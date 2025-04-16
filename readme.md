
rm -rf venv
python3 -m venv venv
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
    --allow-unauthenticated \
    --service-account backend-flask@cv-generator-447314.iam.gserviceaccount.com \
    --set-env-vars ENV=prod

###### TEST backend

curl -X POST "http://localhost:8080/api/generate-profile" \
  -H "Content-Type: application/json" \
  -v

curl -X POST "http://localhost:8080/api/v2/generate-profile" \
  -H "Content-Type: application/json" \
  -v



curl -X POST "https://cv-generator-api-dev-177360827241.europe-west1.run.app/api/generate-profile" \
  -H "Content-Type: application/json" \
  -v

curl -X POST \
  http://localhost:8080/api/generate-cv \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer test-token' \
  -d '{"cv_name": "cv_test"}'

curl -X POST \
  http://localhost:8080/api/v2/generate-cv \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer test-token' \
  -d '{"cv_id": "test_cv"}'

curl -X POST "https://cv-generator-api-dev-177360827241.europe-west1.run.app/api/generate-cv" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer test-token" \
-d '{"cv_name": "cv_test"}'

## MCP

mcp-langgraph-sse

uvx --from mcpdoc mcpdoc \
  --urls LangGraph:https://langchain-ai.github.io/langgraph/llms.txt \
  --transport sse \
  --port 8082 \
  --host localhost \
  --follow-redirects