"""
SEC EDGAR RSS Feed Fetcher
Fetches latest filings from SEC RSS feed (Atom format)
"""

import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SECRSSFeedFetcher:
    """Fetch and parse SEC EDGAR RSS feed"""
    
    def __init__(self, output_dir: str = "data/raw/sec/rss_feed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # SEC EDGAR API requires User-Agent header
        self.headers = {
            "User-Agent": "EDGAR Streaming Pipeline brandon.hardison@gmail.com",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "application/atom+xml,application/xml,text/xml"
        }
        
        # SEC RSS feed URL for current filings
        self.rss_feed_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&output=atom"
        
        # Filing types to prioritize
        self.priority_forms = [
            '10-K', '10-Q', '8-K', '10-K/A', '10-Q/A', '8-K/A',
            'S-1', 'DEF 14A', '13F', 'SC 13G', 'SC 13D', '4', '3', '5'
        ]
    
    def fetch_rss_feed(self) -> Optional[str]:
        """Fetch RSS feed content from SEC"""
        logger.info(f"Fetching RSS feed from {self.rss_feed_url}...")
        
        try:
            response = requests.get(self.rss_feed_url, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Successfully fetched RSS feed (size: {len(response.content)} bytes)")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching RSS feed: {e}")
            return None
    
    def parse_atom_feed(self, feed_content: str) -> List[Dict]:
        """Parse Atom feed XML and extract filing information"""
        logger.info("Parsing Atom feed...")
        
        try:
            root = ET.fromstring(feed_content)
            
            # Atom namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            filings = []
            
            # Iterate through entry elements (each filing)
            for entry in root.findall('atom:entry', ns):
                filing = {}
                
                # Extract basic information
                title = entry.find('atom:title', ns)
                if title is not None:
                    filing['title'] = title.text
                
                # Extract link (filing URL)
                link = entry.find('atom:link', ns)
                if link is not None:
                    filing['filing_url'] = link.get('href')
                
                # Extract summary/description
                summary = entry.find('atom:summary', ns)
                if summary is not None:
                    filing['summary'] = summary.text
                
                # Extract updated date
                updated = entry.find('atom:updated', ns)
                if updated is not None:
                    filing['updated'] = updated.text
                
                # Extract id
                id_elem = entry.find('atom:id', ns)
                if id_elem is not None:
                    filing['id'] = id_elem.text
                
                # Extract category (form type)
                category = entry.find('atom:category', ns)
                if category is not None:
                    filing['form_type'] = category.get('term')
                    filing['form_label'] = category.get('label')
                
                # Parse filing details from title or summary
                if 'title' in filing:
                    # Title format is typically: "COMPANY_NAME - FORM_TYPE (FILED DATE)"
                    parts = filing['title'].split(' - ')
                    if len(parts) >= 2:
                        filing['company_name'] = parts[0].strip()
                        form_part = parts[1].strip()
                        filing['form_info'] = form_part
                
                # Extract CIK from URL if available
                if 'filing_url' in filing:
                    # URL format: https://www.sec.gov/Archives/edgar/data/CIK/...
                    url_parts = filing['filing_url'].split('/edgar/data/')
                    if len(url_parts) > 1:
                        cik_part = url_parts[1].split('/')[0]
                        filing['cik'] = cik_part
                
                # Add priority flag
                filing['is_priority'] = filing.get('form_type', '') in self.priority_forms
                
                # Add timestamp
                filing['fetched_at'] = datetime.now().isoformat()
                
                filings.append(filing)
            
            logger.info(f"Parsed {len(filings)} filings from RSS feed")
            return filings
            
        except ET.ParseError as e:
            logger.error(f"Error parsing Atom feed: {e}")
            return []
    
    def filter_filings(self, filings: List[Dict], 
                      form_types: Optional[List[str]] = None,
                      priority_only: bool = False) -> List[Dict]:
        """Filter filings by form type or priority"""
        filtered = filings
        
        if priority_only:
            filtered = [f for f in filtered if f.get('is_priority', False)]
            logger.info(f"Filtered to {len(filtered)} priority filings")
        
        if form_types:
            filtered = [f for f in filtered if f.get('form_type') in form_types]
            logger.info(f"Filtered to {len(filtered)} filings matching form types: {form_types}")
        
        return filtered
    
    def save_to_csv(self, filings: List[Dict], filename: Optional[str] = None):
        """Save filings to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sec_filings_{timestamp}.csv"
        
        output_path = self.output_dir / filename
        
        df = pd.DataFrame(filings)
        df.to_csv(output_path, index=False)
        
        logger.info(f"Saved {len(filings)} filings to {output_path}")
    
    def save_to_json(self, filings: List[Dict], filename: Optional[str] = None):
        """Save filings to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sec_filings_{timestamp}.json"
        
        output_path = self.output_dir / filename
        
        import json
        with open(output_path, 'w') as f:
            json.dump(filings, f, indent=2)
        
        logger.info(f"Saved {len(filings)} filings to {output_path}")
    
    def fetch_and_save(self, 
                      save_csv: bool = True,
                      save_json: bool = True,
                      form_types: Optional[List[str]] = None,
                      priority_only: bool = False):
        """Fetch, parse, filter and save filings"""
        # Fetch RSS feed
        feed_content = self.fetch_rss_feed()
        if not feed_content:
            logger.error("Failed to fetch RSS feed")
            return
        
        # Parse feed
        filings = self.parse_atom_feed(feed_content)
        if not filings:
            logger.error("No filings parsed from feed")
            return
        
        # Filter if requested
        if form_types or priority_only:
            filings = self.filter_filings(filings, form_types, priority_only)
        
        # Save to files
        if save_csv:
            self.save_to_csv(filings)
        
        if save_json:
            self.save_to_json(filings)
        
        # Print summary
        logger.info(f"=== Summary ===")
        logger.info(f"Total filings: {len(filings)}")
        
        if filings:
            # Count by form type
            form_counts = {}
            for filing in filings:
                form_type = filing.get('form_type', 'UNKNOWN')
                form_counts[form_type] = form_counts.get(form_type, 0) + 1
            
            logger.info("Filings by form type:")
            for form_type, count in sorted(form_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {form_type}: {count}")
        
        return filings


def main():
    """Main execution function"""
    fetcher = SECRSSFeedFetcher()
    
    # Fetch all filings
    logger.info("Fetching all current SEC filings...")
    filings = fetcher.fetch_and_save(save_csv=True, save_json=True)
    
    # Also fetch priority filings only
    if filings:
        logger.info("\nFetching priority filings only...")
        priority_filings = fetcher.fetch_and_save(
            save_csv=True, 
            save_json=False,
            priority_only=True
        )
    
    logger.info("SEC RSS feed fetching completed")


if __name__ == "__main__":
    main()
