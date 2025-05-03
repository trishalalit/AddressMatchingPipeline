# Scalable Address Matching Pipeline

## What We Set Out to Do

Hey there! This project started with a clear challenge: how do we accurately match millions of transaction addresses against a database of canonical addresses? Imagine you have customer transactions with all sorts of address formats - some abbreviated, some with typos, some missing apartment numbers - and you need to link them to your official address records.

Our goal was to build a system that could:
- Process a massive dataset (200+ million records) efficiently
- Handle the messy reality of real-world addresses
- Achieve a high match rate (95%+) without sacrificing accuracy
- Provide an API for real-time address matching

## What We've Accomplished

So far, we've built a complete end-to-end solution that:
- Ingests address data from Excel/CSV files into a PostgreSQL database
- Normalizes raw address text into standardized components
- Implements a smart "waterfall" matching approach that tries multiple techniques:
  - First attempts exact matching (fastest and most confident)
  - Falls back to fuzzy matching for close matches
  - Uses phonetic matching for "sounds like" cases
  - Can even call external APIs for the toughest cases
- Provides a simple REST API for real-time matching
- Automatically validates and fixes data schemas
- Handles the whole process in manageable batches for performance
- Features a modern, interactive web frontend for address matching and system monitoring

The system currently achieves around 95% match rates on our test datasets, with impressive performance thanks to careful database optimization and a thoughtful blocking strategy that dramatically reduces the number of comparisons needed.

## TLDR: Overview
This system ingests address data from different sources, normalizes and parses raw text into standardized components, and performs a series of matching techniques with increasing flexibility to achieve the highest possible match rate while maintaining accuracy.

### Features
- **Data Ingestion**: Batch loading of Excel/CSV files into PostgreSQL
- **Address Parsing**: Normalizes raw address text into components using usaddress and custom logic
- **Multi-tier Matching Strategy**:
  - Exact matching on normalized fields
  - Fuzzy matching with trigram similarity
  - Phonetic matching for sound-alike addresses
  - External API fallback for difficult cases
- **Scalability**: Designed to handle 200+ million records through:
  - Efficient database indexing
  - Batch processing
  - PostgreSQL optimization
- **Performance Monitoring**: Tracks runtime, memory usage, and match rates
- **REST API**: FastAPI endpoint for real-time address matching
- **Robust Error Handling**: Automatic schema validation and column addition

## Technical Stack
- **Database**: PostgreSQL with pg_trgm and fuzzystrmatch extensions
- **API**: FastAPI
- **Frontend**: Vanilla JavaScript with Bootstrap, Chart.js
- **Container**: Docker and Docker Compose
- **Language**: Python 3.10
- **Key Libraries**:
  - SQLAlchemy: Database ORM
  - pandas: Data processing
  - usaddress: Address parsing
  - rapidfuzz: Fuzzy string matching
  - jellyfish: Phonetic algorithms

## Repository Structure
```
address-matching-pipeline/
├── src/                     # Source code
│   ├── db/                  # Database models and connection
│   ├── ingestion/           # Data loading
│   ├── processing/          # Address parsing and normalization
│   ├── matching/            # Matching algorithms
│   ├── pipeline/            # Orchestration
│   └── api/                 # FastAPI service
├── frontend/                # Web frontend
│   ├── public/              # Static assets
│   ├── src/                 # Frontend source code
│   │   ├── components/      # UI components
│   │   ├── services/        # API services
│   │   └── styles/          # CSS stylesheets
│   └── nginx.conf           # Nginx configuration
├── data/                    # Data directory
├── scripts/                 # Utility scripts
├── tests/                   # Test suite
├── docker-compose.yml       # Docker services
├── Dockerfile               # Application container
├── test_matching.py         # Test script for address matching
└── README.md                # Documentation
```
## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/address-matching-pipeline.git
   cd address-matching-pipeline
   ```
2. Place your data files in the `data/` directory:
   - `data/11211 Addresses.xlsx`: Canonical addresses
   - `data/transactions_2_11211.xlsx`: Transaction records
3. Start the services:
   ```bash
   docker-compose up -d
   ```
### Accessing the Web Interface

The frontend is available at `http://localhost:3000`:

- **Dashboard** shows key metrics and statistics
- **Match Address** provides a form for testing address matching
- **Statistics** displays detailed performance metrics

### Running the Pipeline
The pipeline can be run end-to-end or in stages:

```bash
docker-compose run app python -m src.pipeline.orchestrator
docker-compose run app python -m src.pipeline.orchestrator --skip-load
docker-compose run app python -m src.pipeline.orchestrator --skip-parse
docker-compose run app python -m src.pipeline.orchestrator --skip-match

```

### Running Tests

The test script provides a convenient way to test the address matching pipeline:

```bash
# Run the full test suite
docker-compose run app python test_matching.py

# Skip address normalization if already done
docker-compose run app python test_matching.py --skip-normalize
```

The test script performs the following:
1. Checks and adds the required `match_timestamp` column if missing
2. Adds sample canonical addresses for testing
3. Normalizes transaction addresses to ensure consistent matching
4. Sets appropriate matching thresholds for testing
5. Runs the complete matching pipeline
6. Verifies the results and reports match statistics

### Using the API

The API is available at `http://localhost:8000`:

- `GET /`: API information
- `GET /health`: System health check
- `POST /match_address`: Match a single address
- `GET /statistics`: Pipeline statistics

Example API request:

```bash
curl -X POST http://localhost:8000/match_address \
  -H "Content-Type: application/json" \
  -d '{
    "address_line_1": "123 Main St",
    "address_line_2": "Apt 4B",
    "city": "Brooklyn",
    "state": "NY",
    "zip_code": 11211
  }'
```

## Design Decisions and Trade-offs

### Database Design

- **Indexes**: Strategically created for both exact and fuzzy matching
- **Partitioning**: For handling 200M+ records efficiently
- **Extensions**: Using pg_trgm for trigram matching and fuzzystrmatch for phonetic algorithms
- **Schema Validation**: Automatic column addition for missing fields (e.g., `match_timestamp`)

### Matching Strategy

1. **Blocking Strategy**: Narrow the search space by:
   - Initial filtering by ZIP code
   - Using first characters of street name
   - This reduces comparison complexity from O(n²) to nearly O(n)

2. **Waterfall Approach**:
   - Start with exact matching (fastest, highest confidence)
   - Progress to fuzzy matching with thresholds
   - Try phonetic matching for sound-alike addresses
   - Fall back to external API for difficult cases

3. **Confidence Scoring**:
   - 1.0 for exact matches
   - Scaled scores for fuzzy matches based on similarity
   - Weighted scoring across multiple fields

4. **Address Normalization**:
   - Automatically normalizes address formats for consistent matching
   - Handles various address formats and variations
   - Robust parsing using usaddress library with custom fallbacks

### Performance Considerations

- **Batch Processing**: Operates on data in manageable chunks
- **Indexing Strategy**: Optimized for the specific query patterns
- **Connection Pooling**: Efficient database connection management
- **Parallel Processing**: Where possible for performance

## Performance Results

On a typical development machine (4-core, 16GB RAM):

- **Data Loading**: ~X records/second
- **Address Parsing**: ~X records/second
- **Matching Pipeline**: ~X records/second
- **Total Runtime**: ~X minutes for the sample dataset
- **Match Rate**: ~95% overall (combining exact, fuzzy, and phonetic matches)

Projected performance for 200M records:
- **Estimated Runtime**: ~X hours
- **Peak Memory Usage**: ~X GB
- **Disk Usage**: ~X GB

## Recent Improvements

- **Schema Validation**: Automatically checks and adds missing columns (e.g., `match_timestamp`)
- **Transaction Normalization**: Improved address normalization to ensure consistent matching
- **Enhanced Near Match Detection**: Improved detection of near matches using Jaccard similarity
- **Robust Error Handling**: Better error handling throughout the pipeline
- **Improved Testing**: Comprehensive test script to validate the entire pipeline

## Future Improvements

- Implement distributed processing for faster matching of very large datasets
- Add machine learning-based address matching for difficult cases
- Enhance the API with batch processing capabilities
- Add more visualization dashboards for match quality analysis
- Implement address standardization using USPS data

## License

This project is licensed under the MIT License - see the LICENSE file for details. 