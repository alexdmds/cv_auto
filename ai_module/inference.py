from ai_module.new_models.global_chain import compiled_main_graph
from ai_module.lg_models import CVGenState, ProfileState
from ai_module.models.generate_profile_chain import create_profile_graph
import logging
from typing import Dict

logger = logging.getLogger(__name__)

async def generate_profile(profile_state: ProfileState) -> ProfileState:
    """
    Exécute le workflow LangGraph pour extraire les informations structurées d'un CV brut
    
    Args:
        profile_state (ProfileState): L'état contenant le texte brut à analyser
        
    Returns:
        ProfileState: L'état mis à jour avec les informations extraites (head, experiences, education)
    """
    logger.info("Démarrage de l'extraction du profil avec LangGraph")
    
    try:
        # Création et compilation du graphe
        profile_graph = create_profile_graph().compile()
        
        # Exécution du graphe
        result = await profile_graph.ainvoke(profile_state)
        
        logger.info("Extraction du profil terminée avec succès")
        logger.info(f"Informations extraites: head, experiences ({len(result.get('experiences', []))}), education ({len(result.get('education', []))})")
        
        return result
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du profil: {str(e)}", exc_info=True)
        # En cas d'erreur, on retourne l'état initial
        return profile_state


def generate_cv(state: CVGenState) -> CVGenState:
    """
    Exécute la chaîne de traitement LangChain pour générer un CV optimisé
    
    Args:
        state (CVGenState): L'état global initial contenant les données brutes du profil
        
    Returns:
        CVGenState: L'état global mis à jour avec les données optimisées pour le CV
    """
    logger.info("Démarrage de la génération du CV avec LangChain")
    
    try:
        # Exécution du graphe LangChain
        result = compiled_main_graph.invoke(state)
        
        # Le résultat est déjà un GlobalState
        logger.info("Génération du CV terminée avec succès")
        
        # Définir l'état comme complété
        result.status = "completed"
        
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la génération du CV: {str(e)}", exc_info=True)
        
        # En cas d'erreur, retourner l'état initial mais marquer comme échoué
        state.status = "failed"
        state.error_message = str(e)
        
        return state
