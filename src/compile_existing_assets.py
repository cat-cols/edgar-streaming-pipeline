"""
Compile comprehensive asset list from existing project data
Uses SEC company_tickers.json and other existing data sources
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List

def load_sec_tickers(filepath: str = "data/raw/sec/company_tickers.json") -> List[Dict]:
    """Load SEC company tickers from existing file"""
    print("Loading SEC company tickers...")
    
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
    
    print(f"Loaded {len(companies)} companies from SEC")
    return companies

def add_additional_assets(companies: List[Dict]) -> List[Dict]:
    """Add ETFs, indices, commodities, forex, crypto to the list"""
    print("Adding additional asset classes...")
    
    additional_assets = [
        # Major ETFs
        {'ticker': 'SPY', 'name': 'SPDR S&P 500 ETF Trust', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'VOO', 'name': 'Vanguard S&P 500 ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'IVV', 'name': 'iShares Core S&P 500 ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'QQQ', 'name': 'Invesco QQQ Trust', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'IWM', 'name': 'iShares Russell 2000 ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'EFA', 'name': 'iShares MSCI EAFE ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'VEA', 'name': 'Vanguard FTSE Developed Markets ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'VWO', 'name': 'Vanguard Emerging Markets Stock ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'EEM', 'name': 'iShares MSCI Emerging Markets ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'TLT', 'name': 'iShares 20+ Year Treasury Bond ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'IEF', 'name': 'iShares 7-10 Year Treasury Bond ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'LQD', 'name': 'iShares Investment Grade Corporate Bond ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'HYG', 'name': 'iShares iBoxx High Yield Corporate Bond ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'GLD', 'name': 'SPDR Gold Shares', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'SLV', 'name': 'iShares Silver Trust', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'USO', 'name': 'United States Oil Fund', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        
        # Sector ETFs
        {'ticker': 'XLK', 'name': 'Technology Select Sector SPDR Fund', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'XLF', 'name': 'Financial Select Sector SPDR Fund', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'XLV', 'name': 'Health Care Select Sector SPDR Fund', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'XLE', 'name': 'Energy Select Sector SPDR Fund', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'XLI', 'name': 'Industrial Select Sector SPDR Fund', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'XLU', 'name': 'Utilities Select Sector SPDR Fund', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'XLP', 'name': 'Consumer Staples Select Sector SPDR Fund', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'XLY', 'name': 'Consumer Discretionary Select Sector SPDR Fund', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'XLRE', 'name': 'Real Estate Select Sector SPDR Fund', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'XLC', 'name': 'Communication Services Select Sector SPDR Fund', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'XLB', 'name': 'Materials Select Sector SPDR Fund', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        
        # Bond ETFs
        {'ticker': 'AGG', 'name': 'iShares Core U.S. Aggregate Bond ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'BND', 'name': 'Vanguard Total Bond Market ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'VCIT', 'name': 'Vanguard Intermediate-Term Corporate Bond ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'VCSH', 'name': 'Vanguard Short-Term Corporate Bond ETF', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        
        # Crypto ETFs
        {'ticker': 'IBIT', 'name': 'iShares Bitcoin Trust', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'FBTC', 'name': 'Fidelity Wise Origin Bitcoin Fund', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        {'ticker': 'ETHA', 'name': 'iShares Ethereum Trust', 'source': 'ETF', 'asset_type': 'etf', 'exchange': 'US'},
        
        # Market Indices
        {'ticker': '^GSPC', 'name': 'S&P 500 Index', 'source': 'INDEX', 'asset_type': 'index', 'exchange': 'INDEX'},
        {'ticker': '^DJI', 'name': 'Dow Jones Industrial Average', 'source': 'INDEX', 'asset_type': 'index', 'exchange': 'INDEX'},
        {'ticker': '^IXIC', 'name': 'NASDAQ Composite Index', 'source': 'INDEX', 'asset_type': 'index', 'exchange': 'INDEX'},
        {'ticker': '^RUT', 'name': 'Russell 2000 Index', 'source': 'INDEX', 'asset_type': 'index', 'exchange': 'INDEX'},
        {'ticker': '^VIX', 'name': 'CBOE Volatility Index', 'source': 'INDEX', 'asset_type': 'index', 'exchange': 'INDEX'},
        {'ticker': '^TNX', 'name': '10-Year Treasury Yield', 'source': 'INDEX', 'asset_type': 'index', 'exchange': 'INDEX'},
        {'ticker': '^FVX', 'name': '5-Year Treasury Yield', 'source': 'INDEX', 'asset_type': 'index', 'exchange': 'INDEX'},
        {'ticker': '^IRX', 'name': '13-Week Treasury Yield', 'source': 'INDEX', 'asset_type': 'index', 'exchange': 'INDEX'},
        {'ticker': '^N225', 'name': 'Nikkei 225 Index', 'source': 'INDEX', 'asset_type': 'index', 'exchange': 'INDEX'},
        {'ticker': '^FTSE', 'name': 'FTSE 100 Index', 'source': 'INDEX', 'asset_type': 'index', 'exchange': 'INDEX'},
        {'ticker': '^GDAXI', 'name': 'DAX Performance Index', 'source': 'INDEX', 'asset_type': 'index', 'exchange': 'INDEX'},
        
        # Commodities (Futures)
        {'ticker': 'GC=F', 'name': 'Gold Futures', 'source': 'COMMODITY', 'asset_type': 'commodity', 'exchange': 'COMEX'},
        {'ticker': 'SI=F', 'name': 'Silver Futures', 'source': 'COMMODITY', 'asset_type': 'commodity', 'exchange': 'COMEX'},
        {'ticker': 'PL=F', 'name': 'Platinum Futures', 'source': 'COMMODITY', 'asset_type': 'commodity', 'exchange': 'NYMEX'},
        {'ticker': 'HG=F', 'name': 'Copper Futures', 'source': 'COMMODITY', 'asset_type': 'commodity', 'exchange': 'COMEX'},
        {'ticker': 'CL=F', 'name': 'Crude Oil Futures', 'source': 'COMMODITY', 'asset_type': 'commodity', 'exchange': 'NYMEX'},
        {'ticker': 'NG=F', 'name': 'Natural Gas Futures', 'source': 'COMMODITY', 'asset_type': 'commodity', 'exchange': 'NYMEX'},
        {'ticker': 'RB=F', 'name': 'RBOB Gasoline Futures', 'source': 'COMMODITY', 'asset_type': 'commodity', 'exchange': 'NYMEX'},
        {'ticker': 'HO=F', 'name': 'Heating Oil Futures', 'source': 'COMMODITY', 'asset_type': 'commodity', 'exchange': 'NYMEX'},
        {'ticker': 'ZC=F', 'name': 'Corn Futures', 'source': 'COMMODITY', 'asset_type': 'commodity', 'exchange': 'CBOT'},
        {'ticker': 'ZW=F', 'name': 'Wheat Futures', 'source': 'COMMODITY', 'asset_type': 'commodity', 'exchange': 'CBOT'},
        {'ticker': 'ZS=F', 'name': 'Soybean Futures', 'source': 'COMMODITY', 'asset_type': 'commodity', 'exchange': 'CBOT'},
        {'ticker': 'CC=F', 'name': 'Cocoa Futures', 'source': 'COMMODITY', 'asset_type': 'commodity', 'exchange': 'ICE'},
        {'ticker': 'SB=F', 'name': 'Sugar Futures', 'source': 'COMMODITY', 'asset_type': 'commodity', 'exchange': 'ICE'},
        {'ticker': 'KC=F', 'name': 'Coffee Futures', 'source': 'COMMODITY', 'asset_type': 'commodity', 'exchange': 'ICE'},
        
        # Forex Pairs
        {'ticker': 'EURUSD=X', 'name': 'EUR/USD', 'source': 'FOREX', 'asset_type': 'forex', 'exchange': 'FOREX'},
        {'ticker': 'GBPUSD=X', 'name': 'GBP/USD', 'source': 'FOREX', 'asset_type': 'forex', 'exchange': 'FOREX'},
        {'ticker': 'USDJPY=X', 'name': 'USD/JPY', 'source': 'FOREX', 'asset_type': 'forex', 'exchange': 'FOREX'},
        {'ticker': 'USDCHF=X', 'name': 'USD/CHF', 'source': 'FOREX', 'asset_type': 'forex', 'exchange': 'FOREX'},
        {'ticker': 'AUDUSD=X', 'name': 'AUD/USD', 'source': 'FOREX', 'asset_type': 'forex', 'exchange': 'FOREX'},
        {'ticker': 'USDCAD=X', 'name': 'USD/CAD', 'source': 'FOREX', 'asset_type': 'forex', 'exchange': 'FOREX'},
        {'ticker': 'NZDUSD=X', 'name': 'NZD/USD', 'source': 'FOREX', 'asset_type': 'forex', 'exchange': 'FOREX'},
        {'ticker': 'EURGBP=X', 'name': 'EUR/GBP', 'source': 'FOREX', 'asset_type': 'forex', 'exchange': 'FOREX'},
        {'ticker': 'EURJPY=X', 'name': 'EUR/JPY', 'source': 'FOREX', 'asset_type': 'forex', 'exchange': 'FOREX'},
        {'ticker': 'GBPJPY=X', 'name': 'GBP/JPY', 'source': 'FOREX', 'asset_type': 'forex', 'exchange': 'FOREX'},
        
        # Cryptocurrencies
        {'ticker': 'BTC-USD', 'name': 'Bitcoin USD', 'source': 'CRYPTO', 'asset_type': 'crypto', 'exchange': 'CRYPTO'},
        {'ticker': 'ETH-USD', 'name': 'Ethereum USD', 'source': 'CRYPTO', 'asset_type': 'crypto', 'exchange': 'CRYPTO'},
        {'ticker': 'BNB-USD', 'name': 'Binance Coin USD', 'source': 'CRYPTO', 'asset_type': 'crypto', 'exchange': 'CRYPTO'},
        {'ticker': 'XRP-USD', 'name': 'Ripple USD', 'source': 'CRYPTO', 'asset_type': 'crypto', 'exchange': 'CRYPTO'},
        {'ticker': 'SOL-USD', 'name': 'Solana USD', 'source': 'CRYPTO', 'asset_type': 'crypto', 'exchange': 'CRYPTO'},
        {'ticker': 'ADA-USD', 'name': 'Cardano USD', 'source': 'CRYPTO', 'asset_type': 'crypto', 'exchange': 'CRYPTO'},
        {'ticker': 'DOGE-USD', 'name': 'Dogecoin USD', 'source': 'CRYPTO', 'asset_type': 'crypto', 'exchange': 'CRYPTO'},
        {'ticker': 'DOT-USD', 'name': 'Polkadot USD', 'source': 'CRYPTO', 'asset_type': 'crypto', 'exchange': 'CRYPTO'},
    ]
    
    print(f"Added {len(additional_assets)} additional assets")
    return companies + additional_assets

def create_summary(df: pd.DataFrame) -> str:
    """Generate summary of compiled assets"""
    summary = []
    summary.append("=" * 60)
    summary.append("COMPREHENSIVE TRADEABLE ASSET LIST")
    summary.append("=" * 60)
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
            sample = df[df['asset_type'] == asset_type]['ticker'].head(10).tolist()
            summary.append(f"  {asset_type}: {', '.join(sample)}")
    summary.append("")
    
    return "\n".join(summary)

def main():
    """Main execution"""
    print("=" * 60)
    print("COMPILING COMPREHENSIVE ASSET LIST")
    print("=" * 60)
    
    # Load SEC data
    companies = load_sec_tickers()
    
    # Add additional assets
    all_assets = add_additional_assets(companies)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_assets)
    
    # Remove duplicates based on ticker
    df = df.drop_duplicates(subset=['ticker'], keep='first')
    
    print(f"\nTotal unique assets: {len(df)}")
    
    # Create output directory
    output_dir = Path("assets/compiled")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as CSV
    csv_path = output_dir / "comprehensive_asset_list.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved to: {csv_path}")
    
    # Save as JSON
    json_path = output_dir / "comprehensive_asset_list.json"
    df.to_json(json_path, orient='records', indent=2)
    print(f"Saved to: {json_path}")
    
    # Generate and save summary
    summary = create_summary(df)
    summary_path = output_dir / "asset_summary.txt"
    with open(summary_path, 'w') as f:
        f.write(summary)
    print(f"Saved summary to: {summary_path}")
    
    print("\n" + summary)
    
    return df

if __name__ == "__main__":
    main()
