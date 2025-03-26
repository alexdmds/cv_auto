#!/usr/bin/env python3
"""
Script de test pour la méthode from_user_document de GlobalState
Ce script permet de tester la conversion directe de UserDocument vers GlobalState
"""

import sys
import os
import argparse
from pprint import pprint
import json

# Ajout du répertoire parent au PYTHONPATH pour trouver les modules du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import des modèles
from backend.models import UserDocument, CV, CVData, Profile, HeadProfile, ExperienceCV, ExperienceProfile, EducationCV, EducationProfile, LanguageCV, SkillCV, SectionsName
from ai_module.lg_models import GlobalState

def create_test_user_document():
    """
    Crée un UserDocument de test avec des données fictives
    """
    # Créer un profil
    profile = Profile(
        head=HeadProfile(
            name="Jean Dupont",
            title="Ingénieur Full Stack",
            mail="jean.dupont@example.com",
            phone="+33612345678",
            linkedin_url="https://linkedin.com/in/jeandupont"
        ),
        experiences=[
            ExperienceProfile(
                title="Développeur Senior",
                company="Tech Innovation",
                dates="2018-2022",
                location="Paris, France",
                full_descriptions=["Développement d'applications web et mobiles", "Gestion d'une équipe de 5 développeurs"],
                bullets=["Architecture de microservices", "Mise en place de CI/CD"]
            ),
            ExperienceProfile(
                title="Développeur Junior",
                company="StartupXYZ",
                dates="2015-2018",
                location="Lyon, France",
                full_descriptions=["Développement frontend avec React"],
                bullets=["Intégration API REST", "Développement de composants réutilisables"]
            )
        ],
        educations=[
            EducationProfile(
                title="Master en Informatique",
                university="Université de Paris",
                dates="2013-2015",
                location="Paris, France",
                full_descriptions="Spécialisation en développement web et intelligence artificielle"
            ),
            EducationProfile(
                title="Licence en Informatique",
                university="Université de Lyon",
                dates="2010-2013",
                location="Lyon, France",
                full_descriptions="Formation générale en informatique"
            )
        ],
        skills={
            "Programmation": ["Python", "JavaScript", "TypeScript", "Java"],
            "Frameworks": ["React", "Node.js", "Django", "Spring Boot"],
            "Outils": ["Git", "Docker", "Kubernetes", "AWS"]
        },
        languages=[
            {"language": "Français", "level": "Langue maternelle"},
            {"language": "Anglais", "level": "Courant (TOEIC 950)"},
            {"language": "Espagnol", "level": "Intermédiaire (B1)"}
        ],
        hobbies="Randonnée, photographie, lecture, échecs"
    )
    
    # Créer un CV
    cv_data = CVData(
        name="Jean Dupont",
        title="Développeur Full Stack",
        mail="jean.dupont@example.com",
        phone="+33612345678",
        sections_name=SectionsName(
            experience_section_name="Expérience Professionnelle",
            education_section_name="Formation",
            skills_section_name="Compétences Techniques",
            languages_section_name="Langues",
            hobbies_section_name="Centres d'intérêt"
        ),
        experiences=[
            ExperienceCV(
                title="Lead Developer",
                company="Tech Innovation",
                dates="2018-2022",
                location="Paris, France",
                bullets=[
                    "Direction technique d'une équipe de 5 développeurs",
                    "Conception d'architecture microservices pour des applications à forte charge",
                    "Migration de systèmes legacy vers des solutions cloud natives"
                ]
            ),
            ExperienceCV(
                title="Développeur Frontend",
                company="StartupXYZ",
                dates="2015-2018",
                location="Lyon, France",
                bullets=[
                    "Développement d'interfaces utilisateur avec React et TypeScript",
                    "Optimisation des performances frontend (bundle size, rendering)",
                    "Mise en place de tests automatisés (Jest, Cypress)"
                ]
            )
        ],
        educations=[
            EducationCV(
                title="Master en Informatique",
                university="Université de Paris",
                dates="2013-2015",
                location="Paris, France",
                description="Spécialisation en développement web et applications cloud"
            )
        ],
        skills=[
            SkillCV(
                category_name="Langages de programmation",
                skills="Python, JavaScript, TypeScript, Java"
            ),
            SkillCV(
                category_name="Frameworks & Bibliothèques",
                skills="React, Node.js, Express, Django, Spring Boot"
            ),
            SkillCV(
                category_name="DevOps & Cloud",
                skills="Docker, Kubernetes, AWS, CI/CD, Git"
            )
        ],
        languages=[
            LanguageCV(
                language="Français",
                level="Langue maternelle"
            ),
            LanguageCV(
                language="Anglais",
                level="Courant (TOEIC 950)"
            )
        ],
        hobbies="Randonnée en montagne, photographie de paysage, lecture de science-fiction"
    )
    
    cv1 = CV(
        cv_name="Développeur Full Stack Senior",
        job_raw="Nous recherchons un développeur full stack senior avec au moins 5 ans d'expérience en JavaScript/TypeScript et Python. Vous serez responsable de la conception, de l'implémentation et de la maintenance d'applications web à forte charge. Une expérience avec les technologies cloud est requise.",
        cv_data=cv_data
    )
    
    cv2 = CV(
        cv_name="Lead Developer",
        job_raw="Poste de lead developer pour diriger une équipe de développeurs sur un produit SaaS B2B. Compétences en architecture logicielle, management d'équipe et technologies cloud requises.",
        cv_data=cv_data
    )
    
    # Créer le UserDocument
    user_doc = UserDocument(cvs=[cv1, cv2], profile=profile)
    return user_doc

def test_conversion(cv_name):
    """
    Teste la conversion d'un UserDocument en GlobalState
    
    Args:
        cv_name (str): Nom du CV à utiliser pour la conversion
    """
    print(f"Test de conversion avec le CV: {cv_name}")
    
    # Créer un UserDocument de test
    user_doc = create_test_user_document()
    
    # Convertir en GlobalState directement avec la méthode from_user_document
    global_state = GlobalState.from_user_document(user_doc, cv_name)
    
    # Vérifier le résultat
    if global_state is None:
        print(f"❌ Aucun CV trouvé avec le nom: {cv_name}")
        return False
    
    print("✅ Conversion réussie!")
    
    # Afficher des informations générales
    print("\n=== INFORMATIONS GÉNÉRALES ===")
    print(f"Nom: {global_state.head.name}")
    print(f"Titre: {global_state.head.title_refined}")
    print(f"Email: {global_state.head.mail}")
    print(f"Téléphone: {global_state.head.tel_refined}")
    
    # Afficher les noms des sections
    print("\n=== NOMS DES SECTIONS ===")
    for section_key, section_name in global_state.sections.items():
        print(f"{section_key}: {section_name}")
    
    # Afficher les expériences
    print(f"\n=== EXPÉRIENCES ({len(global_state.experiences)}) ===")
    for idx, exp in enumerate(global_state.experiences, 1):
        print(f"\nExpérience #{idx}:")
        print(f"Titre: {exp.title_refined}")
        print(f"Entreprise: {exp.company_refined}")
        print(f"Dates: {exp.dates_refined}")
        print(f"Lieu: {exp.location_refined}")
        if exp.bullets:
            print(f"Points clés ({len(exp.bullets)}):")
            for bullet in exp.bullets[:2]:  # Afficher seulement les 2 premiers pour plus de lisibilité
                print(f"- {bullet}")
            if len(exp.bullets) > 2:
                print(f"- ... {len(exp.bullets) - 2} autres points")
    
    # Afficher les formations
    print(f"\n=== FORMATIONS ({len(global_state.education)}) ===")
    for idx, edu in enumerate(global_state.education, 1):
        print(f"\nFormation #{idx}:")
        print(f"Diplôme: {edu.degree_refined}")
        print(f"Institution: {edu.institution_refined}")
        print(f"Dates: {edu.dates_refined}")
        print(f"Lieu: {edu.location_refined}")
        if edu.description_refined:
            desc_preview = edu.description_refined[:100] + "..." if len(edu.description_refined) > 100 else edu.description_refined
            print(f"Description: {desc_preview}")
    
    # Afficher les compétences
    print("\n=== COMPÉTENCES ===")
    for category, skills in global_state.competences.items():
        print(f"{category}: {', '.join(skills[:5])}")
        if len(skills) > 5:
            print(f"... et {len(skills) - 5} autres")
    
    # Afficher les langues
    print(f"\n=== LANGUES ({len(global_state.langues)}) ===")
    for lang in global_state.langues:
        print(f"{lang.language}: {lang.level}")
    
    # Afficher les hobbies
    if global_state.hobbies_raw:
        print("\n=== CENTRES D'INTÉRÊT ===")
        print(global_state.hobbies_raw)
    
    # Afficher la description du poste
    if global_state.job_raw:
        print("\n=== DESCRIPTION DU POSTE ===")
        job_preview = global_state.job_raw[:150] + "..." if len(global_state.job_raw) > 150 else global_state.job_raw
        print(job_preview)
    
    # Sauvegarder le résultat dans un fichier JSON pour inspection
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"global_state_{cv_name.replace(' ', '_')}.json")
    
    global_state.to_json(output_file)
    print(f"\nLe résultat complet a été sauvegardé dans: {output_file}")
    
    return True

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Test de conversion UserDocument -> GlobalState")
    parser.add_argument("cv_name", nargs="?", default="Développeur Full Stack Senior", 
                        help="Nom du CV à utiliser pour la conversion")
    
    args = parser.parse_args()
    
    test_conversion(args.cv_name)

if __name__ == "__main__":
    main() 