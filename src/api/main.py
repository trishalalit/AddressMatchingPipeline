from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import time
from sqlalchemy import text

from ..db.connection import get_db_session
from ..processing.parser import AddressParser
from ..processing.normalizer import AddressNormalizer
from ..matching.exact import exact_match
from ..matching.fuzzy import fuzzy_match
from ..matching.phonetic import phonetic_match
from ..matching.api import api_match

logger = logging.getLogger(__name__)
app = FastAPI(
    title="Address Matching API",
    description="API for matching addresses against canonical database",
    version="1.0.0"
)
class AddressRequest(BaseModel):
    address_line_1: str = Field(..., description="Primary address line")
    address_line_2: Optional[str] = Field(None, description="Secondary address line (unit, apt, etc.)")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State (2-letter code)")
    zip_code: int = Field(..., description="ZIP code")

class MatchResult(BaseModel):
    hhid: str = Field(..., description="Canonical address ID")
    address: str = Field(..., description="Full canonical address")
    confidence_score: float = Field(..., description="Match confidence score (0-1)")
    match_type: str = Field(..., description="Type of match (exact, fuzzy, phonetic, api)")

class AddressMatchResponse(BaseModel):
    address: AddressRequest = Field(..., description="Input address")
    matches: List[MatchResult] = Field(..., description="Matching results")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")

@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "api": "Address Matching API",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "API information"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/match_address", "method": "POST", "description": "Match an address"}
        ]
    }
@app.get("/health")
def health_check():
    """Health check endpoint."""
    try:
        with get_db_session() as session:
            session.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": str(e)
        }
@app.post("/match_address", response_model=AddressMatchResponse)
def match_address(address: AddressRequest):
    """
    Match an address against the canonical database.
    
    Uses a waterfall approach:
    1. Exact matching
    2. Fuzzy matching
    3. Phonetic matching
    4. External API fallback
    """
    start_time = time.time()
    parser = AddressParser()
    normalizer = AddressNormalizer()
    parsed_components = parser.parse(address.address_line_1, address.address_line_2)
    normalized_components = normalizer.normalize_address_components(parsed_components)
    normalized_address = normalizer.build_normalized_address(normalized_components)
    temp_id = f"temp_{int(time.time() * 1000)}"
    insert_query = """
    INSERT INTO transactions (
        id, 
        status,
        price, 
        bedrooms, 
        bathrooms, 
        square_feet,
        address_line_1, 
        address_line_2, 
        city, 
        state, 
        zip_code,
        normalized_address,
        parsed_house,
        parsed_predir,
        parsed_street,
        parsed_strtype,
        parsed_postdir,
        parsed_apttype,
        parsed_aptnbr
    ) VALUES (
        :id, 
        'TEMP',
        0,
        0,
        0,
        0,
        :address_line_1, 
        :address_line_2, 
        :city, 
        :state, 
        :zip_code,
        :normalized_address,
        :parsed_house,
        :parsed_predir,
        :parsed_street,
        :parsed_strtype,
        :parsed_postdir,
        :parsed_apttype,
        :parsed_aptnbr
    )
    """
    with get_db_session() as session:
        session.execute(text(insert_query), {
            "id": temp_id,
            "address_line_1": address.address_line_1,
            "address_line_2": address.address_line_2 or "",
            "city": address.city,
            "state": address.state,
            "zip_code": address.zip_code,
            "normalized_address": normalized_address,
            "parsed_house": normalized_components.get("parsed_house", ""),
            "parsed_predir": normalized_components.get("parsed_predir", ""),
            "parsed_street": normalized_components.get("parsed_street", ""),
            "parsed_strtype": normalized_components.get("parsed_strtype", ""),
            "parsed_postdir": normalized_components.get("parsed_postdir", ""),
            "parsed_apttype": normalized_components.get("parsed_apttype", ""),
            "parsed_aptnbr": normalized_components.get("parsed_aptnbr", "")
        })
    matches = []
    with get_db_session() as session:
        query = """
        SELECT 
            ca.id as canonical_id,
            ca.hhid,
            ca.address,
            1.0 as confidence_score,
            'exact' as match_type
        FROM 
            canonical_addresses ca
        JOIN 
            transactions t ON 
                LOWER(ca.normalized_address) = LOWER(t.normalized_address) AND
                ca.zip = t.zip_code
        WHERE 
            t.id = :temp_id
        LIMIT 5
        """
        result = session.execute(text(query), {"temp_id": temp_id})
        matches = [dict(row._mapping) for row in result]
    if not matches:
        with get_db_session() as session:
            query = """
            SELECT 
                ca.id as canonical_id,
                ca.hhid,
                ca.address,
                similarity(LOWER(ca.normalized_address), LOWER((
                    SELECT normalized_address FROM transactions WHERE id = :temp_id
                ))) as confidence_score,
                'fuzzy' as match_type
            FROM 
                canonical_addresses ca
            JOIN 
                transactions t ON ca.zip = t.zip_code
            WHERE 
                t.id = :temp_id AND
                similarity(LOWER(ca.normalized_address), LOWER(t.normalized_address)) > 0.6
            ORDER BY 
                confidence_score DESC
            LIMIT 5
            """
            result = session.execute(text(query), {"temp_id": temp_id})
            matches = [dict(row._mapping) for row in result]
    with get_db_session() as session:
        session.execute(text("DELETE FROM transactions WHERE id = :id"), {"id": temp_id})
    processing_time = (time.time() - start_time) * 1000  
    return {
        "address": address,
        "matches": matches,
        "processing_time_ms": processing_time
    }
@app.get("/statistics")
def get_statistics():
    """Get matching statistics."""
    with get_db_session() as session:
        query = """
        SELECT 
            COUNT(*) as total_transactions,
            COUNT(DISTINCT am.transaction_id) as matched_transactions,
            COUNT(DISTINCT CASE WHEN am.match_type = 'exact' THEN am.transaction_id END) as exact_matches,
            COUNT(DISTINCT CASE WHEN am.match_type = 'fuzzy' THEN am.transaction_id END) as fuzzy_matches,
            COUNT(DISTINCT CASE WHEN am.match_type = 'phonetic' THEN am.transaction_id END) as phonetic_matches,
            COUNT(DISTINCT CASE WHEN am.match_type = 'api' THEN am.transaction_id END) as api_matches
        FROM 
            transactions t
        LEFT JOIN 
            address_matches am ON t.id = am.transaction_id
        WHERE 
            t.status != 'TEMP'
        """
        result = session.execute(text(query))
        stats = dict(result.mappings().fetchone())
        if stats['total_transactions'] > 0:
            stats['match_percentage'] = (stats['matched_transactions'] / stats['total_transactions']) * 100
        else:
            stats['match_percentage'] = 0            
    return stats 