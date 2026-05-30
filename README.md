# EDGAR Streaming Pipeline & Financial Engineering Platform

A comprehensive financial data engineering platform combining SEC EDGAR data processing with quantitative stock screening and interactive dashboards.

## Overview

This platform integrates SEC EDGAR data ingestion with advanced financial engineering tools for systematic stock analysis and screening. It provides a complete workflow from data collection to investment decision support.

### Key Components

- **Asset Compiler**: Comprehensive tradeable asset universe (10,000+ stocks, ETFs, commodities, forex, crypto)
- **Stock Screener**: Multi-factor quantitative screening system (value, quality, momentum, low volatility)
- **Interactive Dashboard**: Streamlit-based dashboard for exploring screened stocks
- **Financial Glossary**: Comprehensive reference for financial terminology and concepts
- **EDGAR Integration**: SEC filing data processing and analysis

## Features

### Asset Management
- Compile comprehensive list of tradeable assets from multiple sources
- Support for stocks, ETFs, indices, commodities, forex, and cryptocurrencies
- Automatic categorization and metadata management
- Integration with SEC EDGAR company database

### Quantitative Screening
- Multi-factor model combining value, quality, momentum, and low volatility factors
- Automated financial data fetching from Yahoo Finance
- Quality filters (ROE, debt levels, liquidity requirements)
- Portfolio construction with multiple methods (equal weight, risk parity, Kelly criterion)
- Walk-forward backtesting engine

### Interactive Dashboard
- Real-time factor weight adjustment
- Interactive filtering and sorting
- Visual analytics with charts and graphs
- Individual stock detail analysis
- Export functionality for further analysis

### Knowledge Base
- Financial formulas and calculations
- Key financial ratios and metrics
- Factor models and quantitative finance concepts
- SEC filing types and purposes
- Project-specific asset categories

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd edgar-streaming-pipeline
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
python -c "import yfinance; import pandas; import streamlit; print('Installation successful')"
```

## Quick Start

### 1. Compile Asset Universe

Generate a comprehensive list of tradeable assets:

```bash
python src/compile_existing_assets.py
```

This creates:
- `assets/compiled/comprehensive_asset_list.csv`
- `assets/compiled/comprehensive_asset_list.json`
- `assets/compiled/asset_summary.txt`

### 2. Screen Stocks

Run the quantitative stock screener:

```bash
python src/stock_screener/screen_stocks.py
```

This generates screening results in `data/screening_results/`

### 3. Launch Dashboard

Start the interactive dashboard:

```bash
streamlit run src/dashboard/app.py
```

The dashboard will open at `http://localhost:8501`

## Project Structure

```
edgar-streaming-pipeline/
├── assets/                      # Asset data and compiled lists
│   ├── compiled/               # Generated asset lists
│   └── 1.ingestion/            # EDGAR data sources
├── data/                       # Data storage
│   ├── company_tickers.json    # SEC company database
│   ├── cache/                  # Cached data
│   └── screening_results/      # Screening outputs
├── glossary/                   # Financial knowledge base
│   ├── financial/              # Financial formulas, ratios, metrics
│   ├── technical/              # Data pipeline terminology
│   ├── quantitative/           # Factor models and quant concepts
│   ├── reference/              # SEC filing types, reference materials
│   └── project/                # Project-specific definitions
├── src/                        # Source code
│   ├── compile_existing_assets.py  # Asset compiler
│   ├── stock_screener/         # Stock screening system
│   │   ├── data/              # Data fetching
│   │   ├── factors/           # Factor calculation
│   │   ├── scoring/           # Ranking and filtering
│   │   ├── portfolio/         # Portfolio construction
│   │   ├── backtesting/       # Backtesting engine
│   │   └── utils/             # Configuration and helpers
│   └── dashboard/             # Streamlit dashboard
│       ├── app.py             # Dashboard application
│       └── requirements.txt    # Dashboard dependencies
├── notes/                      # Notes and research
├── tests/                      # Test files
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Usage

### Asset Compilation

The asset compiler aggregates data from multiple sources:

```python
from src.compile_existing_assets import main

# Run asset compilation
main()
```

**Output**: Comprehensive asset list with 10,000+ tradeable instruments

### Stock Screening

The stock screener implements a multi-factor approach:

```python
from src.stock_screener.screen_stocks import main

# Run screening
report, portfolio = main()
```

**Factor Model**:
- Value (30%): P/E, P/B, EV/EBITDA ratios
- Quality (30%): ROE, ROA, profit margins, debt levels
- Momentum (25%): Price momentum, technical indicators
- Low Volatility (15%): Beta, historical volatility

### Dashboard Usage

The dashboard provides interactive exploration:

1. **Adjust Factor Weights**: Use sidebar sliders to customize factor importance
2. **Apply Filters**: Set minimum ROE, market cap, debt constraints
3. **View Rankings**: Explore top-ranked stocks by composite score
4. **Analyze Stocks**: Select individual stocks for detailed analysis
5. **Export Results**: Download screening results as CSV

## Configuration

### Factor Weights

Edit `src/stock_screener/utils/config.py`:

```python
FACTOR_WEIGHTS = {
    'value': 0.3,
    'quality': 0.3,
    'momentum': 0.25,
    'lowvol': 0.15,
}
```

### Screening Filters

```python
SCREENING_FILTERS = {
    'min_market_cap': 1e9,      # $1B minimum
    'min_roe': 0.05,            # 5% minimum ROE
    'max_debt_to_equity': 3.0,  # Maximum 3x debt-to-equity
    'min_current_ratio': 1.0,   # Minimum 1.0 current ratio
}
```

### Portfolio Parameters

```python
PORTFOLIO_CONFIG = {
    'default_capital': 100000,
    'max_position_size': 0.1,   # Maximum 10% per position
    'max_stocks': 30,           # Maximum stocks in portfolio
}
```

## Data Sources

### Primary Sources
- **SEC EDGAR**: Company tickers and filing data (10,000+ companies)
- **Yahoo Finance**: Price data, fundamentals, technical indicators via yfinance
- **NASDAQ**: Stock listings (via GitHub)
- **Manual Curation**: ETFs, indices, commodities, forex, crypto

### Data Updates
- SEC data: Monthly updates recommended
- Price data: Real-time via yfinance
- Fundamentals: Quarterly updates

## Methodology

### Factor Model

The screening system uses a multi-factor model based on established financial research:

**Value Factors**
- Identify undervalued stocks using traditional valuation metrics
- Lower P/E, P/B, EV/EBITDA ratios indicate better value
- Dividend yield provides income component

**Quality Factors**
- Assess financial health and business quality
- High ROE/ROA indicates efficient capital use
- Strong profit margins and manageable debt levels

**Momentum Factors**
- Capture price trends and market sentiment
- Multiple timeframes (3M, 6M, 12M) for robustness
- Technical indicators confirm trends

**Low Volatility Factors**
- Reduce portfolio risk through lower volatility stocks
- Beta measures market sensitivity
- Historical volatility indicates price stability

### Portfolio Construction

Multiple construction methods supported:
- **Equal Weight**: Simple, diversified allocation
- **Value Weighted**: Market cap-based allocation
- **Risk Parity**: Equal risk contribution
- **Kelly Criterion**: Optimal growth allocation

### Backtesting

Walk-forward backtesting validates strategies:
- Realistic out-of-sample testing
- Performance metrics (Sharpe ratio, max drawdown, win rate)
- Benchmark comparison (information ratio, tracking error)

## Glossary

The glossary provides comprehensive financial knowledge:

**Financial** (`glossary/financial/`)
- Formulas: Basic and advanced financial calculations
- Ratios: Key financial ratios for analysis
- Metrics: Performance and risk metrics

**Technical** (`glossary/technical/`)
- Data pipeline terminology and concepts
- ETL/ELT processes
- Data quality and monitoring

**Quantitative** (`glossary/quantitative/`)
- Factor models (CAPM, Fama-French, Carhart)
- Risk metrics and portfolio theory
- Statistical arbitrage concepts

**Reference** (`glossary/reference/`)
- SEC filing types and purposes
- Classification schemes
- Standard codes and identifiers

**Project** (`glossary/project/`)
- Asset categories and classifications
- Project-specific terminology
- Usage in the pipeline

## Integration with EDGAR Pipeline

This platform is designed to integrate with SEC EDGAR data:

1. **Asset Universe**: Uses SEC company_tickers.json as foundation
2. **Filing Analysis**: Can incorporate SEC filing analysis into factors
3. **Event-Driven**: Potential for real-time filing-based signals
4. **Compliance**: Maintains SEC data standards and formats

## Performance Considerations

- **Asset Compilation**: ~10,000+ assets, processes in seconds
- **Stock Screening**: Sample size configurable, full universe may take longer
- **Dashboard**: Data cached for 1 hour, initial load 10-30 seconds
- **Memory Usage**: Depends on data size, typically < 2GB for full universe

## Troubleshooting

### No Screening Data Found
Run the stock screener first:
```bash
python src/stock_screener/screen_stocks.py
```

### Dashboard Won't Load
Ensure dependencies are installed:
```bash
pip install streamlit plotly
```

### Data Fetching Errors
Check internet connection and yfinance status:
```python
import yfinance as yf
test = yf.download("AAPL", period="1d")
```

### Import Errors
Verify Python path and installation:
```bash
python -c "import sys; print(sys.path)"
```

## Contributing

Contributions are welcome! Areas for contribution:

- Additional factor models
- New data sources
- Enhanced visualizations
- Performance optimizations
- Documentation improvements
- Bug fixes

## License

[Specify your license here]

## Disclaimer

This platform is for educational and research purposes only. Not financial advice. Past performance does not guarantee future results. Always conduct your own research and consult with financial advisors before making investment decisions.

## Contact

For questions, issues, or suggestions:
- Open an issue on GitHub
- Contact: [your contact information]

## Acknowledgments

- SEC EDGAR for providing public company data
- Yahoo Finance for market data via yfinance
- Streamlit for the dashboard framework
- Open source quantitative finance community

## Roadmap

### Planned Features
- [ ] Real-time SEC filing integration
- [ ] Machine learning factor models
- [ ] Sector and industry analysis
- [ ] Advanced backtesting with transaction costs
- [ ] Portfolio optimization with constraints
- [ ] Alert system for new opportunities
- [ ] Mobile-responsive dashboard
- [ ] API endpoints for programmatic access
- [ ] Multi-currency support
- [ ] International market expansion

### Version History
- **v1.0.0**: Initial release with asset compiler, stock screener, and dashboard
