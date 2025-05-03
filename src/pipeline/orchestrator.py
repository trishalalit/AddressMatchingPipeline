import os
import logging
import argparse
import time
from typing import List, Dict, Any
from tqdm import tqdm
from dotenv import load_dotenv
from sqlalchemy import text

from ..db.connection import get_db_session, check_database_connection
from ..ingestion.loader import load_canonical_addresses, load_transactions
from ..processing.parser import AddressParser
from ..processing.normalizer import AddressNormalizer
from ..matching.exact import process_all_exact_matches
from ..matching.fuzzy import process_all_fuzzy_matches
from ..matching.phonetic import process_all_phonetic_matches
from ..matching.api import process_all_api_matches

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Address Matching Pipeline')
    
    parser.add_argument('--canonical', default='data/11211 Addresses.xlsx',
                      help='Path to canonical addresses file')
    parser.add_argument('--transactions', default='data/transactions_2_11211.xlsx',
                      help='Path to transactions file')
    parser.add_argument('--skip-load', action='store_true',
                      help='Skip data loading step')
    parser.add_argument('--skip-parse', action='store_true',
                      help='Skip address parsing step')
    parser.add_argument('--skip-match', action='store_true',
                      help='Skip address matching step')
    parser.add_argument('--batch-size', type=int, default=1000,
                      help='Batch size for processing')
    
    return parser.parse_args()

def process_address_parsing():
    from ..db.session import SessionLocal
    
    parser = AddressParser()
    session = SessionLocal()
    
    try:
        # Counting records that need processing
        count_result = session.execute(text("SELECT COUNT(*) FROM transactions WHERE normalized_address IS NULL"))
        count = count_result.scalar()
        
        if count == 0:
            logging.info("No transactions need address parsing")
            return 0
        
        logging.info(f"Found {count} transactions needing address parsing")
        
        # Get transactions needing processing
        transactions = session.execute(
            text("SELECT id, address_line_1, address_line_2, city, state, zip_code FROM transactions WHERE normalized_address IS NULL")
        ).fetchall()
        
        processed_count = 0
        
        for transaction in transactions:
            trans_id = transaction[0]
            address_line_1 = transaction[1] or ""
            address_line_2 = transaction[2] or ""
            city = transaction[3] or ""
            state = transaction[4] or ""
            zip_code = str(transaction[5]) if transaction[5] else ""
            
            full_address = f"{address_line_1} {address_line_2}, {city}, {state} {zip_code}".strip()            
            parsed_address = parser.parse(full_address)
            
            if parsed_address:
                session.execute(
                    text("""
                    UPDATE transactions 
                    SET 
                        parsed_house = :house,
                        parsed_predir = :predir,
                        parsed_street = :street,
                        parsed_strtype = :strtype,
                        parsed_postdir = :postdir,
                        parsed_apttype = :apttype,
                        parsed_aptnbr = :aptnbr,
                        normalized_address = :normalized_address
                    WHERE id = :id
                    """),
                    {
                        "house": parsed_address.get("house", ""),
                        "predir": parsed_address.get("predir", ""),
                        "street": parsed_address.get("street", ""),
                        "strtype": parsed_address.get("strtype", ""),
                        "postdir": parsed_address.get("postdir", ""),
                        "apttype": parsed_address.get("apttype", ""),
                        "aptnbr": parsed_address.get("aptnbr", ""),
                        "normalized_address": parsed_address.get("normalized_address", ""),
                        "id": trans_id
                    }
                )
                processed_count += 1
                
                if processed_count % 100 == 0:
                    session.commit()
                    logging.info(f"Processed {processed_count} transactions")
            else:
                logging.warning(f"Failed to parse address for transaction {trans_id}: {full_address}")
        
        session.commit()
        logging.info(f"Completed address parsing for {processed_count} transactions")
        return processed_count
    
    except Exception as e:
        session.rollback()
        logging.error(f"Error in address parsing: {str(e)}")
        raise
    finally:
        session.close()

def process_matching_pipeline():
    logger.info("Starting matching pipeline")
    
    logger.info("Step 1: Exact matching")
    exact_matches = process_exact_matching()
    logger.info(f"Completed exact matching with {exact_matches} matches")
    if os.getenv("ENABLE_FUZZY_MATCHING", "true").lower() == "true":
        logger.info("Step 2: Fuzzy matching")
        fuzzy_matches = process_fuzzy_matching()
        logger.info(f"Completed fuzzy matching with {fuzzy_matches} matches")
    else:
        logger.info("Fuzzy matching disabled, skipping")
    if os.getenv("ENABLE_PHONETIC_MATCHING", "true").lower() == "true":
        logger.info("Step 3: Phonetic matching")
        phonetic_matches = process_phonetic_matching()
        logger.info(f"Completed phonetic matching with {phonetic_matches} matches")
    else:
        logger.info("Phonetic matching disabled, skipping")
    
    logger.info("API matching has been disabled by configuration")
    
    stats = get_match_status()
    logger.info(f"Matching pipeline completed with results: {stats}")
    
    return stats

def process_exact_matching():
    from ..matching.exact import ExactMatcher
    from ..db.session import SessionLocal
    
    matcher = ExactMatcher()
    session = SessionLocal()
    
    try:
        # Get count of unmatched transactions
        count_result = session.execute(
            text("SELECT COUNT(*) FROM transactions WHERE match_status IS NULL OR match_status = 'pending'")
        )
        unmatched_count = count_result.scalar()
        
        if unmatched_count == 0:
            logger.info("No transactions need exact matching")
            return 0
        
        logger.info(f"Found {unmatched_count} transactions for exact matching")
        
        # Get transactions for matching
        # Exact matching typically matches on normalized_address
        transactions = session.execute(
            text("""
            SELECT id, normalized_address
            FROM transactions 
            WHERE (match_status IS NULL OR match_status = 'pending')
                AND normalized_address IS NOT NULL
            """)
        ).fetchall()
        
        # Get canonical addresses for comparison
        canonical_addresses = session.execute(
            text("""
            SELECT id, normalized_address
            FROM canonical_addresses
            WHERE normalized_address IS NOT NULL
            """)
        ).fetchall()
        
        matched_count = 0
        
        # Create dictionary of canonical addresses for faster lookup
        canonical_dict = {addr[1]: addr[0] for addr in canonical_addresses if addr[1]}
        
        # Process each transaction
        for transaction in transactions:
            transaction_id = transaction[0]
            normalized_address = transaction[1]
            
            if not normalized_address or normalized_address not in canonical_dict:
                continue
                
            # We have an exact match
            canonical_id = canonical_dict[normalized_address]
            
            # Update transaction match status
            session.execute(
                text("""
                UPDATE transactions
                SET 
                    match_status = 'matched',
                    match_score = 1.0,
                    match_timestamp = CURRENT_TIMESTAMP
                WHERE id = :transaction_id
                """),
                {
                    "transaction_id": transaction_id
                }
            )
            
            # Add match to address_matches table
            session.execute(
                text("""
                INSERT INTO address_matches (
                    transaction_id,
                    canonical_address_id,
                    match_type,
                    confidence_score
                ) VALUES (
                    :transaction_id,
                    :canonical_id,
                    'exact',
                    1.0
                )
                ON CONFLICT (transaction_id) DO UPDATE
                SET 
                    canonical_address_id = :canonical_id,
                    match_type = 'exact',
                    confidence_score = 1.0
                """),
                {
                    "transaction_id": transaction_id,
                    "canonical_id": canonical_id
                }
            )
            
            matched_count += 1
            
            if matched_count % 100 == 0:
                session.commit()
                logger.info(f"Processed {matched_count} exact matches")
        
        session.commit()
        logger.info(f"Completed exact matching with {matched_count} matches")
        return matched_count
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error in exact matching: {str(e)}")
        raise
    finally:
        session.close()

def process_fuzzy_matching():
    from ..matching.fuzzy import FuzzyMatcher
    from ..db.session import SessionLocal
    
    # Configuration
    threshold = float(os.getenv("FUZZY_MATCH_THRESHOLD", "0.8"))
    matcher = FuzzyMatcher(similarity_threshold=threshold)
    session = SessionLocal()
    
    try:
        # Get count of unmatched transactions
        count_result = session.execute(
            text("SELECT COUNT(*) FROM transactions WHERE match_status IS NULL OR match_status = 'pending'")
        )
        unmatched_count = count_result.scalar()
        
        if unmatched_count == 0:
            logger.info("No transactions need fuzzy matching")
            return 0
        
        logger.info(f"Found {unmatched_count} transactions for fuzzy matching")
        
        # Get transactions for matching
        transactions = session.execute(
            text("""
            SELECT id, normalized_address
            FROM transactions 
            WHERE (match_status IS NULL OR match_status = 'pending')
                AND normalized_address IS NOT NULL
            """)
        ).fetchall()
        
        # Get canonical addresses for comparison
        canonical_addresses = session.execute(
            text("""
            SELECT id, normalized_address
            FROM canonical_addresses
            WHERE normalized_address IS NOT NULL
            """)
        ).fetchall()
        
        # Create dictionary of canonical addresses
        canonical_dict = {addr[0]: addr[1] for addr in canonical_addresses if addr[1]}
        
        matched_count = 0
        
        # Process each transaction
        for transaction in transactions:
            transaction_id = transaction[0]
            normalized_address = transaction[1]
            
            if not normalized_address:
                continue
            
            # Find best fuzzy match
            best_match = matcher.find_best_match(normalized_address, canonical_dict)
            
            if best_match:
                canonical_id, score = best_match
                
                # Update transaction with match status
                session.execute(
                    text("""
                    UPDATE transactions
                    SET 
                        match_status = 'matched',
                        match_score = :score,
                        match_timestamp = CURRENT_TIMESTAMP
                    WHERE id = :transaction_id
                    """),
                    {
                        "score": score,
                        "transaction_id": transaction_id
                    }
                )
                
                # Add match to address_matches table
                session.execute(
                    text("""
                    INSERT INTO address_matches (
                        transaction_id,
                        canonical_address_id,
                        match_type,
                        confidence_score
                    ) VALUES (
                        :transaction_id,
                        :canonical_id,
                        'fuzzy',
                        :score
                    )
                    ON CONFLICT (transaction_id) DO UPDATE
                    SET 
                        canonical_address_id = :canonical_id,
                        match_type = 'fuzzy',
                        confidence_score = :score
                    """),
                    {
                        "transaction_id": transaction_id,
                        "canonical_id": canonical_id,
                        "score": score
                    }
                )
                
                matched_count += 1
                
                if matched_count % 100 == 0:
                    session.commit()
                    logger.info(f"Processed {matched_count} fuzzy matches")
        
        session.commit()
        logger.info(f"Completed fuzzy matching with {matched_count} matches")
        return matched_count
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error in fuzzy matching: {str(e)}")
        raise
    finally:
        session.close()

def process_phonetic_matching():
    from ..matching.phonetic import PhoneticMatcher
    from ..db.session import SessionLocal
    
    # Configuration
    threshold = float(os.getenv("PHONETIC_MATCH_THRESHOLD", "0.7"))
    matcher = PhoneticMatcher(threshold=threshold)
    session = SessionLocal()
    
    try:
        # Get count of unmatched transactions
        count_result = session.execute(
            text("SELECT COUNT(*) FROM transactions WHERE match_status IS NULL OR match_status = 'pending'")
        )
        unmatched_count = count_result.scalar()
        
        if unmatched_count == 0:
            logger.info("No transactions need phonetic matching")
            return 0
        
        logger.info(f"Found {unmatched_count} transactions for phonetic matching")
        
        # Get transactions for matching - use the correct field names from the schema
        transactions = session.execute(
            text("""
            SELECT id, parsed_street, parsed_house, parsed_apttype, parsed_aptnbr
            FROM transactions 
            WHERE (match_status IS NULL OR match_status = 'pending')
                AND parsed_street IS NOT NULL
            """)
        ).fetchall()
        
        # Get canonical addresses for comparison
        canonical_addresses = session.execute(
            text("""
            SELECT id, street, house, apttype, aptnbr
            FROM canonical_addresses
            WHERE street IS NOT NULL
            """)
        ).fetchall()
        
        matched_count = 0
        
        # Process each transaction
        for transaction in transactions:
            transaction_id = transaction[0]
            street_name = transaction[1]  # parsed_street
            street_number = transaction[2]  # parsed_house
            apt_type = transaction[3]  # parsed_apttype
            apt_number = transaction[4]  # parsed_aptnbr
            
            # Combine apt_type and apt_number for unit
            unit = None
            if apt_type and apt_number:
                unit = f"{apt_type} {apt_number}"
            elif apt_number:
                unit = apt_number
            
            if not street_name:
                continue
            
            # Find best phonetic match
            best_match = matcher.find_best_match(
                street_name, 
                street_number, 
                unit, 
                canonical_addresses
            )
            
            if best_match:
                canonical_id, score = best_match
                
                # Update transaction with match
                session.execute(
                    text("""
                    UPDATE transactions
                    SET 
                        match_status = 'matched',
                        match_score = :score,
                        match_timestamp = CURRENT_TIMESTAMP
                    WHERE id = :transaction_id
                    """),
                    {
                        "score": score,
                        "transaction_id": transaction_id
                    }
                )
                
                # Add match to address_matches table
                session.execute(
                    text("""
                    INSERT INTO address_matches (
                        transaction_id,
                        canonical_address_id,
                        match_type,
                        confidence_score
                    ) VALUES (
                        :transaction_id,
                        :canonical_id,
                        'phonetic',
                        :score
                    )
                    ON CONFLICT (transaction_id) DO UPDATE
                    SET 
                        canonical_address_id = :canonical_id,
                        match_type = 'phonetic',
                        confidence_score = :score
                    """),
                    {
                        "transaction_id": transaction_id,
                        "canonical_id": canonical_id,
                        "score": score
                    }
                )
                
                matched_count += 1
                
                if matched_count % 100 == 0:
                    session.commit()
                    logger.info(f"Processed {matched_count} phonetic matches")
        
        session.commit()
        logger.info(f"Completed phonetic matching with {matched_count} matches")
        return matched_count
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error in phonetic matching: {str(e)}")
        raise
    finally:
        session.close()

def process_api_matching():
    logger.info("API matching functionality has been disabled")
    return 0

def process_export():
    import csv
    import os
    from datetime import datetime
    from ..db.session import SessionLocal
    
    output_dir = os.path.join(os.getcwd(), "results")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"matching_results_{timestamp}.csv")
    
    session = SessionLocal()
    
    try:
        # Get matched transactions with their canonical address
        results = session.execute(
            text("""
            SELECT 
                t.id as transaction_id,
                t.address_line_1 as transaction_address_1,
                t.address_line_2 as transaction_address_2,
                t.city as transaction_city,
                t.state as transaction_state,
                t.zip_code as transaction_zip,
                t.normalized_address as normalized_transaction,
                c.id as canonical_id,
                c.address as canonical_address_1,
                NULL as canonical_address_2,
                c.city as canonical_city,
                c.state as canonical_state,
                c.zip as canonical_zip,
                c.normalized_address as normalized_canonical,
                am.match_type,
                t.match_score,
                t.match_status
            FROM 
                transactions t
            LEFT JOIN 
                address_matches am ON t.id = am.transaction_id
            LEFT JOIN 
                canonical_addresses c ON am.canonical_address_id = c.id
            ORDER BY
                t.match_status, t.match_score DESC
            """)
        ).fetchall()
        
        # Write to CSV
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = [
                'transaction_id', 'transaction_address_1', 'transaction_address_2',
                'transaction_city', 'transaction_state', 'transaction_zip',
                'normalized_transaction', 'canonical_id', 'canonical_address_1',
                'canonical_address_2', 'canonical_city', 'canonical_state',
                'canonical_zip', 'normalized_canonical', 'match_type',
                'match_score', 'match_status'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in results:
                writer.writerow({
                    'transaction_id': row[0],
                    'transaction_address_1': row[1],
                    'transaction_address_2': row[2],
                    'transaction_city': row[3],
                    'transaction_state': row[4],
                    'transaction_zip': row[5],
                    'normalized_transaction': row[6],
                    'canonical_id': row[7],
                    'canonical_address_1': row[8],
                    'canonical_address_2': row[9],
                    'canonical_city': row[10],
                    'canonical_state': row[11],
                    'canonical_zip': row[12],
                    'normalized_canonical': row[13],
                    'match_type': row[14],
                    'match_score': row[15],
                    'match_status': row[16]
                })
        
        logger.info(f"Exported {len(results)} results to {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"Error exporting results: {str(e)}")
        raise
    finally:
        session.close()

def get_match_status():
    from ..db.session import SessionLocal
    
    session = SessionLocal()
    try:
        match_counts = session.execute(
            text("""
            SELECT am.match_type, COUNT(*) as count 
            FROM transactions t
            JOIN address_matches am ON t.id = am.transaction_id
            WHERE t.match_status = 'matched' 
            GROUP BY am.match_type
            """)
        ).fetchall()
        
        # Get overall statistics
        stats = session.execute(
            text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN match_status = 'matched' THEN 1 ELSE 0 END) as matched,
                SUM(CASE WHEN match_status = 'unmatched' THEN 1 ELSE 0 END) as unmatched,
                SUM(CASE WHEN match_status = 'pending' THEN 1 ELSE 0 END) as pending
            FROM transactions
            """)
        ).fetchone()
        
        return {
            "total": stats[0] if stats else 0,
            "matched": stats[1] if stats else 0,
            "unmatched": stats[2] if stats else 0,
            "pending": stats[3] if stats else 0,
            "match_sources": {source: count for source, count in match_counts}
        }
    except Exception as e:
        logger.error(f"Error getting match status: {str(e)}")
        return {"error": str(e)}
    finally:
        session.close()

def main():
    args = parse_arguments()
    
    if not check_database_connection():
        logger.error("Database connection failed. Exiting.")
        return
    
    pipeline_start = time.time()
    
    if not args.skip_load:
        logger.info("Step 1: Loading data")
        canonical_count = load_canonical_addresses(args.canonical)
        logger.info(f"Loaded {canonical_count} canonical addresses")
        
        transaction_count = load_transactions(args.transactions)
        logger.info(f"Loaded {transaction_count} transactions")
    else:
        logger.info("Skipping data loading step")
    
    if not args.skip_parse:
        logger.info("Step 2: Parsing addresses")
        processed_count = process_address_parsing()
        logger.info(f"Processed {processed_count} addresses")
    else:
        logger.info("Skipping address parsing step")
    
    if not args.skip_match:
        logger.info("Step 3: Matching addresses")
        match_results = process_matching_pipeline()
    else:
        logger.info("Skipping address matching step")
    
    logger.info("Step 4: Exporting results")
    process_export()
    
    pipeline_end = time.time()
    total_runtime = pipeline_end - pipeline_start
    
    logger.info(f"Pipeline completed in {total_runtime:.2f} seconds")

if __name__ == "__main__":
    main() 