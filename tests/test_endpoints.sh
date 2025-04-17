#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Sauvegarder le répertoire de départ
START_DIR=$(pwd)

# Se déplacer dans le répertoire parent pour lancer le serveur
cd "$(dirname "$0")/.." || exit

echo -e "${GREEN}Démarrage du serveur...${NC}"
python backend/main.py &
SERVER_PID=$!

# Attendre que le serveur démarre
echo "Attente du démarrage du serveur..."
sleep 5

# Vérifier si le serveur est en cours d'exécution
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${RED}Erreur: Le serveur n'a pas démarré correctement${NC}"
    cd "$START_DIR" || exit
    exit 1
fi

# Test de l'endpoint health
echo -e "\n${GREEN}Test de l'endpoint /health${NC}"
curl -X GET http://localhost:8080/health \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json"

# Test de l'endpoint generate-profile
echo -e "\n\n${GREEN}Test de l'endpoint /api/v2/generate-profile${NC}"
curl -X POST http://localhost:8080/api/v2/generate-profile \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json"

# Test de l'endpoint generate-cv
echo -e "\n\n${GREEN}Test de l'endpoint /api/v2/generate-cv${NC}"
curl -X POST http://localhost:8080/api/v2/generate-cv \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json" \
  -d '{"cv_id": "test_cv"}'

# Arrêt du serveur
echo -e "\n\n${GREEN}Arrêt du serveur...${NC}"
if kill -0 $SERVER_PID 2>/dev/null; then
    kill $SERVER_PID
    wait $SERVER_PID 2>/dev/null
fi

# Retour au répertoire de départ
cd "$START_DIR" || exit

echo -e "\n${GREEN}Tests terminés${NC}" 