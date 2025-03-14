from ai_module.models.generate_profile import generate_profile as generate_profile_impl
from ai_module.models.generate_head import generate_structured_head as generate_head_impl
from ai_module.new_models.global_chain import compiled_main_graph
from ai_module.new_models.lg_models import GlobalState
import logging
from typing import Dict

logger = logging.getLogger(__name__)

async def generate_profile(text: str) -> Dict:
    """
    Wrapper pour generate_profile
    """
    return await generate_profile_impl(text)

async def generate_head(text: str) -> Dict:
    """
    Wrapper pour generate_head
    """
    return await generate_head_impl(text)

def generate_cv(state: GlobalState) -> GlobalState:
    """
    Exécute la chaîne de traitement LangChain pour générer un CV optimisé
    
    Args:
        state (GlobalState): L'état global initial contenant les données brutes du profil
        
    Returns:
        GlobalState: L'état global mis à jour avec les données optimisées pour le CV
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
