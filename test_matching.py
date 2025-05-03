#!/usr/bin/env python3

import os
import sys
import logging
import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import argparse
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgrespassword")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "address_matching")

db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_canonical_addresses():
    logger.info("Adding canonical addresses for testing")
    
    session = SessionLocal()
    try:
        count_result = session.execute(
            text("SELECT COUNT(*) FROM canonical_addresses")
        ).scalar()
        
        if count_result > 0:
            logger.info(f"Found {count_result} existing canonical addresses, skipping insertion")
            return count_result
        
        transactions = session.execute(
            text("""
            SELECT id, address_line_1, address_line_2, city, state, zip_code, normalized_address
            FROM transactions
            ORDER BY id
            LIMIT 10
            """)
        ).fetchall()
        
        canonical_addresses_added = 0
        
        for i, t in enumerate(transactions):
            if i % 3 != 0:
                continue
                
            transaction_id = t[0]
            address = t[1]
            address_line_2 = t[2] if t[2] else ""
            city = t[3]
            state = t[4]
            zip_code = t[5]
            
            normalized_address = f"{address} {address_line_2} {city} {state} {zip_code}".strip()
            normalized_address = ' '.join(normalized_address.split())
            
            hhid = f"HH{i+1000}"
            
            parts = address.split(' ', 1)
            house = parts[0] if len(parts) > 0 else ""
            street = parts[1] if len(parts) > 1 else address
            
            canonical_address = address
            if i % 2 == 0:
                if "Street" in canonical_address:
                    canonical_address = canonical_address.replace("Street", "St")
                elif "Avenue" in canonical_address:
                    canonical_address = canonical_address.replace("Avenue", "Ave")
                elif "Road" in canonical_address:
                    canonical_address = canonical_address.replace("Road", "Rd")
            
            session.execute(
                text("""
                INSERT INTO canonical_addresses
                (hhid, fname, lname, address, city, state, zip, normalized_address, street, house)
                VALUES (:hhid, 'Test', 'User', :address, :city, :state, :zip_code, :normalized_address, :street, :house)
                """),
                {
                    "hhid": hhid,
                    "address": canonical_address,
                    "city": city,
                    "state": state,
                    "zip_code": zip_code,
                    "normalized_address": normalized_address,
                    "street": street,
                    "house": house
                }
            )
            canonical_addresses_added += 1
        
        session.commit()
        logger.info(f"Created {canonical_addresses_added} canonical addresses for testing")
        return canonical_addresses_added
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding canonical addresses: {str(e)}")
        raise
    finally:
        session.close()

def normalize_transaction_addresses():
    logger.info("Normalizing transaction addresses")
    
    session = SessionLocal()
    try:
        count_result = session.execute(
            text("SELECT COUNT(*) FROM transactions WHERE normalized_address IS NULL OR normalized_address = ''")
        ).scalar()
        
        if count_result == 0:
            logger.info("All transactions already have normalized addresses")
            return 0
        
        logger.info(f"Found {count_result} transactions needing address normalization")
        
        transactions = session.execute(
            text("""
            SELECT id, address_line_1, address_line_2, city, state, zip_code 
            FROM transactions 
            WHERE normalized_address IS NULL OR normalized_address = ''
            """)
        ).fetchall()
        
        normalized_count = 0
        
        for transaction in transactions:
            trans_id = transaction[0]
            address_line_1 = transaction[1] or ""
            address_line_2 = transaction[2] or ""
            city = transaction[3] or ""
            state = transaction[4] or ""
            zip_code = str(transaction[5]) if transaction[5] else ""
            
            normalized_address = f"{address_line_1} {address_line_2} {city} {state} {zip_code}".strip()
            normalized_address = ' '.join(normalized_address.split())
            
            session.execute(
                text("""
                UPDATE transactions 
                SET normalized_address = :normalized_address
                WHERE id = :id
                """),
                {
                    "normalized_address": normalized_address,
                    "id": trans_id
                }
            )
            
            normalized_count += 1
            
            if normalized_count % 100 == 0:
                session.commit()
                logger.info(f"Normalized {normalized_count} transaction addresses")
        
        session.commit()
        logger.info(f"Completed address normalization for {normalized_count} transactions")
        return normalized_count
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error normalizing addresses: {str(e)}")
        raise
    finally:
        session.close()

def add_missing_column():
    logger.info("Checking for missing match_timestamp column in transactions table")
    
    session = SessionLocal()
    try:
        result = session.execute(
            text("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name='transactions' AND column_name='match_timestamp'
            )
            """)
        ).scalar()
        
        if result:
            logger.info("match_timestamp column already exists in transactions table")
            return
        
        logger.info("Adding missing match_timestamp column to transactions table")
        session.execute(
            text("""
            ALTER TABLE transactions 
            ADD COLUMN match_timestamp TIMESTAMP
            """)
        )
        session.commit()
        logger.info("Added match_timestamp column to transactions table")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding missing column: {str(e)}")
        raise
    finally:
        session.close()

def lower_matching_thresholds():
    logger.info("Setting lower matching thresholds")
    
    os.environ["FUZZY_MATCH_THRESHOLD"] = "0.6"
    os.environ["PHONETIC_MATCH_THRESHOLD"] = "0.5"
    
    logger.info(f"Set FUZZY_MATCH_THRESHOLD to {os.environ['FUZZY_MATCH_THRESHOLD']}")
    logger.info(f"Set PHONETIC_MATCH_THRESHOLD to {os.environ['PHONETIC_MATCH_THRESHOLD']}")

def run_pipeline():
    logger.info("Running address matching pipeline")
    try:
        exit_code = os.system("python -m src.pipeline.orchestrator")
        if exit_code != 0:
            logger.error(f"Pipeline execution failed with exit code {exit_code}")
            return False
        return True
    except Exception as e:
        logger.error(f"Error running pipeline: {str(e)}")
        return False

def verify_results():
    logger.info("Verifying matching results")
    
    session = SessionLocal()
    try:
        match_count = session.execute(
            text("SELECT COUNT(*) FROM address_matches")
        ).scalar()
        
        logger.info(f"Found {match_count} total address matches")
        
        matched_transactions = session.execute(
            text("SELECT COUNT(*) FROM transactions WHERE match_status = 'matched'")
        ).scalar()
        
        logger.info(f"Found {matched_transactions} matched transactions")
        
        match_types = session.execute(
            text("SELECT match_type, COUNT(*) FROM address_matches GROUP BY match_type")
        ).fetchall()
        
        match_type_counts = {t[0]: t[1] for t in match_types}
        logger.info(f"Matches by type: {', '.join([f'{k}: {v}' for k, v in match_type_counts.items()])}")
        
        check_for_near_matches(session)
        
        return match_count, matched_transactions, match_type_counts
        
    except Exception as e:
        logger.error(f"Error verifying results: {str(e)}")
        raise
    finally:
        session.close()

def check_for_near_matches(session):
    unmatched_transactions = session.execute(
        text("""
        SELECT id, normalized_address FROM transactions
        WHERE match_status IS NULL OR match_status != 'matched'
        """)
    ).fetchall()
    
    if not unmatched_transactions:
        logger.info("No unmatched transactions to check for near matches")
        return
    
    logger.info(f"Checking {len(unmatched_transactions)} unmatched transactions for near matches")
    
    canonical_addresses = session.execute(
        text("SELECT id, normalized_address FROM canonical_addresses")
    ).fetchall()
    
    for trans in unmatched_transactions:
        trans_id = trans[0]
        trans_addr = trans[1]
        
        if not trans_addr:
            continue
            
        best_match = None
        best_score = 0
        
        for canon in canonical_addresses:
            canon_id = canon[0]
            canon_addr = canon[1]
            
            if not canon_addr:
                continue
                
            score = similarity(trans_addr, canon_addr)
            
            if score > best_score:
                best_score = score
                best_match = canon_id
        
        if best_score > 0.5:
            logger.info(f"Near match found for {trans_id}: score {best_score} with {best_match}")

def similarity(a, b):
    if not a or not b:
        return 0
        
    a = a.lower()
    b = b.lower()
    
    a_words = set(a.split())
    b_words = set(b.split())
    common_words = len(a_words.intersection(b_words))
    
    if not common_words:
        return 0
        
    return common_words / len(a_words.union(b_words))

def main():
    parser = argparse.ArgumentParser(description='Test address matching pipeline')
    parser.add_argument('--skip-normalize', action='store_true', help='Skip address normalization')
    args = parser.parse_args()
    
    start_time = time.time()
    
    try:
        add_missing_column()
        
        add_canonical_addresses()
        
        if not args.skip_normalize:
            normalize_transaction_addresses()
        
        lower_matching_thresholds()
        
        success = run_pipeline()
        
        if success:
            verify_results()
        
    except Exception as e:
        logger.error(f"Error in test script: {str(e)}")
        sys.exit(1)
    
    end_time = time.time()
    logger.info(f"Test completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main() 