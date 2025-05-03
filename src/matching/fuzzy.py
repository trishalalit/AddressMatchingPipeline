from sqlalchemy import text
import logging
from typing import List, Dict, Any, Tuple, Optional
from ..db.connection import get_db_session

logger = logging.getLogger(__name__)

class FuzzyMatcher:
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.logger = logging.getLogger(__name__)
        self.similarity_threshold = similarity_threshold
    
    def match(self, transaction_ids: List[str] = None, batch_size: int = 1000) -> int:
        if transaction_ids:
            return fuzzy_match(transaction_ids, self.similarity_threshold, batch_size)
        else:
            return process_all_fuzzy_matches(self.similarity_threshold)
    
    def find_best_match(self, normalized_address: str, canonical_dict: Dict[int, str]) -> Optional[Tuple[int, float]]:
        if not normalized_address:
            return None
            
        best_score = self.similarity_threshold
        best_match = None
        
        for canonical_id, canonical_address in canonical_dict.items():
            if not canonical_address:
                continue
            score = self._calculate_similarity(normalized_address.lower(), canonical_address.lower())
            
            if score > best_score:
                best_score = score
                best_match = canonical_id
                
        return (best_match, best_score) if best_match else None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        if not str1 or not str2:
            return 0.0
        set1 = set(str1)
        set2 = set(str2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0

def fuzzy_match(transaction_ids: List[str], similarity_threshold: float = 0.7, batch_size: int = 1000) -> int:
    logger.info(f"Starting fuzzy matching for {len(transaction_ids)} transactions with threshold {similarity_threshold}")
    
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
        'fuzzy',
        similarity(LOWER(t.normalized_address), LOWER(ca.normalized_address)) as score
    FROM 
        transactions t
    JOIN 
        canonical_addresses ca ON (
            -- Same ZIP code for blocking
            t.zip_code = ca.zip
            -- And minimum similarity threshold
            AND similarity(LOWER(t.normalized_address), LOWER(ca.normalized_address)) >= :similarity_threshold
        )
    WHERE 
        t.id = :transaction_id
        -- Ensure not already matched
        AND NOT EXISTS (
            SELECT 1 FROM address_matches am WHERE am.transaction_id = t.id
        )
    ORDER BY
        score DESC
    LIMIT 1
    ON CONFLICT (transaction_id) DO NOTHING
    RETURNING transaction_id
    """
    
    total_matched = 0
    
    with get_db_session() as session:
        for transaction_id in transaction_ids:
            result = session.execute(
                text(match_query),
                {
                    "transaction_id": transaction_id,
                    "similarity_threshold": similarity_threshold
                }
            )
            
            if result.rowcount > 0:
                total_matched += 1
    
    logger.info(f"Fuzzy matching complete. Matched {total_matched} out of {len(transaction_ids)} transactions")
    return total_matched

def batch_fuzzy_match(similarity_threshold: float = 0.7, batch_size: int = 1000) -> int:
    logger.info(f"Starting batch fuzzy matching with threshold {similarity_threshold} and batch size {batch_size}")
    
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
    return fuzzy_match(unmatched_ids, similarity_threshold)

def process_all_fuzzy_matches(similarity_threshold: float = 0.7) -> int:
    logger.info(f"Processing all unmatched transactions with fuzzy matching, threshold {similarity_threshold}")
    
    total_matched = 0
    batch_size = 1000
    
    while True:
        matches = batch_fuzzy_match(similarity_threshold, batch_size)
        total_matched += matches
        
        if matches == 0:
            break
    
    logger.info(f"Completed all fuzzy matching. Total matched: {total_matched}")
    return total_matched 