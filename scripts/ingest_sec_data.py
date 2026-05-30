"""
SEC EDGAR API Data Ingestion Script
Ingests company tickers, ETFs, and other SEC data using the SEC EDGAR API
"""

import requests
import json
import pandas as pd
import time
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SECEdgarIngestor:
    """Ingest data from SEC EDGAR API"""

    def __init__(self, output_dir: str = "data/raw/sec"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # SEC EDGAR API requires User-Agent header
        self.headers = {
            "User-Agent": "EDGAR Streaming Pipeline brandon.hardison@gmail.com",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*"
        }

        # SEC EDGAR API endpoints
        self.company_tickers_url = "https://www.sec.gov/files/company_tickers.json"
        self.company_tickers_exchange_url = "https://www.sec.gov/files/company_tickers_exchange.json"

    def fetch_company_tickers(self) -> Dict:
        """Fetch company tickers from SEC EDGAR API"""
        logger.info("Fetching company tickers from SEC EDGAR API...")

        try:
            response = requests.get(self.company_tickers_url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Successfully fetched {len(data)} company tickers")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching company tickers: {e}")
            return {}

    def fetch_company_tickers_exchange(self) -> Dict:
        """Fetch company tickers by exchange from SEC EDGAR API"""
        logger.info("Fetching company tickers by exchange from SEC EDGAR API...")

        try:
            response = requests.get(self.company_tickers_exchange_url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Successfully fetched exchange data")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching company tickers by exchange: {e}")
            return {}

    def fetch_company_facts(self, cik: str) -> Optional[Dict]:
        """Fetch company facts for a specific CIK"""
        url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Successfully fetched company facts for CIK {cik}")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching company facts for CIK {cik}: {e}")
            return None

    def fetch_company_facts_batch(self, ciks: List[str], delay: float = 0.1) -> List[Dict]:
        """Fetch company facts for multiple CIKs with rate limiting"""
        logger.info(f"Fetching company facts for {len(ciks)} companies...")

        results = []
        for i, cik in enumerate(ciks):
            if i % 100 == 0:
                logger.info(f"Progress: {i}/{len(ciks)} companies processed")

            data = self.fetch_company_facts(cik)
            if data:
                results.append(data)

            # Rate limiting
            time.sleep(delay)

        logger.info(f"Successfully fetched {len(results)} company facts")
        return results

    def parse_company_tickers(self, data: Dict) -> List[Dict]:
        """Parse company tickers data into structured format"""
        companies = []

        for key, value in data.items():
            companies.append({
                'cik': value['cik_str'],
                'ticker': value['ticker'],
                'name': value['title'],
                'exchange': value.get('exch', ''),
                'source': 'SEC_EDGAR',
                'asset_type': 'stock'
            })

        return companies

    def parse_exchange_data(self, data: Dict) -> Dict[str, List[Dict]]:
        """Parse exchange-specific company data"""
        exchange_data = {}

        # Handle different data structures
        if isinstance(data, list):
            # Data is a list, skip parsing
            logger.info("Exchange data is a list, skipping detailed parsing")
            return {}

        for exchange_code, companies in data.items():
            if exchange_code == 'filename':
                continue

            # Handle if companies is a list
            if isinstance(companies, list):
                logger.info(f"Exchange {exchange_code} contains list data, skipping")
                continue

            exchange_companies = []
            for key, value in companies.items():
                exchange_companies.append({
                    'cik': value['cik_str'],
                    'ticker': value['ticker'],
                    'name': value['title'],
                    'exchange': exchange_code,
                    'source': 'SEC_EDGAR',
                    'asset_type': 'stock'
                })
            
            exchange_data[exchange_code] = exchange_companies
        
        return exchange_data
    
    def save_company_tickers(self, data: Dict, filename: str = "company_tickers.json"):
        """Save company tickers to file"""
        output_path = self.output_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved company tickers to {output_path}")
    
    def save_company_tickers_csv(self, companies: List[Dict], filename: str = "company_tickers.csv"):
        """Save company tickers to CSV file"""
        output_path = self.output_dir / filename
        
        df = pd.DataFrame(companies)
        df.to_csv(output_path, index=False)
        
        logger.info(f"Saved company tickers CSV to {output_path}")
    
    def save_exchange_data(self, exchange_data: Dict[str, List[Dict]]):
        """Save exchange-specific data to separate files"""
        for exchange, companies in exchange_data.items():
            filename = f"company_tickers_{exchange.lower()}.csv"
            output_path = self.output_dir / filename
            
            df = pd.DataFrame(companies)
            df.to_csv(output_path, index=False)
            
            logger.info(f"Saved {exchange} data to {output_path}")
    
    def fetch_and_save_all(self):
        """Fetch and save all SEC data"""
        logger.info("Starting SEC EDGAR data ingestion...")
        
        # Fetch company tickers
        company_tickers = self.fetch_company_tickers()
        if company_tickers:
            self.save_company_tickers(company_tickers)
            
            # Parse and save as CSV
            companies = self.parse_company_tickers(company_tickers)
            self.save_company_tickers_csv(companies)
        
        # Fetch exchange-specific data
        exchange_data = self.fetch_company_tickers_exchange()
        if exchange_data:
            parsed_exchange_data = self.parse_exchange_data(exchange_data)
            self.save_exchange_data(parsed_exchange_data)
        
        logger.info("SEC EDGAR data ingestion completed")
    
    def get_etf_list(self) -> List[Dict]:
        """Get list of ETFs from SEC data"""
        logger.info("Extracting ETF list from SEC data...")
        
        # Load company tickers
        company_tickers_path = self.output_dir / "company_tickers.json"
        if not company_tickers_path.exists():
            logger.warning("Company tickers file not found. Fetching first...")
            self.fetch_and_save_all()
        
        with open(company_tickers_path, 'r') as f:
            data = json.load(f)
        
        # Filter for ETFs (this is a simplified approach)
        # In practice, you'd need more sophisticated filtering
        etfs = []
        for key, value in data.items():
            name = value['title'].lower()
            ticker = value['ticker']
            
            # Simple heuristic for ETF detection
            if any(keyword in name for keyword in ['etf', 'trust', 'fund', 'portfolio', 'index']):
                etfs.append({
                    'cik': value['cik_str'],
                    'ticker': ticker,
                    'name': value['title'],
                    'source': 'SEC_EDGAR',
                    'asset_type': 'etf'
                })
        
        logger.info(f"Found {len(etfs)} potential ETFs")
        return etfs
    
    def save_etf_list(self, etfs: List[Dict], filename: str = "etf_list.json"):
        """Save ETF list to file"""
        output_path = self.output_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(etfs, f, indent=2)
        
        logger.info(f"Saved ETF list to {output_path}")


def main():
    """Main execution function"""
    ingestor = SECEdgarIngestor()
    
    # Fetch and save all SEC data
    ingestor.fetch_and_save_all()
    
    # Extract and save ETF list
    etfs = ingestor.get_etf_list()
    if etfs:
        ingestor.save_etf_list(etfs)
    
    logger.info("SEC EDGAR data ingestion completed successfully")


if __name__ == "__main__":
    main()
