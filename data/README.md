# Data Directory

This directory should contain the address data files that will be processed by the pipeline.

## Required Data Files

1. **Canonical Address File** - `11211 Addresses.xlsx`
   - Contains the authoritative addresses to match against
   - Expected columns: `hhid`, `fname`, `lname`, `address`, `house`, `street`, etc.

2. **Transaction File** - `transactions_2_11211.xlsx`
   - Contains the transaction addresses that need to be matched
   - Expected columns: `id`, `status`, `price`, `address_line_1`, `address_line_2`, etc.

## File Format

- The system accepts Excel files (.xlsx or .xls)
- CSV files can also be used with minor adjustments to the loader.py file

## Data Privacy

- This directory is excluded from git version control through .gitignore
- Never commit actual address data to the repository
- For development, use anonymized sample data

## Sample Data Generation

If you need to generate sample data for testing, you can use the script:

```bash
python -m scripts.generate_sample
```

This will create test data files with randomized addresses while maintaining realistic patterns. 