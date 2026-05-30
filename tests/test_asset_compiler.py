"""
Test script for asset compiler - tests individual data sources
"""

import json
import pandas as pd
import requests
from pathlib import Path

def test_sec_data():
    """Test loading SEC company tickers"""
    print("Testing SEC company tickers...")
    filepath = "assets/1.ingestion/2.Data_Ingestion/0.SOURCES/_data/company_tickers.json"
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        print(f"✓ SEC data loaded successfully")
        print(f"  Total entries: {len(data)}")
        
        # Show sample
        sample_keys = list(data.keys())[:5]
        print(f"  Sample entries: {sample_keys}")
        for key in sample_keys:
            print(f"    {data[key]}")
        
        return True
    except Exception as e:
        print(f"✗ Error loading SEC data: {e}")
        return False

def test_nasdaq_download():
    """Test downloading NASDAQ listings"""
    print("\nTesting NASDAQ listings download...")
    
    try:
        url = "https://raw.githubusercontent.com/datasets/nasdaq-listings/main/data/nasdaq-listed.csv"
        response = requests.get(url)
        
        from io import StringIO
        df = pd.read_csv(StringIO(response.text))
        
        print(f"✓ NASDAQ data downloaded successfully")
        print(f"  Total entries: {len(df)}")
        print(f"  Columns: {df.columns.tolist()}")
        print(f"  Sample rows:")
        print(df.head())
        
        return True
    except Exception as e:
        print(f"✗ Error downloading NASDAQ data: {e}")
        return False

def test_yfinance():
    """Test yfinance installation"""
    print("\nTesting yfinance...")
    
    try:
        import yfinance as yf
        print(f"✓ yfinance imported successfully")
        
        # Test getting info for a known ticker
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        print(f"  AAPL info retrieved successfully")
        print(f"  Company name: {info.get('longName', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"✗ Error with yfinance: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("ASSET COMPILER DATA SOURCE TEST")
    print("=" * 50)
    
    results = []
    results.append(("SEC Data", test_sec_data()))
    results.append(("NASDAQ Download", test_nasdaq_download()))
    results.append(("yfinance", test_yfinance()))
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name}: {status}")
