"""
Historical Price Fetching Script
Fetches historical price data for all tradeable stocks
"""

import yfinance as yf
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HistoricalPriceFetcher:
    """Fetch historical price data for tradeable stocks"""
    
    def __init__(self, output_dir: str = "data/raw/prices"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load asset universe
        self.asset_universe_file = Path("data/reference/comprehensive_asset_list.csv")
        self.asset_universe = self.load_asset_universe()
        
        # Track processed stocks
        self.processed_file = self.output_dir / "processed_stocks.json"
        self.processed_stocks = self.load_processed_stocks()
    
    def load_asset_universe(self) -> pd.DataFrame:
        """Load the compiled asset universe"""
        if self.asset_universe_file.exists():
            logger.info(f"Loading asset universe from {self.asset_universe_file}")
            return pd.read_csv(self.asset_universe_file)
        else:
            logger.warning("Asset universe file not found")
            return pd.DataFrame()
    
    def load_processed_stocks(self) -> set:
        """Load set of already processed stocks"""
        if self.processed_file.exists():
            with open(self.processed_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def save_processed_stocks(self):
        """Save set of processed stocks"""
        with open(self.processed_file, 'w') as f:
            json.dump(list(self.processed_stocks), f)
    
    def fetch_stock_prices(self, ticker: str, period: str = "5y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """Fetch historical prices for a single stock"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                logger.warning(f"No data returned for {ticker}")
                return None
            
            # Add ticker column
            hist['ticker'] = ticker
            
            logger.info(f"Fetched {len(hist)} price records for {ticker}")
            return hist
            
        except Exception as e:
            logger.error(f"Error fetching prices for {ticker}: {e}")
            return None
    
    def save_stock_prices(self, ticker: str, price_data: pd.DataFrame):
        """Save historical prices for a stock"""
        # Create ticker directory
        ticker_dir = self.output_dir / ticker
        ticker_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as CSV
        csv_file = ticker_dir / f"{ticker}_prices.csv"
        price_data.to_csv(csv_file, index=True)
        
        # Save as Parquet (more efficient)
        try:
            parquet_file = ticker_dir / f"{ticker}_prices.parquet"
            price_data.to_parquet(parquet_file, index=True)
        except ImportError:
            logger.warning("PyArrow not installed, skipping Parquet format")
        
        # Save metadata
        metadata = {
            'ticker': ticker,
            'start_date': str(price_data.index.min()),
            'end_date': str(price_data.index.max()),
            'total_records': len(price_data),
            'columns': list(price_data.columns),
            'last_updated': datetime.now().isoformat()
        }
        
        metadata_file = ticker_dir / f"{ticker}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved price data for {ticker} to {ticker_dir}")
    
    def fetch_and_save_stock(self, ticker: str, period: str = "5y", interval: str = "1d") -> bool:
        """Fetch and save prices for a single stock"""
        if ticker in self.processed_stocks:
            logger.info(f"Skipping {ticker} (already processed)")
            return True
        
        price_data = self.fetch_stock_prices(ticker, period, interval)
        
        if price_data is not None:
            self.save_stock_prices(ticker, price_data)
            self.processed_stocks.add(ticker)
            return True
        
        return False
    
    def fetch_all_stocks(self, asset_types: Optional[List[str]] = None, 
                         period: str = "5y", interval: str = "1d",
                         sample_size: Optional[int] = None,
                         delay: float = 0.1) -> Dict:
        """Fetch historical prices for all stocks"""
        logger.info("Starting historical price fetching...")
        
        # Filter asset universe
        if asset_types:
            stocks_df = self.asset_universe[self.asset_universe['asset_type'].isin(asset_types)]
        else:
            stocks_df = self.asset_universe[self.asset_universe['asset_type'] == 'stock']
        
        # Sample if specified
        if sample_size:
            stocks_df = stocks_df.head(sample_size)
            logger.info(f"Processing sample of {sample_size} stocks")
        
        tickers = stocks_df['ticker'].tolist()
        logger.info(f"Fetching prices for {len(tickers)} stocks")
        
        results = {
            'total': len(tickers),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        for i, ticker in enumerate(tickers):
            if i % 100 == 0:
                logger.info(f"Progress: {i}/{len(tickers)} stocks processed")
                self.save_processed_stocks()  # Save progress
            
            try:
                success = self.fetch_and_save_stock(ticker, period, interval)
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(ticker)
            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
                results['failed'] += 1
                results['errors'].append(ticker)
            
            # Rate limiting
            time.sleep(delay)
        
        # Save final progress
        self.save_processed_stocks()
        
        # Create summary report
        self.create_summary_report(results)
        
        logger.info(f"Price fetching completed: {results['successful']} successful, {results['failed']} failed")
        return results
    
    def create_summary_report(self, results: Dict):
        """Create summary report of price fetching"""
        report = []
        report.append("=" * 80)
        report.append("HISTORICAL PRICE FETCHING SUMMARY")
        report.append("=" * 80)
        report.append(f"Total Stocks Processed: {results['total']}")
        report.append(f"Successful: {results['successful']}")
        report.append(f"Failed: {results['failed']}")
        report.append(f"Skipped: {results['skipped']}")
        report.append(f"Success Rate: {results['successful']/results['total']*100:.1f}%")
        report.append("")
        
        if results['errors']:
            report.append("Failed Stocks:")
            for ticker in results['errors'][:20]:  # Show first 20
                report.append(f"  - {ticker}")
            if len(results['errors']) > 20:
                report.append(f"  ... and {len(results['errors']) - 20} more")
        
        report.append("")
        report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        
        report_text = "\n".join(report)
        
        # Save report
        report_file = self.output_dir / "fetching_summary.txt"
        with open(report_file, 'w') as f:
            f.write(report_text)
        
        logger.info(f"Saved summary report to {report_file}")
    
    def fetch_etf_prices(self, period: str = "5y", interval: str = "1d", delay: float = 0.1):
        """Fetch historical prices for ETFs"""
        logger.info("Fetching ETF prices...")
        return self.fetch_all_stocks(asset_types=['etf'], period=period, interval=interval, delay=delay)
    
    def fetch_commodity_prices(self, period: str = "5y", interval: str = "1d", delay: float = 0.1):
        """Fetch historical prices for commodities"""
        logger.info("Fetching commodity prices...")
        return self.fetch_all_stocks(asset_types=['commodity'], period=period, interval=interval, delay=delay)
    
    def fetch_forex_prices(self, period: str = "5y", interval: str = "1d", delay: float = 0.1):
        """Fetch historical prices for forex pairs"""
        logger.info("Fetching forex prices...")
        return self.fetch_all_stocks(asset_types=['forex'], period=period, interval=interval, delay=delay)
    
    def fetch_crypto_prices(self, period: str = "5y", interval: str = "1d", delay: float = 0.1):
        """Fetch historical prices for cryptocurrencies"""
        logger.info("Fetching crypto prices...")
        return self.fetch_all_stocks(asset_types=['crypto'], period=period, interval=interval, delay=delay)
    
    def create_master_price_index(self):
        """Create master index of all price data"""
        logger.info("Creating master price index...")
        
        price_data = []
        
        for ticker_dir in self.output_dir.iterdir():
            if ticker_dir.is_dir() and ticker_dir.name not in ['processed_stocks.json', 'fetching_summary.txt']:
                metadata_file = ticker_dir / f"{ticker_dir.name}_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    price_data.append(metadata)
        
        if price_data:
            index_df = pd.DataFrame(price_data)
            index_file = self.output_dir / "price_data_index.csv"
            index_df.to_csv(index_file, index=False)
            logger.info(f"Saved master index to {index_file}")
            logger.info(f"Total stocks with price data: {len(index_df)}")
        else:
            logger.warning("No price data found to index")


def main():
    """Main execution function"""
    fetcher = HistoricalPriceFetcher()
    
    # Fetch stock prices (sample for testing)
    logger.info("Starting historical price fetching...")
    
    # Start with a small sample for testing
    results = fetcher.fetch_all_stocks(
        period="2y",  # 2 years of data
        interval="1d",  # daily data
        # sample_size=20,  # Start with 20 stocks for testing
        delay=0.2  # Rate limiting
    )
    
    # Create master index
    fetcher.create_master_price_index()
    
    logger.info("Historical price fetching completed")


if __name__ == "__main__":
    main()
