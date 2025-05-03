CREATE EXTENSION IF NOT EXISTS pg_trgm; 
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch; 

CREATE TABLE canonical_addresses (
    id SERIAL PRIMARY KEY,
    hhid TEXT UNIQUE NOT NULL,
    fname TEXT NOT NULL,
    mname TEXT,
    lname TEXT NOT NULL,
    suffix TEXT,
    address TEXT NOT NULL,
    house TEXT NOT NULL,
    predir TEXT,
    street TEXT NOT NULL,
    strtype TEXT,
    postdir TEXT,
    apttype TEXT,
    aptnbr TEXT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip INTEGER NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    homeownercd TEXT,
    normalized_address TEXT
);
CREATE TABLE transactions (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    price BIGINT NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms INTEGER NOT NULL,
    square_feet INTEGER NOT NULL,
    address_line_1 TEXT NOT NULL,
    address_line_2 TEXT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip_code INTEGER NOT NULL,
    property_type TEXT,
    year_built DOUBLE PRECISION,
    presented_by TEXT,
    brokered_by TEXT,
    presented_by_mobile DOUBLE PRECISION,
    mls TEXT,
    listing_office_id TEXT,
    listing_agent_id TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    open_house TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    email TEXT,
    list_date TIMESTAMP,
    pending_date TIMESTAMP,
    presented_by_first_name TEXT,
    presented_by_last_name TEXT,
    presented_by_middle_name TEXT,
    presented_by_suffix DOUBLE PRECISION,
    geog TEXT,
    parsed_house TEXT,
    parsed_predir TEXT,
    parsed_street TEXT,
    parsed_strtype TEXT,
    parsed_postdir TEXT,
    parsed_apttype TEXT,
    parsed_aptnbr TEXT,
    normalized_address TEXT,
    match_status TEXT,
    match_score DOUBLE PRECISION
);
CREATE TABLE address_matches (
    id SERIAL PRIMARY KEY,
    transaction_id TEXT NOT NULL REFERENCES transactions(id),
    canonical_address_id INTEGER NOT NULL REFERENCES canonical_addresses(id),
    match_type TEXT NOT NULL, 
    confidence_score DOUBLE PRECISION NOT NULL,
    match_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(transaction_id)
);
CREATE TABLE match_failures (
    id SERIAL PRIMARY KEY,
    transaction_id TEXT NOT NULL REFERENCES transactions(id),
    failure_reason TEXT NOT NULL,
    failure_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(transaction_id)
);
CREATE INDEX idx_canonical_zip ON canonical_addresses(zip);
CREATE INDEX idx_canonical_street ON canonical_addresses(street);
CREATE INDEX idx_canonical_norm_addr ON canonical_addresses(normalized_address);
CREATE INDEX idx_transaction_zip ON transactions(zip_code);
CREATE INDEX idx_transaction_norm_addr ON transactions(normalized_address);
CREATE INDEX idx_transaction_match_status ON transactions(match_status);
CREATE INDEX idx_canonical_street_trgm ON canonical_addresses USING GIN(street gin_trgm_ops);
CREATE INDEX idx_canonical_address_trgm ON canonical_addresses USING GIN(address gin_trgm_ops);
CREATE INDEX idx_transaction_addr_line1_trgm ON transactions USING GIN(address_line_1 gin_trgm_ops);
CREATE INDEX idx_transaction_norm_addr_trgm ON transactions USING GIN(normalized_address gin_trgm_ops); 