import unittest
from ai_module.models.generate_profile_chain import generate_structured_head_node
from ai_module.models.data_structures1 import ProfileState, HeadData

class TestGenerateHeadNode(unittest.TestCase):
    """Tests pour le nœud generate_structured_head_node."""
    
    def setUp(self):
        """Préparation des données de test."""
        self.texte_test = """
        Jean-Michel Dupont
        Architecte Solutions & Lead Developer
        Email: jm.dupont@email.com | Tel: 06 12 34 56 78
        LinkedIn: linkedin.com/in/jmdupont

        Expert en architecture logicielle et développement full-stack avec 12 ans d'expérience 
        dans la conception et le déploiement de solutions cloud à grande échelle. 
        Passionné par l'innovation technologique et le leadership technique.

        Compétences: 
        - Backend: Python, Java, Node.js, GraphQL, REST APIs
        - Frontend: React, Vue.js, TypeScript, HTML5/CSS3
        - Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD, Terraform
        - Base de données: PostgreSQL, MongoDB, Redis
        - Management: Gestion d'équipe, Méthodologies Agiles, Formation technique

        Langues:
        - Français (Langue maternelle)
        - Anglais (Bilingue, TOEIC 985/990)
        - Allemand (Niveau C1, séjour de 2 ans à Berlin)
        - Espagnol (Niveau B2)

        Centres d'intérêt: 
        - Photographie (exposition amateur 2022)
        - Musique (guitariste dans un groupe de jazz)
        - Course à pied (semi-marathon de Paris 2023)
        - Contribution open source (maintainer sur 3 projets Python)
        """
    
    def test_generate_structured_head_node(self):
        """Test du nœud generate_structured_head_node."""
        # Utilisation du constructeur amélioré
        state = ProfileState(input_text=self.texte_test)
        
        # Appel du nœud
        result = generate_structured_head_node(state)
        
        # Vérification que nous avons reçu un dictionnaire avec la clé 'head'
        self.assertIsInstance(result, dict)
        self.assertIn('head', result)
        
        # Vérification des champs dans l'en-tête généré
        head_data = result['head']
        
        # Vérifier si head_data est un objet HeadData
        self.assertIsInstance(head_data, HeadData)
        
        # Vérification que les valeurs ne sont pas None
        self.assertIsNotNone(head_data.name)
        self.assertIsNotNone(head_data.phone)
        self.assertIsNotNone(head_data.email)
        self.assertIsNotNone(head_data.general_title)
        self.assertIsNotNone(head_data.skills)
        self.assertIsNotNone(head_data.langues)
        self.assertIsNotNone(head_data.hobbies)
        
        # Vérification de quelques valeurs spécifiques
        self.assertIn("Dupont", head_data.name)
        self.assertIn("06 12 34 56 78", head_data.phone)
        self.assertIn("jm.dupont@email.com", head_data.email)
        
        print("\nRésultat du test :")
        print("------------------")
        print(f"Nom: {head_data.name}")
        print(f"Téléphone: {head_data.phone}")
        print(f"Email: {head_data.email}")
        print(f"Titre général: {head_data.general_title}")
        print(f"Compétences: {head_data.skills}")
        print(f"Langues: {head_data.langues}")
        print(f"Centres d'intérêt: {head_data.hobbies}")

if __name__ == "__main__":
    unittest.main()
