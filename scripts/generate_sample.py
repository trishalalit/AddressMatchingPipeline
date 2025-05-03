#!/usr/bin/env python3
"""
Generate sample data for testing the address matching pipeline.
Creates both canonical and transaction sample datasets.
"""

import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Define constants
OUTPUT_DIR = "data"
CANONICAL_FILE = "sample_canonical_addresses.xlsx"
TRANSACTION_FILE = "sample_transactions.xlsx"
NUM_CANONICAL = 1000
NUM_TRANSACTIONS = 500

# Ensure the data directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Sample data elements
street_names = [
    "Main", "Oak", "Pine", "Maple", "Cedar", "Elm", "Washington", "Park",
    "Lake", "Hill", "River", "Forest", "Garden", "Sunset", "Highland",
    "Valley", "Green", "Spring", "Summer", "Willow", "Meadow", "Ocean",
    "Broadway", "Church", "State", "Mill", "Central", "Franklin", "Lincoln",
    "Jackson", "Jefferson", "Adams", "Monroe", "Madison", "Wilson"
]

street_types = ["St", "Ave", "Blvd", "Dr", "Ln", "Rd", "Cir", "Ct", "Pl", "Ter", "Way"]

directions = ["N", "S", "E", "W", "NE", "NW", "SE", "SW"]

unit_types = ["Apt", "Unit", "Ste", "Floor", "#"]

first_names = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Margaret", "Anthony", "Betty", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Dorothy", "Paul", "Kimberly", "Andrew", "Emily", "Kenneth", "Donna"
]

last_names = [
    "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson",
    "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
    "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee",
    "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright", "Lopez",
    "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter"
]

cities = ["Brooklyn", "New York", "Jersey City", "Hoboken", "Newark"]

def generate_canonical_addresses(num_records=NUM_CANONICAL):
    """Generate a dataset of canonical addresses."""
    
    addresses = []
    
    # Set random seed for reproducibility
    random.seed(42)
    
    for i in range(num_records):
        # Generate a random address
        house_num = str(random.randint(1, 9999))
        street = random.choice(street_names)
        street_type = random.choice(street_types)
        
        # Sometimes add a pre-direction
        pre_dir = random.choice(directions) if random.random() < 0.3 else ""
        
        # Sometimes add a post-direction
        post_dir = random.choice(directions) if random.random() < 0.2 else ""
        
        # Sometimes add a unit
        has_unit = random.random() < 0.4
        unit_type = random.choice(unit_types) if has_unit else ""
        unit_num = str(random.randint(1, 500)) if has_unit else ""
        
        # Build address string
        address_parts = [house_num]
        if pre_dir:
            address_parts.append(pre_dir)
        address_parts.append(street)
        address_parts.append(street_type)
        if post_dir:
            address_parts.append(post_dir)
        address = " ".join(address_parts)
        
        # Add unit if present
        full_address = address
        if has_unit:
            full_address = f"{address} {unit_type} {unit_num}"
        
        # Generate person info
        first_name = random.choice(first_names)
        middle_initial = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") if random.random() < 0.5 else ""
        last_name = random.choice(last_names)
        suffix = random.choice(["Jr", "Sr", "II", "III", "IV"]) if random.random() < 0.1 else ""
        
        # Location info
        city = "Brooklyn"  # For the 11211 sample
        state = "NY"
        zip_code = 11211
        
        # Add some randomness to lat/long for visual distinction
        lat = 40.7128 + (random.random() - 0.5) * 0.1
        lng = -73.9644 + (random.random() - 0.5) * 0.1
        
        # Generate a unique ID
        hhid = f"HH{i+10000}"
        
        # Homeowner code
        homeowner_cd = random.choice(["O", "R", ""])
        
        addresses.append({
            "hhid": hhid,
            "fname": first_name,
            "mname": middle_initial,
            "lname": last_name,
            "suffix": suffix,
            "address": full_address,
            "house": house_num,
            "predir": pre_dir,
            "street": street,
            "strtype": street_type,
            "postdir": post_dir,
            "apttype": unit_type,
            "aptnbr": unit_num,
            "city": city,
            "state": state,
            "zip": zip_code,
            "latitude": lat,
            "longitude": lng,
            "homeownercd": homeowner_cd
        })
    
    return pd.DataFrame(addresses)

def generate_transactions(canonical_df, num_records=NUM_TRANSACTIONS):
    """Generate a dataset of transaction addresses, some matching canonical addresses."""
    
    transactions = []
    
    # Set random seed for reproducibility
    random.seed(43)  # Different seed than canonical
    
    # For some transactions, use the canonical address (with variations)
    for i in range(num_records):
        transaction = {}
        
        # Generate a unique ID
        transaction["id"] = f"T{i+20000}"
        transaction["status"] = random.choice(["ACTIVE", "PENDING", "CLOSED", "SOLD"])
        
        # Price info
        transaction["price"] = random.randint(500000, 3000000)
        transaction["bedrooms"] = random.randint(1, 5)
        transaction["bathrooms"] = random.randint(1, 4)
        transaction["square_feet"] = random.randint(600, 3000)
        
        # Randomly decide if this should match a canonical address
        should_match = random.random() < 0.7  # 70% chance of matching
        
        if should_match and not canonical_df.empty:
            # Pick a random canonical address
            canonical_idx = random.randint(0, len(canonical_df) - 1)
            canonical = canonical_df.iloc[canonical_idx]
            
            # Determine how much to vary the address
            variation_level = random.random()
            
            if variation_level < 0.4:  # 40% chance of exact match
                address_line_1 = canonical["address"]
                if canonical["apttype"] and canonical["aptnbr"]:
                    # Move unit info to line 2 in some cases
                    if random.random() < 0.5:
                        address_line_1 = " ".join([canonical["house"], 
                                                canonical.get("predir", ""), 
                                                canonical["street"], 
                                                canonical.get("strtype", ""),
                                                canonical.get("postdir", "")]).strip()
                        address_line_2 = f"{canonical['apttype']} {canonical['aptnbr']}".strip()
                    else:
                        address_line_2 = ""
                else:
                    address_line_2 = ""
            else:  # Introduce variations
                house = canonical["house"]
                street = canonical["street"]
                street_type = canonical["strtype"]
                
                # Sometimes introduce typos or format changes
                if random.random() < 0.3:
                    # Potential variations for street
                    if street == "Main":
                        street = random.choice(["Main", "Mian", "Man"])
                    else:
                        # Random typo - letter swap, deletion, or insertion
                        variation_type = random.choice(["swap", "delete", "insert"])
                        if variation_type == "swap" and len(street) > 1:
                            i = random.randint(0, len(street) - 2)
                            street = street[:i] + street[i+1] + street[i] + street[i+2:]
                        elif variation_type == "delete" and len(street) > 3:
                            i = random.randint(0, len(street) - 1)
                            street = street[:i] + street[i+1:]
                        elif variation_type == "insert":
                            i = random.randint(0, len(street))
                            letter = random.choice("abcdefghijklmnopqrstuvwxyz")
                            street = street[:i] + letter + street[i:]
                
                # Street type abbreviation variation
                if random.random() < 0.4:
                    if street_type == "St":
                        street_type = random.choice(["St", "St.", "Street"])
                    elif street_type == "Ave":
                        street_type = random.choice(["Ave", "Ave.", "Avenue"])
                    elif street_type == "Blvd":
                        street_type = random.choice(["Blvd", "Blvd.", "Boulevard"])
                    elif street_type == "Dr":
                        street_type = random.choice(["Dr", "Dr.", "Drive"])
                    # Add more variations as needed
                
                # Build address with variations
                address_parts = [house]
                if canonical.get("predir"):
                    address_parts.append(canonical["predir"])
                address_parts.append(street)
                address_parts.append(street_type)
                if canonical.get("postdir"):
                    address_parts.append(canonical["postdir"])
                
                address_line_1 = " ".join(address_parts).strip()
                
                # Unit/apt variations
                if canonical.get("apttype") and canonical.get("aptnbr"):
                    if random.random() < 0.5:
                        # Format unit in line 1
                        apt = f"{canonical['apttype']} {canonical['aptnbr']}".strip()
                        address_line_1 = f"{address_line_1} {apt}"
                        address_line_2 = ""
                    else:
                        # Format unit in line 2
                        apt_type = canonical['apttype']
                        # Sometimes vary the unit type
                        if random.random() < 0.3:
                            if apt_type == "Apt":
                                apt_type = random.choice(["Apt", "Apartment", "Unit", "#"])
                            elif apt_type == "Unit":
                                apt_type = random.choice(["Unit", "Apt", "#"])
                        
                        address_line_2 = f"{apt_type} {canonical['aptnbr']}".strip()
                else:
                    address_line_2 = ""
            
            # Use matching city/state/zip
            city = canonical["city"]
            state = canonical["state"]
            zip_code = canonical["zip"]
            
        else:
            # Generate a completely new address
            house_num = str(random.randint(1, 9999))
            street = random.choice(street_names)
            street_type = random.choice(street_types)
            
            # Sometimes add a pre-direction
            pre_dir = random.choice(directions) if random.random() < 0.3 else ""
            
            # Build address
            address_parts = [house_num]
            if pre_dir:
                address_parts.append(pre_dir)
            address_parts.append(street)
            address_parts.append(street_type)
            
            address_line_1 = " ".join(address_parts)
            
            # Sometimes add a unit
            if random.random() < 0.4:
                unit_type = random.choice(unit_types)
                unit_num = str(random.randint(1, 500))
                if random.random() < 0.5:
                    # Add to line 1
                    address_line_1 = f"{address_line_1} {unit_type} {unit_num}"
                    address_line_2 = ""
                else:
                    # Add to line 2
                    address_line_2 = f"{unit_type} {unit_num}"
            else:
                address_line_2 = ""
            
            # Random location
            city = random.choice(cities)
            state = "NY"
            zip_code = 11211 if city == "Brooklyn" else random.choice([10001, 10002, 10003, 10004, 07030])
        
        # Add address to transaction
        transaction["address_line_1"] = address_line_1
        transaction["address_line_2"] = address_line_2
        transaction["city"] = city
        transaction["state"] = state
        transaction["zip_code"] = zip_code
        
        # Add other transaction fields
        transaction["property_type"] = random.choice(["Condo", "Co-op", "Single Family", "Multi-Family", "Townhouse"])
        transaction["year_built"] = random.randint(1900, 2023)
        
        # Agent info
        agent_first = random.choice(first_names)
        agent_last = random.choice(last_names)
        transaction["presented_by"] = f"{agent_first} {agent_last}"
        transaction["brokered_by"] = random.choice(["ABC Realty", "XYZ Properties", "123 Homes", "City Living", "Metro Realty"])
        transaction["presented_by_mobile"] = random.randint(2120000000, 9179999999)
        transaction["mls"] = f"MLS{random.randint(100000, 999999)}"
        transaction["listing_office_id"] = f"LO{random.randint(100, 999)}"
        transaction["listing_agent_id"] = f"LA{random.randint(1000, 9999)}"
        
        # Dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=random.randint(30, 180))
        transaction["created_at"] = start_date
        transaction["updated_at"] = start_date + timedelta(days=random.randint(1, 30))
        transaction["list_date"] = start_date
        transaction["pending_date"] = start_date + timedelta(days=random.randint(14, 60)) if random.random() < 0.5 else None
        
        # Open house
        transaction["open_house"] = f"{random.choice(['Sunday', 'Saturday'])} {random.randint(1, 5)}pm-{random.randint(6, 8)}pm" if random.random() < 0.3 else ""
        
        # Add some randomness to lat/long
        lat = 40.7128 + (random.random() - 0.5) * 0.1
        lng = -73.9644 + (random.random() - 0.5) * 0.1
        transaction["latitude"] = lat
        transaction["longitude"] = lng
        
        # Additional fields
        transaction["email"] = f"{agent_first.lower()}.{agent_last.lower()}@example.com"
        transaction["presented_by_first_name"] = agent_first
        transaction["presented_by_last_name"] = agent_last
        transaction["presented_by_middle_name"] = ""
        transaction["presented_by_suffix"] = ""
        transaction["geog"] = ""
        
        transactions.append(transaction)
    
    return pd.DataFrame(transactions)

def main():
    """Generate sample datasets and save to files."""
    
    print(f"Generating {NUM_CANONICAL} canonical addresses...")
    canonical_df = generate_canonical_addresses(NUM_CANONICAL)
    
    print(f"Generating {NUM_TRANSACTIONS} transactions...")
    transactions_df = generate_transactions(canonical_df, NUM_TRANSACTIONS)
    
    # Save to Excel files
    canonical_path = os.path.join(OUTPUT_DIR, CANONICAL_FILE)
    transactions_path = os.path.join(OUTPUT_DIR, TRANSACTION_FILE)
    
    print(f"Writing canonical addresses to {canonical_path}...")
    canonical_df.to_excel(canonical_path, index=False)
    
    print(f"Writing transactions to {transactions_path}...")
    transactions_df.to_excel(transactions_path, index=False)
    
    print("Sample data generation complete.")
    print(f"Generated {len(canonical_df)} canonical addresses and {len(transactions_df)} transactions.")

if __name__ == "__main__":
    main() 