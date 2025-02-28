from firebase_admin import firestore
import logging

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
        user_ref = db.collection('users').document(user_id)
        
        # Utiliser une transaction pour garantir l'atomicité
        @firestore.transactional
        def update_in_transaction(transaction, user_ref):
            snapshot = user_ref.get(transaction=transaction)
            current_stats = snapshot.get('token_stats', {
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_cost': 0
            })
            
            # Mettre à jour les compteurs
            current_stats['total_input_tokens'] += input_tokens
            current_stats['total_output_tokens'] += output_tokens
            
            # Calculer le coût (à ajuster selon vos tarifs)
            input_cost = (input_tokens / 1000) * 0.01  # $0.01 par 1K tokens
            output_cost = (output_tokens / 1000) * 0.03  # $0.03 par 1K tokens
            current_stats['total_cost'] += input_cost + output_cost
            
            transaction.update(user_ref, {'token_stats': current_stats})
        
        # Exécuter la transaction
        transaction = db.transaction()
        update_in_transaction(transaction, user_ref)
        logger.info(f"Compteurs de tokens mis à jour pour l'utilisateur {user_id}")
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des compteurs de tokens: {str(e)}")
        # Ne pas lever l'erreur pour ne pas bloquer le processus principal 