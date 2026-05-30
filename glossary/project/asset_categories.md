# Project Asset Categories

Asset categories and classifications used in the EDGAR streaming pipeline.

## Asset Types

### Stocks
- Common stock
- Preferred stock
- ADRs (American Depositary Receipts)
- **Source**: SEC EDGAR company_tickers.json
- **Count**: 10,000+ US public companies

### ETFs (Exchange-Traded Funds)
- **Broad Market**: SPY, VOO, VTI, IVV, QQQ
- **International**: EFA, VEA, VWO, EEM
- **Sector**: XLK, XLF, XLV, XLE, XLI, XLU, XLP, XLY, XLRE, XLC, XLB
- **Bond**: TLT, IEF, LQD, HYG, AGG, BND, VCIT, VCSH
- **Commodity**: GLD, SLV, USO
- **Crypto**: IBIT, FBTC, ETHA

### Indices
- **US Market**: ^GSPC (S&P 500), ^DJI (Dow Jones), ^IXIC (NASDAQ), ^RUT (Russell 2000)
- **Volatility**: ^VIX (CBOE Volatility Index)
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

## Exchanges

### US Stock Exchanges
- NYSE (New York Stock Exchange)
- NASDAQ (NASDAQ Stock Market)
- AMEX (American Stock Exchange)

### Futures Exchanges
- COMEX (Commodity Exchange)
- NYMEX (New York Mercantile Exchange)
- CBOT (Chicago Board of Trade)
- ICE (Intercontinental Exchange)

### Other
- INDEX (Market indices)
- FOREX (Foreign exchange)
- CRYPTO (Cryptocurrency exchanges)

## Data Sources

### SEC EDGAR
- **File**: data/raw/sec/company_tickers.json
- **Coverage**: All US public companies
- **Fields**: ticker, CIK, company name
- **Update Frequency**: Monthly

### Manual Curation
- **Coverage**: Popular ETFs, indices, commodities, forex, crypto
- **Fields**: ticker, name, asset type, category
- **Update Frequency**: As needed

### External APIs (Future)
- NASDAQ listings (GitHub)
- Wikipedia (S&P 500 constituents)
- yfinance (real-time data)

## Asset Attributes

### Standard Fields
- `ticker`: Asset symbol
- `name`: Full asset name
- `cik`: SEC CIK number (stocks only)
- `source`: Data source
- `asset_type`: Type of asset
- `exchange`: Exchange where traded
- `category`: Additional categorization

### Classification Schemes
- **Sector**: GICS sectors
- **Industry**: GICS industries
- **Market Cap**: Large-cap, mid-cap, small-cap
- **Style**: Growth, value, blend
- **Region**: US, international, emerging markets

## Usage in Pipeline

### Data Ingestion
- Primary source for SEC filing monitoring
- Ticker list for price data collection
- Asset universe for analysis

### Analysis
- Factor model construction
- Portfolio optimization
- Risk management
- Performance attribution

### Integration
- EDGAR filing correlation
- Price data alignment
- Cross-asset analysis
- Multi-asset strategies
