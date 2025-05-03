from sqlalchemy import text
import logging
from typing import List, Dict, Any, Tuple, Optional
from ..db.connection import get_db_session

logger = logging.getLogger(__name__)

class PhoneticMatcher:
    def __init__(self, threshold: float = 0.7):
        """
        Initialize the PhoneticMatcher.
        
        Args:
            threshold: Minimum phonetic match confidence score
        """
        self.logger = logging.getLogger(__name__)
        self.threshold = threshold
    
    def match(self, transaction_ids: List[str] = None, batch_size: int = 1000) -> int:
        """
        Match transactions against canonical addresses using phonetic matching.
        
        Args:
            transaction_ids: Optional list of transaction IDs to match. If None, processes all unmatched.
            batch_size: Number of transactions to process in each batch
            
        Returns:
            Number of successful matches
        """
        if transaction_ids:
            return phonetic_match(transaction_ids, batch_size)
        else:
            return process_all_phonetic_matches()
            
    def find_best_match(self, street_name: str, street_number: str, unit: str, canonical_addresses: List[Tuple]) -> Optional[Tuple[int, float]]:
        """
        Find the best phonetic match for a given address among canonical addresses.
        
        Args:
            street_name: The street name to match
            street_number: The street number/house number
            unit: The unit/apartment number
            canonical_addresses: List of tuples with canonical address data
            
        Returns:
            Tuple of (canonical_id, score) for the best match, or None if no match
        """
        if not street_name or not street_number:
            return None
            
        best_match = None
        best_score = self.threshold
        
        for ca in canonical_addresses:
            canonical_id = ca[0]
            ca_street_name = ca[1]
            ca_street_number = ca[2]
            ca_unit = ca[3]
            
            if not ca_street_name or not ca_street_number:
                continue
                
            score = 0.0
            
            if self._are_phonetically_similar(street_name, ca_street_name):
                score += 0.6
                
            if street_number == ca_street_number:
                score += 0.3
                
            if unit and ca_unit and unit == ca_unit:
                score += 0.1
                
            if score > best_score:
                best_score = score
                best_match = canonical_id
                
        return (best_match, best_score) if best_match else None
        
    def _are_phonetically_similar(self, str1: str, str2: str) -> bool:
        def simplify(s):
            return ''.join([c for c in s.lower() if c not in 'aeiou '])
        s1 = simplify(str1)
        s2 = simplify(str2)
        max_len = max(len(s1), len(s2))
        allowed_diff = max(1, max_len // 4)
        dist = self._levenshtein_distance(s1, s2)
        
        return dist <= allowed_diff
        
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
            
        if len(s2) == 0:
            return len(s1)
            
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]

def phonetic_match(transaction_ids: List[str], batch_size: int = 1000) -> int:
    logger.info(f"Starting phonetic matching for {len(transaction_ids)} transactions")
    
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
        'phonetic',
        0.8  -- Fixed confidence score for phonetic matches
    FROM 
        transactions t
    JOIN 
        canonical_addresses ca ON (
            -- Same ZIP code for blocking
            t.zip_code = ca.zip
            -- Metaphone match on street name
            AND CASE WHEN t.parsed_street IS NOT NULL AND ca.street IS NOT NULL THEN
                  metaphone(t.parsed_street, 10) = metaphone(ca.street, 10)
                ELSE false END
            -- House number match
            AND CASE WHEN t.parsed_house IS NOT NULL AND ca.house IS NOT NULL THEN
                  t.parsed_house = ca.house
                ELSE false END
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
    
    logger.info(f"Phonetic matching complete. Matched {total_matched} out of {len(transaction_ids)} transactions")
    return total_matched

def batch_phonetic_match(batch_size: int = 1000) -> int:
    logger.info(f"Starting batch phonetic matching with batch size {batch_size}")
    
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
    return phonetic_match(unmatched_ids)

def process_all_phonetic_matches() -> int:
    logger.info("Processing all unmatched transactions with phonetic matching")
    
    total_matched = 0
    batch_size = 1000
    
    while True:
        matches = batch_phonetic_match(batch_size)
        total_matched += matches
        
        if matches == 0:
            break
    
    logger.info(f"Completed all phonetic matching. Total matched: {total_matched}")
    return total_matched 