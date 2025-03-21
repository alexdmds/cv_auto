import unittest
from pathlib import Path
import sys
from os.path import dirname, abspath
import json

# Ajout du répertoire parent au PYTHONPATH
root_dir = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root_dir)

from ai_module.chains_gen_cv.global_chain import compiled_gencv_graph
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
                    location_raw="",
                    location_refined="",
                    dates_raw="",
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
                    location_raw="",
                    location_refined="",
                    dates_raw="",
                    dates_refined="",
                    description_generated="",
                    description_refined="",
                    weight=0.0,
                    order=None,
                    nb_mots=0
                )
            ],
            "head": CVHead(
                name="",
                title_raw="Développeur Full Stack",
                title_generated="",
                title_refined="",
                mail="",
                tel_raw="",
                tel_refined=""
            ),
            "sections": {},
            "competences": {},
            "skills_raw": "Python, Django, React, SQL, Git, Docker",
            "langues": [],
            "hobbies_raw": "",
            "hobbies_refined": "",
            "job_refined": ""
        }

    def test_graph_compilation(self):
        """Teste si le graphe est correctement compilé"""
        self.assertIsNotNone(compiled_gencv_graph)
        self.assertTrue(hasattr(compiled_gencv_graph, 'invoke'))

    def test_chain_execution(self):
        """Teste l'exécution complète de la chaîne"""
        # Création de l'état initial
        initial_state = CVGenState(**self.test_data)
        
        # Exécution de la chaîne et conversion du résultat
        result_dict = compiled_gencv_graph.invoke(initial_state)
        result = CVGenState.from_dict({**initial_state.model_dump(), **result_dict})
        
        # Vérifications des résultats
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.job_refined)
        self.assertIsNotNone(result.experiences)
        self.assertIsNotNone(result.education)
        self.assertIsNotNone(result.head.title_generated)
        self.assertIsNotNone(result.competences)

    def test_output_structure(self):
        """Teste la structure des sorties"""
        initial_state = CVGenState(**self.test_data)
        result_dict = compiled_gencv_graph.invoke(initial_state)
        result = CVGenState.from_dict({**initial_state.model_dump(), **result_dict})
        
        # Vérification de la structure des expériences
        for exp in result.experiences:
            self.assertIsNotNone(exp.title_refined)
            self.assertIsNotNone(exp.company_refined)
            self.assertIsNotNone(exp.summary)
        
        # Vérification de la structure des formations
        for edu in result.education:
            self.assertIsNotNone(edu.degree_refined)
            self.assertIsNotNone(edu.institution_refined)
            self.assertIsNotNone(edu.summary)
        
        # Vérification du titre généré
        self.assertIsNotNone(result.head.title_generated)
        self.assertTrue(len(result.head.title_generated) > 0)
        
        # Vérification des compétences
        self.assertIsInstance(result.competences, dict)
        self.assertTrue(len(result.competences) > 0)

    def test_output_content(self):
        """Teste le contenu des sorties"""
        initial_state = CVGenState(**self.test_data)
        result_dict = compiled_gencv_graph.invoke(initial_state)
        
        # Fusion de tous les résultats intermédiaires
        final_state = initial_state.model_dump()
        for key, value in result_dict.items():
            if isinstance(value, dict):
                if key in final_state and isinstance(final_state[key], dict):
                    final_state[key].update(value)
                else:
                    final_state[key] = value
            else:
                final_state[key] = value
        
        result = CVGenState.from_dict(final_state)
        
        # Vérification que le résumé du poste contient des mots-clés pertinents
        self.assertTrue(any(keyword in result.job_refined.lower() 
                          for keyword in ['python', 'développeur', 'web']))
        
        # Vérification que le titre généré est pertinent
        self.assertTrue(any(keyword in result.head.title_generated.lower() 
                          for keyword in ['développeur', 'full stack', 'python']))
        
        # Debug des compétences
        print("\nCompétences générées:", result.competences)
        print("Résultat complet:", result_dict)
        all_skills = [skill.lower() for skills in result.competences.values() for skill in skills]
        print("Toutes les compétences:", all_skills)
        
        # Vérification que les compétences contiennent les technologies principales
        self.assertTrue(any(keyword in all_skills 
                          for keyword in ['python', 'django', 'react', 'sql']))

if __name__ == '__main__':
    unittest.main()
