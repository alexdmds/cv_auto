from firebase_admin import firestore
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def increment_token_count(user_id: str, input_tokens: int, output_tokens: int):
    """
    Incrémente le compteur de tokens pour un utilisateur.
    
    Args:
        user_id (str): ID de l'utilisateur
        input_tokens (int): Nombre de tokens en entrée
        output_tokens (int): Nombre de tokens en sortie
    """
    try:
        db = firestore.Client()
        
        # Référence au document des statistiques globales de l'utilisateur
        stats_ref = db.collection('token_stats').document(user_id)
        
        # Référence pour l'historique détaillé
        history_ref = db.collection('token_history').document()
        
        # Utiliser une transaction pour garantir l'atomicité
        @firestore.transactional
        def update_in_transaction(transaction, stats_doc_ref):
            doc = stats_doc_ref.get(transaction=transaction)
            if doc.exists:
                current_stats = doc.to_dict()
            else:
                current_stats = {
                    'user_id': user_id,
                    'total_input_tokens': 0,
                    'total_output_tokens': 0,
                    'total_cost': 0,
                    'created_at': datetime.utcnow(),
                }
            
            # Mettre à jour les compteurs avec des valeurs par défaut
            current_stats['total_input_tokens'] = current_stats.get('total_input_tokens', 0) + input_tokens
            current_stats['total_output_tokens'] = current_stats.get('total_output_tokens', 0) + output_tokens
            
            # Calculer le coût
            input_cost = (input_tokens / 1000) * 0.01  # $0.01 par 1K tokens
            output_cost = (output_tokens / 1000) * 0.03  # $0.03 par 1K tokens
            current_stats['total_cost'] = current_stats.get('total_cost', 0) + input_cost + output_cost
            current_stats['updated_at'] = datetime.utcnow()
            
            # Enregistrer l'historique détaillé
            history_data = {
                'user_id': user_id,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'input_cost': input_cost,
                'output_cost': output_cost,
                'total_cost': input_cost + output_cost,
                'timestamp': datetime.utcnow()
            }
            
            # Mettre à jour les deux documents dans la transaction
            transaction.set(stats_doc_ref, current_stats, merge=True)
            transaction.set(history_ref, history_data)
        
        # Exécuter la transaction
        transaction = db.transaction()
        update_in_transaction(transaction, stats_ref)
        
        logger.info(f"Compteurs de tokens mis à jour pour l'utilisateur {user_id}")
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des compteurs de tokens: {str(e)}")
        # Ne pas lever l'erreur pour ne pas bloquer le processus principal 