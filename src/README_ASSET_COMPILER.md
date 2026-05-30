# Comprehensive Tradeable Asset Compiler

This system compiles a complete list of tradeable assets from multiple sources for tracking and analysis.

## Overview

The asset compiler aggregates data from various sources to create a comprehensive master list of tradeable assets including:

- **Stocks**: US public companies from SEC EDGAR (10,000+ companies)
- **ETFs**: Major ETFs across different categories (broad market, sector, bond, commodity, crypto)
- **Indices**: Market indices (S&P 500, Dow Jones, NASDAQ, Russell 2000, VIX, etc.)
- **Commodities**: Futures contracts (metals, energy, agriculture)
- **Forex**: Major currency pairs
- **Cryptocurrencies**: Major crypto assets (Bitcoin, Ethereum, etc.)

## Available Scripts

### 1. `compile_existing_assets.py` (Recommended)
**Purpose**: Uses existing SEC data from the project and adds additional asset classes

**Advantages**:
- Uses existing SEC company_tickers.json file
- No external API calls required
- Fast and reliable
- Includes curated list of popular ETFs, indices, commodities, forex, and crypto

**Usage**:
```bash
python src/compile_existing_assets.py
```

**Output**:
- `assets/compiled/comprehensive_asset_list.csv` - CSV format
- `assets/compiled/comprehensive_asset_list.json` - JSON format
- `assets/compiled/asset_summary.txt` - Summary statistics

### 2. `asset_compiler.py` (Advanced)
**Purpose**: Fetches data from multiple external sources in real-time

**Features**:
- Downloads NASDAQ listings from GitHub
- Fetches S&P 500 stocks from Wikipedia/yfinance
- More comprehensive but requires internet access
- May be slower due to external API calls

**Usage**:
```bash
python src/asset_compiler.py
```

**Output**: Same as above

### 3. `test_asset_compiler.py` (Testing)
**Purpose**: Tests individual data sources before running full compilation

**Usage**:
```bash
python src/test_asset_compiler.py
```

## Data Sources

### Primary Sources

1. **SEC EDGAR** (`data/raw/sec/company_tickers.json`)
   - All US public companies
   - Includes ticker, CIK, and company name
   - ~10,000+ companies

2. **NASDAQ Listings** (GitHub)
   - All NASDAQ-traded securities
   - Updated regularly
   - ~3,000+ securities

3. **Manual Curation**
   - Popular ETFs (50+)
   - Market indices (15+)
   - Commodity futures (15+)
   - Forex pairs (10+)
   - Cryptocurrencies (8+)

## Asset Categories

### Stocks
- US public companies from SEC
- Multiple exchanges (NYSE, NASDAQ, AMEX)
- Includes large-cap, mid-cap, small-cap

### ETFs
- **Broad Market**: SPY, VOO, VTI, IVV, QQQ
- **International**: EFA, VEA, VWO, EEM
- **Sector**: XLK, XLF, XLV, XLE, XLI, XLU, XLP, XLY, XLRE, XLC, XLB
- **Bond**: TLT, IEF, LQD, HYG, AGG, BND, VCIT, VCSH
- **Commodity**: GLD, SLV, USO
- **Crypto**: IBIT, FBTC, ETHA

### Indices
- **US**: ^GSPC (S&P 500), ^DJI (Dow Jones), ^IXIC (NASDAQ), ^RUT (Russell 2000)
- **Volatility**: ^VIX
- **Bond Yields**: ^TNX (10-Year), ^FVX (5-Year), ^IRX (13-Week)
- **International**: ^N225 (Nikkei), ^FTSE (FTSE 100), ^GDAXI (DAX)

### Commodities (Futures)
- **Metals**: GC=F (Gold), SI=F (Silver), PL=F (Platinum), HG=F (Copper)
- **Energy**: CL=F (Crude Oil), NG=F (Natural Gas), RB=F (Gasoline), HO=F (Heating Oil)
- **Agriculture**: ZC=F (Corn), ZW=F (Wheat), ZS=F (Soybeans), CC=F (Cocoa), SB=F (Sugar), KC=F (Coffee)

### Forex Pairs
- **Major**: EURUSD=X, GBPUSD=X, USDJPY=X, USDCHF=X
- **Commodity**: AUDUSD=X, USDCAD=X, NZDUSD=X
- **Cross**: EURGBP=X, EURJPY=X, GBPJPY=X

### Cryptocurrencies
- BTC-USD (Bitcoin)
- ETH-USD (Ethereum)
- BNB-USD (Binance Coin)
- XRP-USD (Ripple)
- SOL-USD (Solana)
- ADA-USD (Cardano)
- DOGE-USD (Dogecoin)
- DOT-USD (Polkadot)

## Output Format

The compiled asset list includes the following fields:

- `ticker`: Asset symbol/ticker
- `name`: Full asset name
- `cik`: SEC CIK number (for stocks)
- `source`: Data source (SEC_EDGAR, NASDAQ, ETF, INDEX, etc.)
- `asset_type`: Type of asset (stock, etf, index, commodity, forex, crypto)
- `exchange`: Exchange where traded
- `category`: Additional categorization (sector, asset class, etc.)

## Usage Examples

### Load the compiled list in Python
```python
import pandas as pd

# Load CSV
assets = pd.read_csv('assets/compiled/comprehensive_asset_list.csv')

# Filter by asset type
stocks = assets[assets['asset_type'] == 'stock']
etfs = assets[assets['asset_type'] == 'etf']

# Get specific tickers
apple = assets[assets['ticker'] == 'AAPL']
spy = assets[assets['ticker'] == 'SPY']
```

### Use with yfinance
```python
import yfinance as yf
import pandas as pd

# Load asset list
assets = pd.read_csv('assets/compiled/comprehensive_asset_list.csv')

# Get data for specific assets
tickers = assets['ticker'].head(10).tolist()
data = yf.download(tickers, period='1mo')
```

### Filter by category
```python
import pandas as pd

assets = pd.read_csv('assets/compiled/comprehensive_asset_list.csv')

# Get all tech sector ETFs
tech_etfs = assets[(assets['asset_type'] == 'etf') & 
                   (assets['name'].str.contains('Technology', case=False))]

# Get all commodity futures
commodities = assets[assets['asset_type'] == 'commodity']
```

## Maintenance

### Updating the List

1. **For SEC data**: The SEC updates `company_tickers.json` regularly. Replace the file in:
   ```
   data/raw/sec/company_tickers.json
   ```

2. **For NASDAQ data**: The GitHub repository is updated regularly. Re-run the compiler to fetch latest data.

3. **For manual additions**: Edit the `add_additional_assets()` function in the script to add new ETFs, indices, etc.

### Recommended Update Frequency
- SEC data: Monthly
- NASDAQ data: Monthly
- Manual additions: As needed

## Troubleshooting

### Issue: SEC file not found
**Solution**: The SEC data file is located at `data/raw/sec/company_tickers.json`. The script uses this path by default.

### Issue: Network errors when downloading NASDAQ data
**Solution**: Use `compile_existing_assets.py` instead, which doesn't require external downloads.

### Issue: yfinance errors
**Solution**: Ensure yfinance is installed and updated: `pip install yfinance --upgrade`

## Integration with EDGAR Pipeline

This asset compiler is designed to work with your existing EDGAR streaming pipeline:

1. The SEC company tickers provide the foundation for EDGAR filing analysis
2. Additional asset classes enable comprehensive market analysis
3. The compiled list can be used to:
   - Track price movements across asset classes
   - Correlate SEC filings with market data
   - Build multi-asset trading strategies
   - Perform cross-asset analysis

## Next Steps

1. Run the compiler to generate the initial asset list
2. Review the output files
3. Customize the asset list by adding/removing assets as needed
4. Integrate with your existing EDGAR pipeline
5. Set up regular updates to keep the list current

## Support

For issues or questions about the asset compiler, refer to the script documentation or check the project's main documentation.
