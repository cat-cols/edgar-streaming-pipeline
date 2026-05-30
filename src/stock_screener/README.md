# Stock Screener - Financial Engineering System

A comprehensive stock screening system using factor models and quantitative methods to identify potentially undervalued stocks.

## Overview

This system implements a financial engineering approach to stock screening, combining:

- **Value Factors**: P/E, P/B, EV/EBITDA ratios
- **Quality Factors**: ROE, ROA, profit margins, debt levels
- **Momentum Factors**: Price momentum, technical indicators
- **Low Volatility Factors**: Beta, historical volatility

## Project Structure

```
src/stock_screener/
├── __init__.py
├── screen_stocks.py          # Main screening script
├── README.md
├── data/
│   ├── __init__.py
│   └── fetcher.py            # Data fetching from yfinance
├── factors/
│   ├── __init__.py
│   └── calculator.py         # Factor calculation
├── scoring/
│   ├── __init__.py
│   └── ranker.py             # Stock ranking and filtering
├── portfolio/
│   ├── __init__.py
│   └── constructor.py        # Portfolio construction
├── backtesting/
│   ├── __init__.py
│   └── engine.py             # Backtesting engine
└── utils/
    ├── __init__.py
    ├── config.py             # Configuration parameters
    └── helpers.py            # Helper functions
```

## Usage

### Basic Screening

```bash
python src/stock_screener/screen_stocks.py
```

This will:
1. Load the asset universe (10,000+ stocks)
2. Fetch financial data (price, fundamentals, technical indicators)
3. Calculate factor scores
4. Apply quality and liquidity filters
5. Rank stocks by composite score
6. Generate screening report
7. Construct portfolio
8. Save results to `data/screening_results/`

### Custom Configuration

Edit `utils/config.py` to customize:

- Factor weights
- Screening filters
- Portfolio parameters
- Backtesting settings

### Programmatic Usage

```python
from data.fetcher import DataFetcher
from factors.calculator import FactorCalculator
from scoring.ranker import StockRanker

# Initialize components
fetcher = DataFetcher()
factor_calc = FactorCalculator()
ranker = StockRanker()

# Load and screen stocks
stocks_df = fetcher.load_asset_universe()
tickers = stocks_df['ticker'].head(100).tolist()

# Fetch data
price_data = fetcher.fetch_stock_data(tickers)
fundamentals = fetcher.fetch_fundamental_data(tickers)
technical_indicators = fetcher.calculate_technical_indicators(price_data)

# Calculate factors
value_factors = factor_calc.calculate_value_factors(fundamentals)
quality_factors = factor_calc.calculate_quality_factors(fundamentals)
momentum_factors = factor_calc.calculate_momentum_factors(technical_indicators)

# Combine and rank
all_factors = factor_calc.combine_all_factors(
    value_factors, quality_factors, momentum_factors, lowvol_factors
)
ranked_stocks = ranker.rank_by_composite_score(all_factors, top_n=20)
```

## Factor Models

### Value Factors
- **P/E Ratio**: Price to earnings (lower = better value)
- **P/B Ratio**: Price to book (lower = better value)
- **EV/EBITDA**: Enterprise value to EBITDA (lower = better value)
- **Dividend Yield**: Higher yield = attractive

### Quality Factors
- **ROE**: Return on equity (higher = better quality)
- **ROA**: Return on assets (higher = better quality)
- **Profit Margins**: Higher margins = better quality
- **Debt-to-Equity**: Lower debt = better quality
- **Current Ratio**: Higher = better liquidity

### Momentum Factors
- **3-Month Momentum**: Recent price performance
- **6-Month Momentum**: Medium-term price performance
- **12-Month Momentum**: Long-term price performance
- **RSI**: Relative strength index
- **Moving Averages**: Trend indicators

### Low Volatility Factors
- **Beta**: Market sensitivity (lower = less volatile)
- **Historical Volatility**: Price variance (lower = less volatile)

## Portfolio Construction

The system supports multiple portfolio construction methods:

- **Equal Weight**: Simple equal allocation
- **Value Weighted**: Weighted by market capitalization
- **Risk Parity**: Equal risk contribution
- **Kelly Criterion**: Optimal growth allocation
- **Mean-Variance Optimization**: Efficient frontier

## Backtesting

The backtesting engine supports:

- **Walk-Forward Analysis**: Realistic out-of-sample testing
- **Performance Metrics**: Sharpe ratio, max drawdown, win rate
- **Benchmark Comparison**: Information ratio, tracking error
- **Monte Carlo Simulation**: Future return distribution

## Output Files

Screening results are saved to `data/screening_results/`:

- `stock_screening_report.csv`: Top stocks with all metrics
- `factor_scores.csv`: All factor scores for screened stocks
- `portfolio_weights.csv`: Portfolio allocation

## Dependencies

- `yfinance`: Financial data
- `pandas`: Data manipulation
- `numpy`: Numerical computing
- `scikit-learn`: Machine learning (optional)

## Configuration

Key parameters in `utils/config.py`:

```python
FACTOR_WEIGHTS = {
    'value': 0.3,
    'quality': 0.3,
    'momentum': 0.25,
    'lowvol': 0.15,
}

SCREENING_FILTERS = {
    'min_market_cap': 1e9,  # $1B minimum
    'min_roe': 0.05,  # 5% minimum ROE
    'max_debt_to_equity': 3.0,
}
```

## Integration with EDGAR Pipeline

This screener integrates with your EDGAR streaming pipeline:

1. Uses the compiled asset universe from SEC data
2. Can be enhanced with SEC filing analysis
3. Supports factor models based on fundamental data
4. Enables systematic stock selection for further analysis

## Next Steps

1. Run the screener to generate initial results
2. Adjust factor weights based on your strategy
3. Implement custom screening criteria
4. Add backtesting for validation
5. Integrate with real-time trading signals
