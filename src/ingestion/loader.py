import os
import pandas as pd
from sqlalchemy import text
import logging
from ..db.connection import get_db_session, engine
from tqdm import tqdm
logger = logging.getLogger(__name__)
def load_canonical_addresses(file_path):
    logger.info(f"Loading canonical addresses from {file_path}")
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Read {len(df)} records from {file_path}")
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return 0
    batch_size = int(os.getenv("BATCH_SIZE", "1000"))
    total_loaded = 0
    df['normalized_address'] = df.apply(
        lambda row: f"{row['house']} {row.get('predir', '')} {row['street']} {row.get('strtype', '')} {row.get('apttype', '')} {row.get('aptnbr', '')}".lower().strip().replace('  ', ' '),
        axis=1
    )
    for i in tqdm(range(0, len(df), batch_size), desc="Loading canonical addresses"):
        batch = df.iloc[i:i+batch_size]
        try:
            batch.to_sql('canonical_addresses', engine, if_exists='append', index=False, 
                         method='multi', chunksize=batch_size)
            total_loaded += len(batch)
            logger.info(f"Loaded batch of {len(batch)} records, total {total_loaded}")
        except Exception as e:
            logger.error(f"Error loading batch: {e}")
    logger.info(f"Completed loading {total_loaded} canonical addresses")
    return total_loaded

def load_transactions(file_path):
    logger.info(f"Loading transactions from {file_path}")
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Read {len(df)} records from {file_path}")
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return 0
    batch_size = int(os.getenv("BATCH_SIZE", "1000"))
    total_loaded = 0
    df = df.fillna({
        'address_line_2': '',
        'property_type': '',
        'year_built': 0,
        'presented_by': '',
        'brokered_by': '',
        'presented_by_mobile': 0,
        'mls': '',
        'listing_office_id': '',
        'listing_agent_id': '',
        'open_house': '',
        'latitude': 0,
        'longitude': 0,
        'email': '',
        'presented_by_first_name': '',
        'presented_by_last_name': '',
        'presented_by_middle_name': '',
        'presented_by_suffix': 0,
        'geog': ''
    })
    for i in tqdm(range(0, len(df), batch_size), desc="Loading transactions"):
        batch = df.iloc[i:i+batch_size]
        try:
            batch.to_sql('transactions', engine, if_exists='append', index=False, 
                         method='multi', chunksize=batch_size)
            total_loaded += len(batch)
            logger.info(f"Loaded batch of {len(batch)} records, total {total_loaded}")
        except Exception as e:
            logger.error(f"Error loading batch: {e}")
    
    logger.info(f"Completed loading {total_loaded} transactions")
    return total_loaded 