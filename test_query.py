from src.db.connection import get_db_session
from sqlalchemy import text
import time
temp_id = f'temp_{int(time.time() * 1000)}'
normalized_address = '30 BAYARD ST UNIT 1A'
with get_db_session() as session:
    # Insert test transaction
