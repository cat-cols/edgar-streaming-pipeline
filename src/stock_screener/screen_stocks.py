"""
Main stock screening script
Demonstrates how to use the stock screener modules to identify potentially undervalued stocks
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from data.fetcher import DataFetcher
from factors.calculator import FactorCalculator
from scoring.ranker import StockRanker
from portfolio.constructor import PortfolioConstructor
from backtesting.engine import BacktestEngine
from utils.config import DATA_CONFIG, FACTOR_WEIGHTS, SCREENING_FILTERS, PORTFOLIO_CONFIG
from utils.helpers import save_to_csv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main screening workflow"""
    
    logger.info("=" * 60)
    logger.info("STOCK SCREENING - FINANCIAL ENGINEERING APPROACH")
    logger.info("=" * 60)
    
    # Initialize components
    fetcher = DataFetcher()
    factor_calc = FactorCalculator()
    ranker = StockRanker()
    portfolio_constructor = PortfolioConstructor()
    backtest_engine = BacktestEngine()
    
    # Step 1: Load asset universe
    logger.info("\n[Step 1] Loading asset universe...")
    stocks_df = fetcher.load_asset_universe()
    
    # Sample subset for demonstration (remove this for full universe)
    sample_size = min(100, len(stocks_df))  # Limit to 100 for demo
    tickers = stocks_df['ticker'].head(sample_size).tolist()
    logger.info(f"Screening {len(tickers)} stocks (sample)")
    
    # Step 2: Fetch data
    logger.info("\n[Step 2] Fetching financial data...")
    price_data = fetcher.fetch_stock_data(tickers, period="2y", interval="1d")
    fundamentals = fetcher.fetch_fundamental_data(tickers)
    technical_indicators = fetcher.calculate_technical_indicators(price_data)
    
    # Step 3: Calculate factors
    logger.info("\n[Step 3] Calculating factors...")
    value_factors = factor_calc.calculate_value_factors(fundamentals)
    quality_factors = factor_calc.calculate_quality_factors(fundamentals)
    momentum_factors = factor_calc.calculate_momentum_factors(technical_indicators)
    lowvol_factors = factor_calc.calculate_low_volatility_factors(fundamentals, technical_indicators)
    
    # Step 4: Combine factors
    logger.info("\n[Step 4] Combining factors...")
    all_factors = factor_calc.combine_all_factors(
        value_factors, quality_factors, momentum_factors, lowvol_factors, FACTOR_WEIGHTS
    )
    
    # Step 5: Apply filters
    logger.info("\n[Step 5] Applying quality and liquidity filters...")
    filtered_factors = ranker.apply_quality_filters(all_factors, fundamentals)
    filtered_factors = ranker.apply_liquidity_filters(filtered_factors, fundamentals)
    
    # Step 6: Rank stocks
    logger.info("\n[Step 6] Ranking stocks...")
    ranked_stocks = ranker.rank_by_composite_score(filtered_factors, top_n=20)
    
    # Step 7: Generate report
    logger.info("\n[Step 7] Generating screening report...")
    report = ranker.generate_screening_report(ranked_stocks, fundamentals, technical_indicators)
    
    # Save report
    output_dir = Path("data/screening_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "stock_screening_report.csv"
    ranker.save_report(report, str(report_path))
    
    # Display top stocks
    logger.info("\n" + "=" * 60)
    logger.info("TOP 10 STOCKS BY COMPOSITE SCORE")
    logger.info("=" * 60)
    print(report.head(10).to_string(index=False))
    
    # Step 8: Construct portfolio
    logger.info("\n[Step 8] Constructing portfolio...")
    top_tickers = ranked_stocks.head(10).index.tolist()
    
    # Equal-weight portfolio
    equal_weight_portfolio = portfolio_constructor.equal_weight_portfolio(
        top_tickers, PORTFOLIO_CONFIG['default_capital']
    )
    
    logger.info(f"Equal-weight portfolio: {len(equal_weight_portfolio)} stocks")
    for ticker, weight in equal_weight_portfolio.items():
        logger.info(f"  {ticker}: {weight:.2%}")
    
    # Step 9: Calculate portfolio metrics (if we have returns data)
    logger.info("\n[Step 9] Calculating portfolio metrics...")
    returns = fetcher.calculate_returns(price_data)
    
    if returns:
        portfolio_metrics = portfolio_constructor.calculate_portfolio_metrics(
            equal_weight_portfolio, returns
        )
        logger.info(f"Portfolio metrics: {portfolio_metrics}")
    
    # Step 10: Save results
    logger.info("\n[Step 10] Saving results...")
    
    # Save factor scores
    factors_path = output_dir / "factor_scores.csv"
    all_factors.to_csv(factors_path)
    logger.info(f"Factor scores saved to {factors_path}")
    
    # Save portfolio weights
    portfolio_df = pd.DataFrame([
        {'ticker': ticker, 'weight': weight} 
        for ticker, weight in equal_weight_portfolio.items()
    ])
    portfolio_path = output_dir / "portfolio_weights.csv"
    portfolio_df.to_csv(portfolio_path, index=False)
    logger.info(f"Portfolio weights saved to {portfolio_path}")
    
    logger.info("\n" + "=" * 60)
    logger.info("SCREENING COMPLETED SUCCESSFULLY")
    logger.info("=" * 60)
    logger.info(f"Results saved to {output_dir}")
    logger.info(f"Top stock: {report.iloc[0]['ticker']} (Score: {report.iloc[0]['composite_score']:.3f})")
    
    return report, equal_weight_portfolio


def run_backtest():
    """Run a simple backtest on the screening strategy"""
    logger.info("\n" + "=" * 60)
    logger.info("RUNNING BACKTEST")
    logger.info("=" * 60)
    
    fetcher = DataFetcher()
    backtest_engine = BacktestEngine()
    
    # Load asset universe
    stocks_df = fetcher.load_asset_universe()
    tickers = stocks_df['ticker'].head(50).tolist()  # Small sample for backtest
    
    # Fetch historical data
    price_data = fetcher.fetch_stock_data(tickers, period="3y", interval="1d")
    
    # Define a simple screening function
    def simple_screening_function(lookback_data):
        """Simple screening: pick top 10 by recent momentum"""
        momentums = {}
        for ticker, df in lookback_data.items():
            if 'Close' in df.columns and len(df) > 20:
                momentum = df['Close'].iloc[-1] / df['Close'].iloc[-20] - 1
                momentums[ticker] = momentum
        
        # Sort by momentum and pick top 10
        sorted_stocks = sorted(momentums.items(), key=lambda x: x[1], reverse=True)
        return [ticker for ticker, _ in sorted_stocks[:10]]
    
    # Run walk-forward backtest
    results = backtest_engine.walk_forward_backtest(
        price_data, 
        simple_screening_function,
        rebalance_freq='M',
        lookback_period=126
    )
    
    # Display results
    logger.info("\nBacktest Results:")
    logger.info(f"Total periods: {len(results['returns'])}")
    logger.info(f"Metrics: {results['metrics']}")
    
    if not results['returns'].empty:
        logger.info(f"\nCumulative Returns:")
        print((1 + results['returns']['return']).cumprod().tail(10))
    
    return results


if __name__ == "__main__":
    # Run main screening
    report, portfolio = main()
    
    # Optionally run backtest (commented out by default)
    # backtest_results = run_backtest()
