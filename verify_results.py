#!/usr/bin/env python3

import os
import sys
import csv
import glob
from sqlalchemy import text
import argparse
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.db.session import SessionLocal

def get_latest_results_file():
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    if not os.path.exists(results_dir):
        results_dir = "/app/results"
        
    csv_files = glob.glob(os.path.join(results_dir, "matching_results_*.csv"))
    if not csv_files:
        print(f"No result files found in {results_dir}")
        return None
        
    latest_file = max(csv_files, key=os.path.getmtime)
    return latest_file

def read_csv_results(file_path):
    results = []
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            results.append(row)
    return results

def check_for_near_matches(session):
    transactions = session.execute(text("""
        SELECT id, normalized_address 
        FROM transactions 
        WHERE normalized_address IS NOT NULL
        LIMIT 10
    """)).all()
    
    canonicals = session.execute(text("""
        SELECT id, normalized_address 
        FROM canonical_addresses 
        WHERE normalized_address IS NOT NULL
        LIMIT 100
    """)).all()
    
    if not transactions or not canonicals:
        print("No transactions or canonical addresses found for near-match check")
        return
    
    print("\nChecking for potential near-matches:")
    
    def similarity(a, b):
        if not a or not b:
            return 0
        a_set = set(a.lower().split())
        b_set = set(b.lower().split())
        intersection = len(a_set.intersection(b_set))
        union = len(a_set.union(b_set))
        return intersection / union if union > 0 else 0
    
    near_matches = []
    for t_id, t_addr in transactions:
        if not t_addr:
            continue
            
        for c_id, c_addr in canonicals:
            if not c_addr:
                continue
                
            sim = similarity(t_addr, c_addr)
            if sim > 0.5:
                near_matches.append((t_id, c_id, t_addr, c_addr, sim))
    
    near_matches.sort(key=lambda x: x[4], reverse=True)
    
    if near_matches:
        print(f"Found {len(near_matches)} potential near-matches:")
        for i, (t_id, c_id, t_addr, c_addr, sim) in enumerate(near_matches[:5]):
            print(f"\nPotential Match {i+1} (similarity: {sim:.2f}):")
            print(f"  Transaction ID: {t_id}")
            print(f"  Transaction address: {t_addr}")
            print(f"  Canonical ID: {c_id}")
            print(f"  Canonical address: {c_addr}")
    else:
        print("No potential near-matches found in the sample")
        
    if near_matches:
        print("\nSuggestion: Consider lowering the similarity threshold in the matching algorithms")
        print("Current thresholds can be found in the environment variables or matcher configurations")

def validate_database_matches(csv_results):
    session = SessionLocal()
    
    try:
        db_total = session.execute(text("SELECT COUNT(*) FROM transactions")).scalar()
        db_matched = session.execute(text("SELECT COUNT(*) FROM transactions WHERE match_status = 'matched'")).scalar()
        db_matches_count = session.execute(text("SELECT COUNT(*) FROM address_matches")).scalar()
        
        csv_matched = sum(1 for row in csv_results if row.get('match_status') == 'matched')
        
        print(f"\nValidation Results:")
        print(f"Total transactions in database: {db_total}")
        print(f"Matched transactions in database: {db_matched}")
        print(f"Address matches in database: {db_matches_count}")
        print(f"Matched transactions in CSV: {csv_matched}")
        
        if db_matched != csv_matched:
            print(f"WARNING: Mismatch between database matched count ({db_matched}) and CSV matched count ({csv_matched})")
        else:
            print(f"SUCCESS: Database and CSV matched counts are consistent")
            
        if db_matched != db_matches_count:
            print(f"WARNING: Mismatch between transactions marked as matched ({db_matched}) and actual address_matches ({db_matches_count})")
        else:
            print(f"SUCCESS: All matched transactions have corresponding address_matches entries")
        
        if db_matches_count > 0:
            match_types = session.execute(text("SELECT match_type, COUNT(*) FROM address_matches GROUP BY match_type")).all()
            print("\nMatch types distribution:")
            for match_type, count in match_types:
                print(f"  {match_type}: {count}")
        
        if db_matches_count > 0:
            print("\nSample matches verification:")
            sample_matches = session.execute(text("""
                SELECT t.id, t.normalized_address, c.normalized_address, am.match_type, t.match_score
                FROM transactions t
                JOIN address_matches am ON t.id = am.transaction_id
                JOIN canonical_addresses c ON am.canonical_address_id = c.id
                LIMIT 5
            """)).all()
            
            for t_id, t_addr, c_addr, match_type, score in sample_matches:
                print(f"Transaction: {t_id}")
                print(f"  Transaction address: {t_addr}")
                print(f"  Canonical address: {c_addr}")
                print(f"  Match type: {match_type}")
                print(f"  Match score: {score}")
                print("")
        
        if db_matches_count == 0:
            check_for_near_matches(session)
                
        return db_matched == csv_matched and db_matched == db_matches_count
                
    finally:
        session.close()

def main():
    parser = argparse.ArgumentParser(description='Verify address matching pipeline results')
    parser.add_argument('--file', help='Specific results file to verify (defaults to most recent)')
    args = parser.parse_args()
    
    results_file = args.file if args.file else get_latest_results_file()
    
    if not results_file:
        print("No results file found. Please run the pipeline first or specify a file.")
        sys.exit(1)
    
    print(f"Verifying results file: {results_file}")
    
    csv_results = read_csv_results(results_file)
    print(f"Found {len(csv_results)} records in CSV file")
    
    if csv_results:
        print("\nSample of results:")
        for i, row in enumerate(csv_results[:3]):
            print(f"Record {i+1}: Transaction ID: {row.get('transaction_id', 'N/A')}")
            print(f"  Match status: {row.get('match_status', 'N/A')}")
            if 'match_type' in row and row['match_type']:
                print(f"  Match type: {row.get('match_type', 'N/A')}")
                print(f"  Match score: {row.get('match_score', 'N/A')}")
                print(f"  Canonical ID: {row.get('canonical_id', 'N/A')}")
    
    is_valid = validate_database_matches(csv_results)
    
    if is_valid:
        print("\nVERIFICATION RESULT: PASSED")
        print("The database and CSV results are consistent.")
        sys.exit(0)
    else:
        print("\nVERIFICATION RESULT: FAILED")
        print("There are inconsistencies between the database and CSV results.")
        sys.exit(1)

if __name__ == "__main__":
    main() 