"""
Comprehensive Tradeable Asset Compiler
Compiles a complete list of tradeable assets from multiple sources including:
- Stocks (NYSE, NASDAQ, AMEX, international)
- ETFs
- Mutual Funds
- Bonds
- Commodities
- Cryptocurrencies
- Futures
- Options
- Indices
"""

import json
import pandas as pd
import requests
import yfinance as yf
from typing import Dict, List, Set
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetCompiler:
    """Compiles comprehensive list of tradeable assets from multiple sources"""
    
    def __init__(self, output_dir: str = "assets/compiled"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.assets = {}

    def load_sec_company_tickers(self, filepath: str = "data/raw/sec/company_tickers.json") -> List[Dict]:
        """Load SEC company tickers (US public companies)"""
        logger.info("Loading SEC company tickers...")

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            companies = []
            for key, value in data.items():
                companies.append({
                    'ticker': value['ticker'],
                    'cik': value['cik_str'],
                    'name': value['title'],
                    'source': 'SEC_EDGAR',
                    'asset_type': 'stock',
                    'exchange': 'US'
                })

            logger.info(f"Loaded {len(companies)} companies from SEC")
            return companies

        except Exception as e:
            logger.error(f"Error loading SEC tickers: {e}")
            return []

    def download_nasdaq_listings(self) -> List[Dict]:
        """Download NASDAQ listed stocks from GitHub"""
        logger.info("Downloading NASDAQ listings...")

        try:
            url = "https://raw.githubusercontent.com/datasets/nasdaq-listings/main/data/nasdaq-listed.csv"
            response = requests.get(url)

            from io import StringIO
            df = pd.read_csv(StringIO(response.text))

            # Filter out footer row if present
            df = df[~df['Symbol'].str.contains('File Creation Time', na=False)]

            assets = []
            for _, row in df.iterrows():
                assets.append({
                    'ticker': row['Symbol'],
                    'name': row['Name'],
                    'source': 'NASDAQ',
                    'asset_type': 'stock',
                    'exchange': 'NASDAQ'
                })

            logger.info(f"Loaded {len(assets)} assets from NASDAQ")
            return assets

        except Exception as e:
            logger.error(f"Error downloading NASDAQ listings: {e}")
            return []

    def get_sp500_stocks(self) -> List[Dict]:
        """Get S&P 500 stock list using yfinance"""
        logger.info("Getting S&P 500 stocks...")

        try:
            # S&P 500 ETF holdings
            spy = yf.Ticker("SPY")
            try:
                info = spy.info
                holdings = info.get('holdings', [])
            except:
                # Alternative: use Wikipedia
                url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
                tables = pd.read_html(url)
                sp500_table = tables[0]

                assets = []
                for _, row in sp500_table.iterrows():
                    ticker = row['Ticker symbol']
                    assets.append({
                        'ticker': ticker,
                        'name': row['Security'],
                        'sector': row['GICS Sector'],
                        'source': 'S&P_500',
                        'asset_type': 'stock',
                        'exchange': 'US'
                    })

                logger.info(f"Loaded {len(assets)} S&P 500 stocks")
                return assets
                
        except Exception as e:
            logger.error(f"Error getting S&P 500 stocks: {e}")
            return []
    
    def get_popular_etfs(self) -> List[Dict]:
        """Get popular ETFs"""
        logger.info("Getting popular ETFs...")
        
        popular_etfs = [
            # Broad Market
            {'ticker': 'SPY', 'name': 'SPDR S&P 500 ETF Trust', 'asset_type': 'etf', 'category': 'Broad Market'},
            {'ticker': 'VOO', 'name': 'Vanguard S&P 500 ETF', 'asset_type': 'etf', 'category': 'Broad Market'},
            {'ticker': 'IVV', 'name': 'iShares Core S&P 500 ETF', 'asset_type': 'etf', 'category': 'Broad Market'},
            {'ticker': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'asset_type': 'etf', 'category': 'Broad Market'},
            
            # International
            {'ticker': 'EFA', 'name': 'iShares MSCI EAFE ETF', 'asset_type': 'etf', 'category': 'International'},
            {'ticker': 'VEA', 'name': 'Vanguard FTSE Developed Markets ETF', 'asset_type': 'etf', 'category': 'International'},
            {'ticker': 'VWO', 'name': 'Vanguard Emerging Markets Stock ETF', 'asset_type': 'etf', 'category': 'International'},
            {'ticker': 'EEM', 'name': 'iShares MSCI Emerging Markets ETF', 'asset_type': 'etf', 'category': 'International'},
            
            # Sector
            {'ticker': 'XLK', 'name': 'Technology Select Sector SPDR Fund', 'asset_type': 'etf', 'category': 'Sector'},
            {'ticker': 'XLF', 'name': 'Financial Select Sector SPDR Fund', 'asset_type': 'etf', 'category': 'Sector'},
            {'ticker': 'XLV', 'name': 'Health Care Select Sector SPDR Fund', 'asset_type': 'etf', 'category': 'Sector'},
            {'ticker': 'XLE', 'name': 'Energy Select Sector SPDR Fund', 'asset_type': 'etf', 'category': 'Sector'},
            
            # Bond
            {'ticker': 'TLT', 'name': 'iShares 20+ Year Treasury Bond ETF', 'asset_type': 'etf', 'category': 'Bond'},
            {'ticker': 'IEF', 'name': 'iShares 7-10 Year Treasury Bond ETF', 'asset_type': 'etf', 'category': 'Bond'},
            {'ticker': 'LQD', 'name': 'iShares Investment Grade Corporate Bond ETF', 'asset_type': 'etf', 'category': 'Bond'},
            {'ticker': 'HYG', 'name': 'iShares iBoxx High Yield Corporate Bond ETF', 'asset_type': 'etf', 'category': 'Bond'},
            
            # Commodity
            {'ticker': 'GLD', 'name': 'SPDR Gold Shares', 'asset_type': 'etf', 'category': 'Commodity'},
            {'ticker': 'SLV', 'name': 'iShares Silver Trust', 'asset_type': 'etf', 'category': 'Commodity'},
            {'ticker': 'USO', 'name': 'United States Oil Fund', 'asset_type': 'etf', 'category': 'Commodity'},
            
            # Crypto
            {'ticker': 'BTC-USD', 'name': 'Bitcoin USD', 'asset_type': 'crypto', 'category': 'Cryptocurrency'},
            {'ticker': 'ETH-USD', 'name': 'Ethereum USD', 'asset_type': 'crypto', 'category': 'Cryptocurrency'},
            {'ticker': 'IBIT', 'name': 'iShares Bitcoin Trust', 'asset_type': 'etf', 'category': 'Crypto'},
            {'ticker': 'FBTC', 'name': 'Fidelity Wise Origin Bitcoin Fund', 'asset_type': 'etf', 'category': 'Crypto'},
        ]
        
        assets = []
        for etf in popular_etfs:
            assets.append({
                'ticker': etf['ticker'],
                'name': etf['name'],
                'source': 'MANUAL',
                'asset_type': etf['asset_type'],
                'category': etf.get('category', ''),
                'exchange': 'US'
            })
        
        logger.info(f"Loaded {len(assets)} popular ETFs/Crypto")
        return assets
    
    def get_commodities(self) -> List[Dict]:
        """Get commodity futures"""
        logger.info("Getting commodities...")
        
        commodities = [
            # Metals
            {'ticker': 'GC=F', 'name': 'Gold Futures', 'category': 'Metal'},
            {'ticker': 'SI=F', 'name': 'Silver Futures', 'category': 'Metal'},
            {'ticker': 'PL=F', 'name': 'Platinum Futures', 'category': 'Metal'},
            {'ticker': 'HG=F', 'name': 'Copper Futures', 'category': 'Metal'},
            
            # Energy
            {'ticker': 'CL=F', 'name': 'Crude Oil Futures', 'category': 'Energy'},
            {'ticker': 'NG=F', 'name': 'Natural Gas Futures', 'category': 'Energy'},
            {'ticker': 'RB=F', 'name': 'RBOB Gasoline Futures', 'category': 'Energy'},
            {'ticker': 'HO=F', 'name': 'Heating Oil Futures', 'category': 'Energy'},
            
            # Agriculture
            {'ticker': 'ZC=F', 'name': 'Corn Futures', 'category': 'Agriculture'},
            {'ticker': 'ZW=F', 'name': 'Wheat Futures', 'category': 'Agriculture'},
            {'ticker': 'ZS=F', 'name': 'Soybean Futures', 'category': 'Agriculture'},
            {'ticker': 'CC=F', 'name': 'Cocoa Futures', 'category': 'Agriculture'},
            {'ticker': 'SB=F', 'name': 'Sugar Futures', 'category': 'Agriculture'},
            {'ticker': 'KC=F', 'name': 'Coffee Futures', 'category': 'Agriculture'},
        ]
        
        assets = []
        for commodity in commodities:
            assets.append({
                'ticker': commodity['ticker'],
                'name': commodity['name'],
                'source': 'YAHOO_FINANCE',
                'asset_type': 'commodity',
                'category': commodity['category'],
                'exchange': 'CMX'
            })
        
        logger.info(f"Loaded {len(assets)} commodities")
        return assets
    
    def get_indices(self) -> List[Dict]:
        """Get market indices"""
        logger.info("Getting market indices...")
        
        indices = [
            {'ticker': '^GSPC', 'name': 'S&P 500', 'category': 'US Index'},
            {'ticker': '^DJI', 'name': 'Dow Jones Industrial Average', 'category': 'US Index'},
            {'ticker': '^IXIC', 'name': 'NASDAQ Composite', 'category': 'US Index'},
            {'ticker': '^RUT', 'name': 'Russell 2000', 'category': 'US Index'},
            {'ticker': '^VIX', 'name': 'CBOE Volatility Index', 'category': 'Volatility Index'},
            {'ticker': '^TNX', 'name': '10-Year Treasury Yield', 'category': 'Bond Index'},
            {'ticker': '^FVX', 'name': '5-Year Treasury Yield', 'category': 'Bond Index'},
            {'ticker': '^IRX', 'name': '13-Week Treasury Yield', 'category': 'Bond Index'},
            {'ticker': '^N225', 'name': 'Nikkei 225', 'category': 'International Index'},
            {'ticker': '^FTSE', 'name': 'FTSE 100', 'category': 'International Index'},
            {'ticker': '^GDAXI', 'name': 'DAX Performance Index', 'category': 'International Index'},
        ]
        
        assets = []
        for index in indices:
            assets.append({
                'ticker': index['ticker'],
                'name': index['name'],
                'source': 'YAHOO_FINANCE',
                'asset_type': 'index',
                'category': index['category'],
                'exchange': 'INDEX'
            })
        
        logger.info(f"Loaded {len(assets)} indices")
        return assets
    
    def get_forex_pairs(self) -> List[Dict]:
        """Get major forex pairs"""
        logger.info("Getting forex pairs...")
        
        forex_pairs = [
            {'ticker': 'EURUSD=X', 'name': 'EUR/USD', 'category': 'Major Pair'},
            {'ticker': 'GBPUSD=X', 'name': 'GBP/USD', 'category': 'Major Pair'},
            {'ticker': 'USDJPY=X', 'name': 'USD/JPY', 'category': 'Major Pair'},
            {'ticker': 'USDCHF=X', 'name': 'USD/CHF', 'category': 'Major Pair'},
            {'ticker': 'AUDUSD=X', 'name': 'AUD/USD', 'category': 'Major Pair'},
            {'ticker': 'USDCAD=X', 'name': 'USD/CAD', 'category': 'Major Pair'},
            {'ticker': 'NZDUSD=X', 'name': 'NZD/USD', 'category': 'Major Pair'},
        ]
        
        assets = []
        for pair in forex_pairs:
            assets.append({
                'ticker': pair['ticker'],
                'name': pair['name'],
                'source': 'YAHOO_FINANCE',
                'asset_type': 'forex',
                'category': pair['category'],
                'exchange': 'FOREX'
            })
        
        logger.info(f"Loaded {len(assets)} forex pairs")
        return assets
    
    def compile_all_assets(self) -> pd.DataFrame:
        """Compile assets from all sources"""
        logger.info("Compiling assets from all sources...")
        
        all_assets = []
        
        # Load from different sources
        all_assets.extend(self.load_sec_company_tickers())
        all_assets.extend(self.download_nasdaq_listings())
        all_assets.extend(self.get_sp500_stocks())
        all_assets.extend(self.get_popular_etfs())
        all_assets.extend(self.get_commodities())
        all_assets.extend(self.get_indices())
        all_assets.extend(self.get_forex_pairs())
        
        # Convert to DataFrame
        df = pd.DataFrame(all_assets)
        
        # Remove duplicates based on ticker
        df = df.drop_duplicates(subset=['ticker'], keep='first')
        
        logger.info(f"Total unique assets compiled: {len(df)}")
        
        return df
    
    def save_assets(self, df: pd.DataFrame, filename: str = "comprehensive_asset_list.csv"):
        """Save compiled assets to file"""
        output_path = self.output_dir / filename
        
        # Save as CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(df)} assets to {output_path}")
        
        # Also save as JSON
        json_path = self.output_dir / filename.replace('.csv', '.json')
        df.to_json(json_path, orient='records', indent=2)
        logger.info(f"Saved {len(df)} assets to {json_path}")
        
        # Save summary statistics
        summary = self.generate_summary(df)
        summary_path = self.output_dir / "asset_summary.txt"
        with open(summary_path, 'w') as f:
            f.write(summary)
        logger.info(f"Saved summary to {summary_path}")
        
        return output_path
    
    def generate_summary(self, df: pd.DataFrame) -> str:
        """Generate summary statistics of compiled assets"""
        summary = []
        summary.append("=" * 50)
        summary.append("COMPREHENSIVE ASSET LIST SUMMARY")
        summary.append("=" * 50)
        summary.append(f"Total Assets: {len(df)}")
        summary.append("")
        
        # By asset type
        summary.append("By Asset Type:")
        if 'asset_type' in df.columns:
            for asset_type, count in df['asset_type'].value_counts().items():
                summary.append(f"  {asset_type}: {count}")
        summary.append("")
        
        # By source
        summary.append("By Source:")
        if 'source' in df.columns:
            for source, count in df['source'].value_counts().items():
                summary.append(f"  {source}: {count}")
        summary.append("")
        
        # By exchange
        summary.append("By Exchange:")
        if 'exchange' in df.columns:
            for exchange, count in df['exchange'].value_counts().items():
                summary.append(f"  {exchange}: {count}")
        summary.append("")
        
        # Sample tickers by category
        summary.append("Sample Assets by Category:")
        if 'asset_type' in df.columns:
            for asset_type in df['asset_type'].unique():
                sample = df[df['asset_type'] == asset_type]['ticker'].head(5).tolist()
                summary.append(f"  {asset_type}: {', '.join(sample)}")
        
        return "\n".join(summary)


def main():
    """Main execution function"""
    compiler = AssetCompiler()
    
    # Compile all assets
    assets_df = compiler.compile_all_assets()
    
    # Save to files
    compiler.save_assets(assets_df)
    
    # Print summary
    print(compiler.generate_summary(assets_df))
    
    return assets_df


if __name__ == "__main__":
    main()
