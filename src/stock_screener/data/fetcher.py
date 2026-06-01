"""
Data fetcher for financial data from multiple sources
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetch financial data from various sources"""

    def __init__(self):
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load_asset_universe(self, filepath: str = "data/reference/comprehensive_asset_list.csv") -> pd.DataFrame:
        """Load the compiled asset universe"""
        logger.info("Loading asset universe...")
        df = pd.read_csv(filepath)
        stocks = df[df['asset_type'] == 'stock']
        logger.info(f"Loaded {len(stocks)} stocks from asset universe")
        return stocks
    
    def fetch_stock_data(self, tickers: List[str], period: str = "2y", 
                        interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """Fetch historical price data for multiple stocks"""
        logger.info(f"Fetching data for {len(tickers)} stocks...")
        
        data = {}
        # Process in batches to avoid overwhelming the API
        batch_size = 100
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i+batch_size]
            try:
                batch_data = yf.download(batch, period=period, interval=interval, progress=False, auto_adjust=False)
                
                # Handle different yfinance return formats
                if isinstance(batch_data, pd.DataFrame) and not batch_data.empty:
                    # Check if it's a multi-index column format (newer yfinance)
                    if isinstance(batch_data.columns, pd.MultiIndex):
                        for ticker in batch:
                            if ticker in batch_data.columns.levels[0]:
                                data[ticker] = batch_data[ticker].copy()
                    else:
                        # Single ticker or different format
                        if len(batch) == 1:
                            ticker = batch[0]
                            data[ticker] = batch_data.copy()
                        else:
                            # Try to extract by column names
                            for ticker in batch:
                                if ticker in batch_data.columns:
                                    data[ticker] = batch_data[[ticker]].copy()
                
                logger.info(f"Fetched batch {i//batch_size + 1}/{(len(tickers)-1)//batch_size + 1}")
            except Exception as e:
                logger.error(f"Error fetching batch {i//batch_size + 1}: {e}")
        
        logger.info(f"Successfully fetched data for {len(data)} stocks")
        return data
    
    def fetch_fundamental_data(self, tickers: List[str]) -> Dict[str, Dict]:
        """Fetch fundamental data (P/E, P/B, market cap, etc.)"""
        logger.info(f"Fetching fundamental data for {len(tickers)} stocks...")
        
        fundamentals = {}
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                fundamentals[ticker] = {
                    'pe_ratio': info.get('forwardPE', np.nan),
                    'pb_ratio': info.get('priceToBook', np.nan),
                    'ps_ratio': info.get('priceToSalesTrailing12Months', np.nan),
                    'ev_ebitda': info.get('enterpriseToEbitda', np.nan),
                    'market_cap': info.get('marketCap', np.nan),
                    'dividend_yield': info.get('dividendYield', np.nan),
                    'roe': info.get('returnOnEquity', np.nan),
                    'roa': info.get('returnOnAssets', np.nan),
                    'profit_margin': info.get('profitMargins', np.nan),
                    'operating_margin': info.get('operatingMargins', np.nan),
                    'debt_to_equity': info.get('debtToEquity', np.nan),
                    'current_ratio': info.get('currentRatio', np.nan),
                    'quick_ratio': info.get('quickRatio', np.nan),
                    'beta': info.get('beta', np.nan),
                    '52_week_high': info.get('fiftyTwoWeekHigh', np.nan),
                    '52_week_low': info.get('fiftyTwoWeekLow', np.nan),
                }
                
            except Exception as e:
                logger.warning(f"Error fetching fundamentals for {ticker}: {e}")
                fundamentals[ticker] = {}
        
        logger.info(f"Fetched fundamental data for {len([f for f in fundamentals.values() if f])} stocks")
        return fundamentals
    
    def calculate_returns(self, price_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.Series]:
        """Calculate returns for each stock"""
        returns = {}
        for ticker, df in price_data.items():
            if 'Close' in df.columns:
                returns[ticker] = df['Close'].pct_change().dropna()
        return returns
    
    def calculate_technical_indicators(self, price_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """Calculate technical indicators for each stock"""
        logger.info("Calculating technical indicators...")
        
        indicators = {}
        for ticker, df in price_data.items():
            if 'Close' in df.columns:
                close = df['Close']
                
                # Moving averages
                sma_50 = close.rolling(window=50).mean()
                sma_200 = close.rolling(window=200).mean()
                
                # RSI
                delta = close.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                
                # Momentum
                momentum_3m = close.pct_change(63)  # ~3 months
                momentum_6m = close.pct_change(126)  # ~6 months
                momentum_12m = close.pct_change(252)  # ~12 months
                
                # Volatility
                volatility = close.pct_change().rolling(window=20).std()
                
                indicators[ticker] = {
                    'sma_50': sma_50.iloc[-1] if len(sma_50) > 0 else np.nan,
                    'sma_200': sma_200.iloc[-1] if len(sma_200) > 0 else np.nan,
                    'rsi': rsi.iloc[-1] if len(rsi) > 0 else np.nan,
                    'momentum_3m': momentum_3m.iloc[-1] if len(momentum_3m) > 0 else np.nan,
                    'momentum_6m': momentum_6m.iloc[-1] if len(momentum_6m) > 0 else np.nan,
                    'momentum_12m': momentum_12m.iloc[-1] if len(momentum_12m) > 0 else np.nan,
                    'volatility': volatility.iloc[-1] if len(volatility) > 0 else np.nan,
                    'price_above_sma50': close.iloc[-1] > sma_50.iloc[-1] if len(sma_50) > 0 else np.nan,
                    'price_above_sma200': close.iloc[-1] > sma_200.iloc[-1] if len(sma_200) > 0 else np.nan,
                }
        
        logger.info(f"Calculated technical indicators for {len(indicators)} stocks")
        return indicators
