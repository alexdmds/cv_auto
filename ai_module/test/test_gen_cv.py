import unittest
from pathlib import Path
import sys
from os.path import dirname, abspath
import json

# Ajout du répertoire parent au PYTHONPATH
root_dir = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root_dir)

from ai_module.chains_gen_cv.global_chain import get_compiled_gencv_graph
from ai_module.lg_models import CVGenState, CVExperience, CVEducation, CVHead

class TestGenCV(unittest.TestCase):
    def setUp(self):
        # Données de test
        self.test_data = {
            "job_raw": """
            Développeur Full Stack Python
            Nous recherchons un développeur expérimenté pour rejoindre notre équipe.
            Compétences requises : Python, Django, React, SQL
            """,
            "experiences": [
                CVExperience(
                    title_raw="Développeur Python",
                    company_raw="Tech Corp",
                    description_raw="Développement d'applications web avec Django et React",
                    title_refined="",
                    company_refined="",
                    summary="",
                    location_raw="Paris",
                    location_refined="",
                    dates_raw="2020-2023",
                    dates_refined="",
                    description_refined="",
                    bullets=[],
                    weight=0.0,
                    order=None,
                    nb_bullets=0
                )
            ],
            "education": [
                CVEducation(
                    degree_raw="Master en Informatique",
                    institution_raw="École d'Ingénieurs",
                    description_raw="Spécialisation en développement web",
                    degree_refined="",
                    institution_refined="",
                    summary="",
                    location_raw="Lyon",
                    location_refined="",
                    dates_raw="2018-2020",
                    dates_refined="",
                    description_generated="",
                    description_refined="",
                    weight=0.0,
                    order=None,
                    nb_mots=0
                )
            ],
            "head": CVHead(
                name="John Doe",
                title_raw="Développeur Full Stack",
                title_generated="",
                title_refined="",
                mail="john@example.com",
                tel_raw="+33123456789",
                tel_refined=""
            ),
            "sections": {},
            "competences": {},
            "skills_raw": "Python, Django, React, SQL, Git, Docker",
            "langues": [],
            "hobbies_raw": "Photographie, Randonnée",
            "hobbies_refined": "",
            "job_refined": "",
            "language_cv": "",
            "final_output": ""
        }

    def test_graph_compilation(self):
        """Teste si le graphe est correctement compilé"""
        graph = get_compiled_gencv_graph()
        self.assertIsNotNone(graph)
        self.assertTrue(hasattr(graph, 'invoke'))

    def test_chain_execution(self):
        """Teste l'exécution complète de la chaîne"""
        initial_state = CVGenState(**self.test_data)
        graph = get_compiled_gencv_graph()
        result_dict = graph.invoke(initial_state)
        result = CVGenState.from_dict(result_dict)
        
        # Vérifications des résultats
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, CVGenState))
        self.assertIsNotNone(result.job_refined)
        self.assertIsNotNone(result.language_cv)
        self.assertIsNotNone(result.experiences)
        self.assertIsNotNone(result.education)
        self.assertIsNotNone(result.head.title_generated)
        self.assertIsNotNone(result.competences)

    def test_output_structure(self):
        """Teste la structure des sorties"""
        initial_state = CVGenState(**self.test_data)
        graph = get_compiled_gencv_graph()
        result_dict = graph.invoke(initial_state)
        result = CVGenState.from_dict(result_dict)
        
        # Vérification de la langue détectée
        self.assertIsNotNone(result.language_cv)
        
        # Vérification de la structure des expériences
        self.assertTrue(isinstance(result.experiences, list))
        if result.experiences:
            exp = result.experiences[0]
            self.assertTrue(isinstance(exp, CVExperience))
            self.assertIsNotNone(exp.title_refined)
            self.assertIsNotNone(exp.company_refined)
            self.assertIsNotNone(exp.summary)
            self.assertIsNotNone(exp.weight)
            self.assertIsNotNone(exp.order)
        
        # Vérification de la structure des formations
        self.assertTrue(isinstance(result.education, list))
        if result.education:
            edu = result.education[0]
            self.assertTrue(isinstance(edu, CVEducation))
            self.assertIsNotNone(edu.degree_refined)
            self.assertIsNotNone(edu.institution_refined)
            self.assertIsNotNone(edu.summary)
            self.assertIsNotNone(edu.weight)
            self.assertIsNotNone(edu.order)
        
        # Vérification du titre généré
        self.assertTrue(isinstance(result.head, CVHead))
        self.assertIsNotNone(result.head.title_generated)
        self.assertTrue(len(result.head.title_generated) > 0)
        
        # Vérification des compétences
        self.assertTrue(isinstance(result.competences, dict))
        self.assertTrue(len(result.competences) > 0)

    def test_output_content(self):
        """Teste le contenu des sorties"""
        initial_state = CVGenState(**self.test_data)
        graph = get_compiled_gencv_graph()
        result_dict = graph.invoke(initial_state)
        result = CVGenState.from_dict(result_dict)
        
        # Vérification de la langue
        self.assertEqual(result.language_cv, 'fr')
        
        # Vérification que le résumé du poste contient des mots-clés pertinents
        self.assertTrue(
            any(keyword in result.job_refined.lower() 
                for keyword in ['python', 'développeur', 'web']),
            f"Le résumé du poste ne contient pas les mots-clés attendus. Contenu: {result.job_refined}"
        )
        
        # Vérification que le titre généré est pertinent
        self.assertTrue(
            any(keyword in result.head.title_generated.lower() 
                for keyword in ['développeur', 'full stack', 'python']),
            f"Le titre généré ne contient pas les mots-clés attendus. Contenu: {result.head.title_generated}"
        )
        
        # Vérification des compétences
        # Aplatir toutes les compétences en une seule liste
        all_skills = []
        for category, skills in result.competences.items():
            if isinstance(skills, list):
                all_skills.extend([skill.lower() for skill in skills])
            elif isinstance(skills, str):
                all_skills.append(skills.lower())
        
        # Vérifier la présence d'au moins une compétence clé
        key_skills = ['python', 'django', 'react', 'sql']
        found_skills = [skill for skill in key_skills if any(skill in s for s in all_skills)]
        self.assertTrue(
            len(found_skills) > 0,
            f"Aucune compétence clé trouvée parmi {key_skills}. Compétences trouvées: {all_skills}"
        )
        
        # Vérification de la priorisation
        if result.experiences:
            exp = result.experiences[0]
            self.assertIsNotNone(exp.weight)
            self.assertIsNotNone(exp.order)

if __name__ == '__main__':
    unittest.main()
