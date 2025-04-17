# CV Generator - Générateur Automatique de CV

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🚀 À Propos

CV Generator est une application web sophistiquée qui automatise la création de CV personnalisés à partir de descriptions de postes. Utilisant l'intelligence artificielle, l'application analyse les offres d'emploi et génère des CV optimisés et adaptés à chaque position.

## ✨ Fonctionnalités

- 🤖 Génération automatique de CV basée sur l'analyse des offres d'emploi
- 📝 Personnalisation intelligente du contenu selon le poste
- 🌐 Support multilingue pour la génération de CV
- 🔒 Système d'authentification sécurisé
- 📊 Interface utilisateur intuitive
- 🔄 Gestion des profils et historique des CV générés
- 🎨 Mise en page professionnelle et personnalisable

## 🛠️ Architecture Technique

- **Backend**: Python/Flask
- **Base de données**: Firestore
- **Frontend**: HTML/CSS/JavaScript
- **Déploiement**: Google Cloud Platform
- **Conteneurisation**: Docker

## 🚀 Installation

1. Cloner le repository :
```bash
git clone https://github.com/votre-username/CV_auto.git
cd CV_auto
```

2. Créer et activer l'environnement virtuel :
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Installer les dépendances :
```bash
cd backend
pip install -r requirements.txt
```

4. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

## 🏗️ Structure du Projet

```
CV_auto/
├── backend/           # API Flask et logique métier
├── frontend/         # Interface utilisateur
├── ai_module/        # Module d'IA pour l'analyse
├── scripts/          # Scripts utilitaires
└── firestore_schema.json  # Schéma de la base de données
```

## 📝 Utilisation

1. Déployer le backend :
```bash
gcloud builds submit --tag europe-west9-docker.pkg.dev/cv-generator-447314/backend-cv-automation/backend-flask:v1
gcloud run deploy backend-flask \
    --image europe-west9-docker.pkg.dev/cv-generator-447314/backend-cv-automation/backend-flask:v1 \
    --platform managed \
    --region europe-west9 \
    --allow-unauthenticated
```

## 🔒 Sécurité

- Authentification utilisateur
- Validation des données
- Protection contre les injections
- Gestion sécurisée des tokens

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.