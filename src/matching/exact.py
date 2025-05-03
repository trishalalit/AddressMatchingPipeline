from sqlalchemy import text
import logging
from typing import List, Dict, Any
from ..db.connection import get_db_session

logger = logging.getLogger(__name__)

class ExactMatcher:
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def match(self, transaction_ids: List[str] = None, batch_size: int = 1000) -> int:
        if transaction_ids:
            return exact_match(transaction_ids, batch_size)
        else:
            return process_all_exact_matches()

def exact_match(transaction_ids: List[str], batch_size: int = 1000) -> int:
    logger.info(f"Starting exact matching for {len(transaction_ids)} transactions")
    
    match_query = """
    INSERT INTO address_matches (
        transaction_id,
        canonical_address_id,
        match_type,
        confidence_score
    )
    SELECT 
        t.id,
        ca.id,
        'exact',
        1.0
    FROM 
        transactions t
    JOIN 
        canonical_addresses ca ON (
            -- Match on normalized address
            LOWER(t.normalized_address) = LOWER(ca.normalized_address)
            -- And same ZIP code
            AND t.zip_code = ca.zip
        )
    WHERE 
        t.id = :transaction_id
        -- Ensure not already matched
        AND NOT EXISTS (
            SELECT 1 FROM address_matches am WHERE am.transaction_id = t.id
        )
    LIMIT 1
    ON CONFLICT (transaction_id) DO NOTHING
    RETURNING transaction_id
    """
    
    total_matched = 0
    
    with get_db_session() as session:
        for transaction_id in transaction_ids:
            result = session.execute(
                text(match_query),
                {"transaction_id": transaction_id}
            )
            
            if result.rowcount > 0:
                total_matched += 1
    
    logger.info(f"Exact matching complete. Matched {total_matched} out of {len(transaction_ids)} transactions")
    return total_matched

def batch_exact_match(batch_size: int = 1000) -> int:
    logger.info(f"Starting batch exact matching with batch size {batch_size}")
    
    unmatched_query = """
    SELECT t.id
    FROM transactions t
    LEFT JOIN address_matches am ON t.id = am.transaction_id
    WHERE am.id IS NULL
    LIMIT :batch_size
    """
    
    with get_db_session() as session:
        unmatched_result = session.execute(text(unmatched_query), {"batch_size": batch_size})
        unmatched_ids = [row[0] for row in unmatched_result]
        
    if not unmatched_ids:
        logger.info("No unmatched transactions found")
        return 0
        
    logger.info(f"Found {len(unmatched_ids)} unmatched transactions")
    
    # Perform matching
    return exact_match(unmatched_ids)

def process_all_exact_matches() -> int:
    logger.info("Processing all unmatched transactions with exact matching")
    
    total_matched = 0
    batch_size = 1000
    
    while True:
        matches = batch_exact_match(batch_size)
        total_matched += matches
        
        if matches == 0:
            break
    
    logger.info(f"Completed all exact matching. Total matched: {total_matched}")
    return total_matched 