import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import text
from ..db.connection import get_db_session

logger = logging.getLogger(__name__)

class ApiMatcher:    
    def __init__(self, api_key: str, threshold: float = 0.7):
        self.logger = logging.getLogger(__name__)
        self.threshold = threshold
    
    def match(self, transaction_ids: List[str] = None, batch_size: int = 100) -> int:
        logger.info("API matching functionality has been disabled")
        return 0
    
    def standardize_address(self, address: Dict[str, Any]) -> Optional[str]:
        if not address.get('address_line_1'):
            return None
        components = []
        if address.get('address_line_1'):
            components.append(address['address_line_1'].strip())
        if address.get('address_line_2'):
            components.append(address['address_line_2'].strip())
        if address.get('city'):
            components.append(address['city'].strip())
        if address.get('state'):
            components.append(address['state'].strip())
        if address.get('zip_code'):
            components.append(str(address['zip_code']).strip())
        
        if not components:
            return None
            
        return ", ".join([c for c in components if c])
    
    def find_best_match(self, standardized_address: str, canonical_addresses: List[Tuple]) -> Optional[Tuple[int, float]]:
        # Local matching only, no API calls
        if not standardized_address:
            return None
            
        best_match = None
        best_score = self.threshold
        for ca in canonical_addresses:
            canonical_id = ca[0]
            ca_components = []
            if ca[1]:  # address_line_1
                ca_components.append(ca[1].strip())
            if ca[2]:  # address_line_2
                ca_components.append(ca[2].strip())
            if ca[3]:  # city
                ca_components.append(ca[3].strip())
            if ca[4]:  # state
                ca_components.append(ca[4].strip())
            if ca[5]:  # zip_code
                ca_components.append(str(ca[5]).strip())
            
            canonical_address = ", ".join([c for c in ca_components if c])
            
            if not canonical_address:
                continue
                
            score = self._calculate_similarity(standardized_address, canonical_address)
            
            if score > best_score:
                best_score = score
                best_match = canonical_id
                
        return (best_match, best_score) if best_match else None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        if not str1 or not str2:
            return 0.0
        s1 = str1.lower().replace(',', ' ').replace('  ', ' ')
        s2 = str2.lower().replace(',', ' ').replace('  ', ' ')
        words1 = set(s1.split())
        words2 = set(s2.split())
        
        if not words1 or not words2:
            return 0.0
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

def api_match(transaction_id: str) -> bool:
    # API matching has been disabled
    logger.info(f"API matching disabled for transaction {transaction_id}")
    return False

def get_canonical_id_for_api_match(address: str, zip_code: int) -> Optional[int]:
    # API matching has been disabled
    return None

def batch_api_match(batch_size: int = 100) -> int:
    # API matching has been disabled
    logger.info(f"Batch API matching has been disabled")
    return 0

def process_all_api_matches() -> int:
    # API matching has been disabled
    logger.info("API matching has been disabled")
    return 0 