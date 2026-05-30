# Data Directory Structure

This directory contains all financial data used in the EDGAR Streaming Pipeline & Financial Engineering Platform.

## Directory Organization

```
data/
├── raw/                    # Original downloaded data (read-only)
│   ├── sec/               # SEC filings and company data
│   ├── prices/            # Raw price data from APIs
│   └── fundamentals/      # Raw fundamental data
├── processed/             # Cleaned and processed data
│   ├── prices/            # Processed price data
│   ├── fundamentals/      # Processed fundamentals
│   └── factors/           # Calculated factors
├── cache/                 # Temporary cache (ignored by git)
├── screening_results/     # Screening outputs (ignored by git)
└── reference/             # Static reference data
```

## Directory Descriptions

### `raw/` - Original Downloaded Data
Contains original data from external sources. **Never modify files in this directory.**

- **`sec/`**: SEC EDGAR data including company_tickers.json, filing data, and company facts
- **`prices/`**: Raw price data from Yahoo Finance, APIs, or other sources
- **`fundamentals/`**: Raw fundamental data from financial APIs or SEC filings

### `processed/` - Processed Data
Contains cleaned, transformed, and analyzed data ready for use in applications.

- **`prices/`**: Cleaned and processed price data (adjusted for splits, dividends, etc.)
- **`fundamentals/`**: Processed fundamental data with standardized formats
- **`factors/`**: Calculated factor scores and metrics for stock screening

### `cache/` - Temporary Cache
Temporary data storage for caching API responses and intermediate results. **Ignored by git.**

### `screening_results/` - Screening Outputs
Results from stock screening processes including reports, rankings, and portfolios. **Ignored by git.**

### `reference/` - Static Reference Data
Static lookup tables and reference data that should be tracked in git.

- `company_tickers.json` - SEC company ticker database (moved to raw/sec/)
- `comprehensive_asset_list.csv` - Complete asset universe
- `comprehensive_asset_list.json` - Complete asset universe (JSON format)
- `asset_summary.txt` - Summary statistics of asset universe

## Data Flow

1. **Download**: Raw data → `data/raw/`
2. **Process**: Raw data → Cleaned/processed → `data/processed/`
3. **Cache**: Temporary data → `data/cache/`
4. **Output**: Screening results → `data/screening_results/`
5. **Reference**: Static data → `data/reference/`

## File Naming Conventions

- **Raw data**: `{source}_{date}_{identifier}.{ext}` (e.g., `sec_20240529_company_tickers.json`)
- **Processed data**: `{type}_{date}_{identifier}.{ext}` (e.g., `prices_20240529_AAPL.csv`)
- **Factors**: `{factor_type}_{date}_{identifier}.{ext}` (e.g., `factors_20240529_composite.csv`)
- **Cache**: `{function}_{hash}.{ext}` (e.g., `fetch_prices_abc123.json`)

## Best Practices

1. **Never modify raw data**: Always copy raw data to processed/ before modifying
2. **Document transformations**: Keep track of how raw data becomes processed data
3. **Version reference data**: Track changes to reference data in git
4. **Clean cache regularly**: Remove old cache files to save space
5. **Use consistent naming**: Follow naming conventions for easy file identification
6. **Separate concerns**: Keep raw, processed, and reference data distinct

## Storage Considerations

- **Raw data**: Can be large, consider compression for long-term storage
- **Processed data**: Optimize for query performance
- **Cache**: Set up automatic cleanup for old files
- **Reference data**: Keep in git for reproducibility

## Backup Strategy

- **Raw data**: Back up regularly (source of truth)
- **Processed data**: Can be regenerated from raw data
- **Reference data**: Backed up in git
- **Cache**: No backup needed (temporary)

## Integration with Scripts

Update script file paths to use new structure:

```python
# Old path
DATA_PATH = "data/company_tickers.json"

# New path
RAW_SEC_PATH = "data/raw/sec/company_tickers.json"
```

## Git Tracking

- **Tracked**: `reference/` directory
- **Ignored**: `raw/`, `processed/`, `cache/`, `screening_results/`

See `.gitignore` for complete ignore patterns.
