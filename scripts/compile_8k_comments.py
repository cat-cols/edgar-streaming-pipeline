"""
SEC 8-K Comments Section Compiler
Extracts and compiles comments/explanatory sections from 8-K filings
"""

import requests
import re
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EightKCommentsCompiler:
    """Compile comments sections from SEC 8-K filings"""
    
    def __init__(self, output_dir: str = "data/processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.headers = {
            "User-Agent": "brandon.hardison@gmail.com"
        }
        
        # SEC EDGAR base URL
        self.sec_base_url = "https://www.sec.gov"
        
        # Load company tickers for mapping
        self.company_tickers_file = Path("data/raw/sec/company_tickers.json")
        self.company_map = self.load_company_map()
    
    def load_company_map(self) -> Dict[str, Dict]:
        """Load company ticker to CIK mapping"""
        if self.company_tickers_file.exists():
            with open(self.company_tickers_file, 'r') as f:
                data = json.load(f)
            
            company_map = {}
            for key, value in data.items():
                cik = str(value['cik_str'])
                company_map[cik] = {
                    'ticker': value['ticker'],
                    'name': value['title'],
                    'cik': cik
                }
                # Also store without leading zeros
                company_map[str(int(cik))] = {
                    'ticker': value['ticker'],
                    'name': value['title'],
                    'cik': cik
                }
            return company_map
        return {}
    
    def get_company_info(self, cik: str) -> Dict:
        """Get company information from CIK"""
        normalized_cik = str(int(cik))
        return self.company_map.get(normalized_cik, self.company_map.get(cik, {'ticker': 'UNKNOWN', 'name': 'Unknown'}))
    
    def fetch_8k_filings(self, cik: str, days_back: int = 30) -> List[Dict]:
        """Fetch recent 8-K filings for a company"""
        logger.info(f"Fetching 8-K filings for CIK {cik}...")
        
        # Construct CIK with leading zeros (10 digits)
        padded_cik = cik.zfill(10)
        
        # SEC EDGAR API for company filings
        url = f"{self.sec_base_url}/cgi-bin/browse-edgar?action=getcompany&CIK={padded_cik}&type=8-K&dateb=&owner=exclude&count=100"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                filings = []
                # Parse the filing table
                table = soup.find('table', class_='tableFile2')
                if table:
                    rows = table.find_all('tr')[1:]  # Skip header row
                    
                    cutoff_date = datetime.now() - timedelta(days=days_back)
                    
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 4:
                            filing_date = cols[3].text.strip()
                            try:
                                filing_dt = datetime.strptime(filing_date, '%Y-%m-%d')
                                if filing_dt >= cutoff_date:
                                    filing_link = cols[1].find('a')
                                    if filing_link:
                                        accession_number = cols[2].text.strip()
                                        document_url = self.sec_base_url + filing_link['href']
                                        
                                        filings.append({
                                            'filing_date': filing_date,
                                            'accession_number': accession_number,
                                            'document_url': document_url
                                        })
                            except ValueError:
                                continue
                
                logger.info(f"Found {len(filings)} recent 8-K filings")
                return filings
            else:
                logger.error(f"Failed to fetch filings: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching 8-K filings: {e}")
            return []
    
    def fetch_filing_document(self, document_url: str) -> Optional[str]:
        """Fetch the actual filing document"""
        try:
            response = requests.get(document_url, headers=self.headers)
            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"Failed to fetch document: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching document: {e}")
            return None
    
    def extract_comments_section(self, content: str) -> Dict[str, str]:
        """Extract comments/explanatory sections from 8-K filing"""
        comments = {}
        
        # Common 8-K section patterns for comments/explanations
        comment_patterns = {
            'explanation': r'(?:EXPLANATION|Explanation|EXPLANATORY NOTE|Explanatory Note)',
            'description': r'(?:DESCRIPTION|Description of Event|DESCRIPTION OF EVENT)',
            'narrative': r'(?:NARRATIVE|Narrative Description|DETAILS)',
            'reasons': r'(?:REASONS|Reasons for|BASIS)',
            'background': r'(?:BACKGROUND|Background Information)',
            'discussion': r'(?:DISCUSSION|Management Discussion|EXPLANATION BY MANAGEMENT)',
            'summary': r'(?:SUMMARY|Executive Summary|EVENT SUMMARY)',
            'details': r'(?:DETAILS|Additional Details|SPECIFIC DETAILS)',
            'materiality': r'(?:MATERIALITY|Material Effect|MATERIAL IMPACT)'
        }
        
        for section_name, pattern in comment_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                start = match.start()
                # Extract text after the section header (up to 2000 characters)
                section_text = content[start:start+2000]
                # Clean up the text
                section_text = re.sub(r'\s+', ' ', section_text).strip()
                if len(section_text) > 50:  # Only keep substantial sections
                    comments[section_name] = section_text[:500]  # Preview
                    break
        
        # Also look for Item 1.01, Item 2.01, etc. which are common 8-K items
        item_patterns = {
            'item_1_01': r'Item\s+1\.01',
            'item_1_02': r'Item\s+1\.02',
            'item_2_01': r'Item\s+2\.01',
            'item_2_02': r'Item\s+2\.02',
            'item_2_03': r'Item\s+2\.03',
            'item_2_04': r'Item\s+2\.04',
            'item_2_05': r'Item\s+2\.05',
            'item_2_06': r'Item\s+2\.06',
            'item_7_01': r'Item\s+7\.01',
            'item_8_01': r'Item\s+8\.01',
            'item_9_01': r'Item\s+9\.01'
        }
        
        for item_name, pattern in item_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                start = match.start()
                section_text = content[start:start+1500]
                section_text = re.sub(r'\s+', ' ', section_text).strip()
                if len(section_text) > 50:
                    comments[item_name] = section_text[:400]
                    break
        
        return comments
    
    def extract_key_events(self, content: str) -> List[str]:
        """Extract key events mentioned in the 8-K filing"""
        events = []
        
        # Common event patterns in 8-K filings
        event_patterns = [
            r'(?:entered into|signed|executed).{0,100}(?:agreement|contract|deal)',
            r'(?:completed|closed|finalized).{0,100}(?:acquisition|merger|purchase)',
            r'(?:appointed|named|elected).{0,100}(?:CEO|director|officer|executive)',
            r'(?:resigned|stepped down|departed).{0,100}(?:CEO|director|officer)',
            r'(?:launched|introduced|announced).{0,100}(?:product|service|program)',
            r'(?:issued|declared).{0,100}(?:dividend|stock|shares)',
            r'(?:restated|revised|updated).{0,100}(?:financial|earnings|results)',
            r'(?:received|granted).{0,100}(?:approval|clearance|letter)',
            r'(?:terminated|ended|cancelled).{0,100}(?:agreement|contract|relationship)'
        ]
        
        for pattern in event_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                cleaned_match = re.sub(r'\s+', ' ', match).strip()
                if len(cleaned_match) > 20 and len(cleaned_match) < 200:
                    events.append(cleaned_match)
        
        # Return unique events (limit to 10)
        unique_events = list(set(events))[:10]
        return unique_events
    
    def process_company_8k_comments(self, cik: str, days_back: int = 30) -> List[Dict]:
        """Process all 8-K filings for a company and extract comments"""
        logger.info(f"Processing 8-K comments for CIK {cik}...")
        
        company_info = self.get_company_info(cik)
        filings = self.fetch_8k_filings(cik, days_back)
        
        processed_filings = []
        
        for filing in filings:
            logger.info(f"Processing filing {filing['accession_number']}...")
            
            # Fetch the document
            content = self.fetch_filing_document(filing['document_url'])
            if content:
                # Extract comments section
                comments = self.extract_comments_section(content)
                
                # Extract key events
                events = self.extract_key_events(content)
                
                filing_data = {
                    'ticker': company_info['ticker'],
                    'company_name': company_info['name'],
                    'cik': cik,
                    'filing_date': filing['filing_date'],
                    'accession_number': filing['accession_number'],
                    'document_url': filing['document_url'],
                    'comments_sections': comments,
                    'key_events': events,
                    'has_comments': len(comments) > 0,
                    'comment_count': len(comments),
                    'event_count': len(events),
                    'processed_at': datetime.now().isoformat()
                }
                
                processed_filings.append(filing_data)
        
        logger.info(f"Processed {len(processed_filings)} 8-K filings for {company_info['ticker']}")
        return processed_filings
    
    def save_company_comments(self, cik: str, filings_data: List[Dict]):
        """Save processed 8-K comments for a company"""
        company_info = self.get_company_info(cik)
        ticker = company_info['ticker']
        
        # Create company directory structure: data/processed/{ticker}/8k_comments
        company_dir = self.output_dir / ticker / "8k_comments"
        company_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        json_file = company_dir / f"{ticker}_8k_comments.json"
        with open(json_file, 'w') as f:
            json.dump(filings_data, f, indent=2)
        
        logger.info(f"Saved 8-K comments to {json_file}")
        
        # Also save as CSV for easier analysis
        if filings_data:
            # Flatten the data for CSV
            csv_data = []
            for filing in filings_data:
                row = {
                    'ticker': filing['ticker'],
                    'company_name': filing['company_name'],
                    'cik': filing['cik'],
                    'filing_date': filing['filing_date'],
                    'accession_number': filing['accession_number'],
                    'document_url': filing['document_url'],
                    'has_comments': filing['has_comments'],
                    'comment_count': filing['comment_count'],
                    'event_count': filing['event_count'],
                    'processed_at': filing['processed_at']
                }
                
                # Add comments sections as separate columns
                for section_name, section_text in filing['comments_sections'].items():
                    row[f'comment_{section_name}'] = section_text
                
                # Add events as a concatenated string
                row['key_events'] = '; '.join(filing['key_events'])
                
                csv_data.append(row)
            
            csv_file = company_dir / f"{ticker}_8k_comments.csv"
            df = pd.DataFrame(csv_data)
            df.to_csv(csv_file, index=False)
            logger.info(f"Saved 8-K comments CSV to {csv_file}")
    
    def compile_multiple_companies(self, cik_list: List[str], days_back: int = 30):
        """Compile 8-K comments for multiple companies"""
        logger.info(f"Compiling 8-K comments for {len(cik_list)} companies...")
        
        all_results = []
        
        for i, cik in enumerate(cik_list):
            logger.info(f"Processing company {i+1}/{len(cik_list)}: CIK {cik}")
            
            try:
                filings_data = self.process_company_8k_comments(cik, days_back)
                self.save_company_comments(cik, filings_data)
                all_results.extend(filings_data)
                
            except Exception as e:
                logger.error(f"Error processing company {cik}: {e}")
        
        # Create master compilation
        self.create_master_compilation(all_results)
        
        logger.info(f"Compilation complete. Total filings processed: {len(all_results)}")
    
    def create_master_compilation(self, all_results: List[Dict]):
        """Create master compilation of all 8-K comments"""
        if not all_results:
            logger.warning("No results to compile")
            return
        
        # Create master compilation directory
        master_dir = self.output_dir / "8k_master_compilation"
        master_dir.mkdir(parents=True, exist_ok=True)
        
        # Create master CSV
        csv_data = []
        for filing in all_results:
            row = {
                'ticker': filing['ticker'],
                'company_name': filing['company_name'],
                'cik': filing['cik'],
                'filing_date': filing['filing_date'],
                'accession_number': filing['accession_number'],
                'document_url': filing['document_url'],
                'has_comments': filing['has_comments'],
                'comment_count': filing['comment_count'],
                'event_count': filing['event_count'],
                'processed_at': filing['processed_at']
            }
            
            # Add comments sections
            for section_name, section_text in filing['comments_sections'].items():
                row[f'comment_{section_name}'] = section_text
            
            row['key_events'] = '; '.join(filing['key_events'])
            csv_data.append(row)
        
        master_df = pd.DataFrame(csv_data)
        master_file = master_dir / "master_8k_comments_compilation.csv"
        master_df.to_csv(master_file, index=False)
        logger.info(f"Saved master compilation to {master_file}")
        
        # Also save as JSON
        master_json = master_dir / "master_8k_comments_compilation.json"
        with open(master_json, 'w') as f:
            json.dump(all_results, f, indent=2)
        logger.info(f"Saved master JSON compilation to {master_json}")


def main():
    """Main execution function"""
    compiler = EightKCommentsCompiler()
    
    # Example: Process a few companies
    # You can specify CIKs or use from your asset list
    sample_ciks = [
        '320193',  # Apple
        '789019',   # Microsoft
        '1067983',  # Berkshire Hathaway
        '1652044',  # Netflix
        '1326801',  # Meta (Facebook)
    ]
    
    # Compile 8-K comments for the last 30 days
    compiler.compile_multiple_companies(sample_ciks, days_back=30)
    
    logger.info("8-K comments compilation completed")


if __name__ == "__main__":
    main()
