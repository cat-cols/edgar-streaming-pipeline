"""
SEC EDGAR Filing Monitor Script
Checks for and extracts new SEC filings
"""

import requests
import json
import pandas as pd
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SECFilingMonitor:
    """Monitor and extract new SEC filings"""
    
    def __init__(self, output_dir: str = "data/raw/sec/filings"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # SEC EDGAR API requires User-Agent header
        self.headers = {
            "User-Agent": "EDGAR Streaming Pipeline brandon.hardison@gmail.com",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*"
        }
        
        # Track processed filings
        self.processed_filings_file = self.output_dir / "processed_filings.json"
        self.processed_filings = self.load_processed_filings()
        
        # Filing types to monitor
        self.filing_types = {
            '10-K': 'Annual Report',
            '10-Q': 'Quarterly Report', 
            '8-K': 'Current Report',
            '10-K/A': 'Amended Annual Report',
            '10-Q/A': 'Amended Quarterly Report',
            '8-K/A': 'Amended Current Report',
            'S-1': 'Registration Statement',
            'DEF 14A': 'Proxy Statement',
            '13F': 'Institutional Holdings',
            'SC 13G': 'Beneficial Ownership Report',
            'SC 13D': 'Beneficial Ownership Report'
        }
    
    def load_processed_filings(self) -> Set[str]:
        """Load set of already processed filing accession numbers"""
        if self.processed_filings_file.exists():
            with open(self.processed_filings_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def save_processed_filings(self):
        """Save set of processed filing accession numbers"""
        with open(self.processed_filings_file, 'w') as f:
            json.dump(list(self.processed_filings), f)
    
    def get_company_submissions(self, cik: str) -> Optional[Dict]:
        """Get company submission data including recent filings"""
        cik_str = str(cik).zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{cik_str}.json"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching submissions for CIK {cik}: {e}")
            return None
    
    def extract_recent_filings(self, submission_data: Dict, days: int = 7) -> List[Dict]:
        """Extract recent filings from company submission data"""
        recent_filings = []
        
        if 'filings' not in submission_data or 'recent' not in submission_data['filings']:
            return recent_filings
        
        recent = submission_data['filings']['recent']
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for i in range(len(recent.get('form', []))):
            filing_date = datetime.strptime(recent['filingDate'][i], "%Y-%m-%d")
            
            if filing_date >= cutoff_date:
                accession_number = recent['accessionNumber'][i]
                
                # Skip if already processed
                if accession_number in self.processed_filings:
                    continue
                
                form_type = recent['form'][i]
                
                # Filter by filing types
                if form_type in self.filing_types:
                    filing_info = {
                        'cik': submission_data['cik'],
                        'accession_number': accession_number,
                        'form_type': form_type,
                        'filing_date': recent['filingDate'][i],
                        'file_number': recent.get('fileNumber', [''])[i] if 'fileNumber' in recent else '',
                        'primary_document': recent['primaryDocument'][i],
                        'primary_doc_description': recent.get('primaryDocDescription', [''])[i] if 'primaryDocDescription' in recent else '',
                    }
                    recent_filings.append(filing_info)
        
        return recent_filings
    
    def get_filing_document_url(self, cik: str, accession_number: str, primary_document: str) -> str:
        """Construct URL to download filing document"""
        # Remove dashes from accession number for URL
        accession_clean = accession_number.replace('-', '')
        return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}/{primary_document}"
    
    def download_filing_document(self, url: str) -> Optional[str]:
        """Download filing document content"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading filing document from {url}: {e}")
            return None
    
    def save_filing_document(self, filing_info: Dict, content: str):
        """Save filing document to file"""
        # Create directory structure: data/raw/sec/filings/{form_type}/{cik}/
        form_type_dir = self.output_dir / filing_info['form_type']
        cik_dir = form_type_dir / filing_info['cik']
        cik_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename: {accession_number}.txt
        filename = f"{filing_info['accession_number']}.txt"
        filepath = cik_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        logger.info(f"Saved filing to {filepath}")
    
    def save_filing_metadata(self, filings: List[Dict]):
        """Save filing metadata to CSV"""
        metadata_file = self.output_dir / "filing_metadata.csv"
        
        # Load existing metadata if exists
        if metadata_file.exists():
            existing_df = pd.read_csv(metadata_file)
            new_df = pd.DataFrame(filings)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            combined_df = pd.DataFrame(filings)
        
        combined_df.to_csv(metadata_file, index=False)
        logger.info(f"Saved filing metadata to {metadata_file}")
    
    def monitor_company(self, cik: str, days: int = 7) -> List[Dict]:
        """Monitor a single company for new filings"""
        logger.info(f"Monitoring company CIK {cik} for filings in last {days} days...")
        
        submission_data = self.get_company_submissions(cik)
        if not submission_data:
            return []
        
        recent_filings = self.extract_recent_filings(submission_data, days)
        
        if recent_filings:
            logger.info(f"Found {len(recent_filings)} new filings for CIK {cik}")
            
            for filing in recent_filings:
                # Download and save document
                url = self.get_filing_document_url(filing['cik'], filing['accession_number'], filing['primary_document'])
                content = self.download_filing_document(url)
                
                if content:
                    self.save_filing_document(filing, content)
                    self.processed_filings.add(filing['accession_number'])
        
        return recent_filings
    
    def monitor_multiple_companies(self, ciks: List[str], days: int = 7, delay: float = 0.1) -> List[Dict]:
        """Monitor multiple companies for new filings"""
        logger.info(f"Monitoring {len(ciks)} companies for filings in last {days} days...")
        
        all_new_filings = []
        
        for i, cik in enumerate(ciks):
            if i % 100 == 0:
                logger.info(f"Progress: {i}/{len(ciks)} companies processed")
            
            new_filings = self.monitor_company(cik, days)
            all_new_filings.extend(new_filings)
            
            # Rate limiting
            time.sleep(delay)
        
        if all_new_filings:
            self.save_filing_metadata(all_new_filings)
            self.save_processed_filings()
        
        logger.info(f"Total new filings found: {len(all_new_filings)}")
        return all_new_filings
    
    def monitor_from_ticker_file(self, ticker_file: str = "data/raw/sec/company_tickers.json", 
                                 days: int = 7, sample_size: Optional[int] = None) -> List[Dict]:
        """Monitor companies from ticker file"""
        logger.info(f"Loading companies from {ticker_file}...")
        
        with open(ticker_file, 'r') as f:
            data = json.load(f)
        
        # Extract CIKs
        ciks = [value['cik_str'] for key, value in data.items()]
        
        # Sample if specified
        if sample_size:
            ciks = ciks[:sample_size]
            logger.info(f"Monitoring sample of {sample_size} companies")
        
        return self.monitor_multiple_companies(ciks, days)
    
    def get_daily_index(self, date: Optional[str] = None) -> Optional[Dict]:
        """Get daily filing index for a specific date"""
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        
        url = f"https://www.sec.gov/Archives/edgar/data/{date}.idx"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse the index file (fixed-width format)
            lines = response.text.split('\n')
            filings = []
            
            for line in lines[11:]:  # Skip header lines
                if len(line) > 100:
                    cik = line[0:10].strip()
                    company_name = line[10:82].strip()
                    form_type = line[62:72].strip()
                    filing_date = line[86:96].strip()
                    
                    filings.append({
                        'cik': cik,
                        'company_name': company_name,
                        'form_type': form_type,
                        'filing_date': filing_date
                    })
            
            return {'date': date, 'filings': filings}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching daily index for {date}: {e}")
            return None
    
    def monitor_daily_filings(self, date: Optional[str] = None, 
                            form_types: Optional[List[str]] = None) -> List[Dict]:
        """Monitor all filings for a specific day"""
        if form_types is None:
            form_types = list(self.filing_types.keys())
        
        logger.info(f"Monitoring daily filings for {date or 'today'}...")
        
        daily_index = self.get_daily_index(date)
        if not daily_index:
            return []
        
        filtered_filings = []
        for filing in daily_index['filings']:
            if filing['form_type'] in form_types:
                accession = f"{filing['cik']}_{filing['filing_date']}_{filing['form_type']}"
                
                if accession not in self.processed_filings:
                    filtered_filings.append(filing)
                    self.processed_filings.add(accession)
        
        logger.info(f"Found {len(filtered_filings)} new filings matching criteria")
        return filtered_filings


def main():
    """Main execution function"""
    monitor = SECFilingMonitor()
    
    # Option 1: Monitor from ticker file (sample for testing)
    logger.info("Starting SEC filing monitoring...")
    
    # Monitor sample of companies (adjust sample_size as needed)
    new_filings = monitor.monitor_from_ticker_file(
        ticker_file="data/raw/sec/company_tickers.json",
        days=7,
        sample_size=50  # Start with small sample for testing
    )
    
    # Option 2: Monitor daily filings (alternative approach)
    # new_filings = monitor.monitor_daily_filings(form_types=['10-K', '10-Q', '8-K'])
    
    if new_filings:
        logger.info(f"Successfully processed {len(new_filings)} new filings")
    else:
        logger.info("No new filings found")
    
    logger.info("SEC filing monitoring completed")


if __name__ == "__main__":
    main()
