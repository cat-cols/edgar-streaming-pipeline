"""
SEC Filing Analysis Script
Organizes filings by company and creates human-readable analysis reports
"""

import json
import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompanyFilingAnalyzer:
    """Analyze and organize SEC filings by company for human-readable reports"""
    
    def __init__(self, filings_dir: str = "data/raw/sec/filings", 
                 output_dir: str = "data/processed/companies"):
        self.filings_dir = Path(filings_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
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
                # Store with both leading zeros and without for flexibility
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
    
    def get_company_filings(self, cik: str) -> Dict[str, List[Path]]:
        """Get all filings for a specific company organized by type"""
        company_filings = {}
        
        # Normalize CIK (remove leading zeros for lookup)
        normalized_cik = str(int(cik))
        
        # Search through filing types
        for form_type_dir in self.filings_dir.iterdir():
            if form_type_dir.is_dir():
                cik_dir = form_type_dir / cik
                if cik_dir.exists():
                    filings = list(cik_dir.glob("*.txt"))
                    if filings:
                        company_filings[form_type_dir.name] = filings
        
        return company_filings
    
    def parse_filing_content(self, filing_path: Path) -> Dict:
        """Parse filing content to extract key information"""
        try:
            with open(filing_path, 'r') as f:
                content = f.read()
            
            # Extract key sections based on filing type
            filing_info = {
                'path': str(filing_path),
                'form_type': filing_path.parent.parent.name,
                'accession_number': filing_path.stem,
                'file_size': len(content),
                'content_preview': content[:500] if len(content) > 500 else content
            }
            
            # Extract common SEC filing sections
            sections = self.extract_sections(content)
            filing_info['sections'] = sections
            
            # Extract financial metrics if available
            metrics = self.extract_financial_metrics(content)
            filing_info['metrics'] = metrics
            
            # Extract risk factors if available
            risks = self.extract_risk_factors(content)
            filing_info['risks'] = risks
            
            return filing_info
            
        except Exception as e:
            logger.error(f"Error parsing filing {filing_path}: {e}")
            return {}
    
    def extract_sections(self, content: str) -> Dict[str, str]:
        """Extract common SEC filing sections"""
        sections = {}
        
        # Common section headers
        section_patterns = {
            'business': r'(?:BUSINESS|Item 1\. Business)',
            'risk_factors': r'(?:RISK FACTORS|Item 1A\. Risk Factors)',
            'financial_statements': r'(?:FINANCIAL STATEMENTS|Item 8\. Financial Statements)',
            'management_discussion': r'(?:MANAGEMENT\'S DISCUSSION|Item 7\. Management\'s Discussion)',
            'legal_proceedings': r'(?:LEGAL PROCEEDINGS|Item 3\. Legal Proceedings)',
            'market_for_securities': r'(?:MARKET FOR|Item 5\. Market for Registrant\'s Common Equity)'
        }
        
        for section_name, pattern in section_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                start = match.start()
                # Get text around the section (simplified)
                section_text = content[start:start+1000]
                sections[section_name] = section_text[:200]  # Preview
                break
        
        return sections
    
    def extract_financial_metrics(self, content: str) -> Dict[str, str]:
        """Extract key financial metrics from filing content"""
        metrics = {}
        
        # Look for common financial patterns
        patterns = {
            'revenue': r'(?:total revenue|net revenue|revenue)[\s:]*\$?[\d,]+\.?\d*\s*(?:million|billion)?',
            'net_income': r'(?:net income|net earnings)[\s:]*\$?[\d,]+\.?\d*\s*(?:million|billion)?',
            'total_assets': r'(?:total assets)[\s:]*\$?[\d,]+\.?\d*\s*(?:million|billion)?',
            'total_liabilities': r'(?:total liabilities)[\s:]*\$?[\d,]+\.?\d*\s*(?:million|billion)?',
            'cash_equivalents': r'(?:cash and cash equivalents|cash equivalents)[\s:]*\$?[\d,]+\.?\d*\s*(?:million|billion)?'
        }
        
        for metric_name, pattern in patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                metrics[metric_name] = matches[0]
        
        return metrics
    
    def extract_risk_factors(self, content: str) -> List[str]:
        """Extract risk factors from filing content"""
        risks = []
        
        # Look for risk factor patterns
        risk_pattern = r'(?:risk|risks|concern|challenge|uncertainty)[^\.]*\.'
        matches = re.findall(risk_pattern, content, re.IGNORECASE)
        
        # Get unique risks (limit to top 10)
        unique_risks = list(set(matches))[:10]
        risks = unique_risks
        
        return risks
    
    def organize_company_filings(self, cik: str) -> Dict:
        """Organize all filings for a company into a structured format"""
        logger.info(f"Organizing filings for company CIK {cik}...")
        
        # Normalize CIK for lookup (remove leading zeros)
        normalized_cik = str(int(cik))
        
        # Try both normalized and original CIK for lookup
        company_info = self.company_map.get(normalized_cik)
        if not company_info:
            company_info = self.company_map.get(cik)
        if not company_info:
            company_info = {'cik': cik, 'name': 'Unknown', 'ticker': 'Unknown'}
            logger.warning(f"Company CIK {cik} (normalized: {normalized_cik}) not found in company map")
        
        # Get all filings for this company
        company_filings = self.get_company_filings(cik)
        
        # Parse each filing
        parsed_filings = {}
        for form_type, filing_paths in company_filings.items():
            parsed_filings[form_type] = []
            for filing_path in filing_paths:
                filing_info = self.parse_filing_content(filing_path)
                if filing_info:
                    parsed_filings[form_type].append(filing_info)
        
        # Create company summary
        company_summary = {
            'company_info': company_info,
            'total_filings': sum(len(filings) for filings in parsed_filings.values()),
            'filings_by_type': {form_type: len(filings) for form_type, filings in parsed_filings.items()},
            'filings': parsed_filings,
            'last_updated': datetime.now().isoformat()
        }
        
        return company_summary
    
    def create_company_report(self, cik: str) -> str:
        """Create human-readable report for a company"""
        company_summary = self.organize_company_filings(cik)
        
        company_info = company_summary['company_info']
        
        # Build report
        report = []
        report.append("=" * 80)
        report.append(f"SEC FILING ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Company: {company_info['name']} ({company_info['ticker']})")
        report.append(f"CIK: {company_info['cik']}")
        report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("FILING SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Filings: {company_summary['total_filings']}")
        report.append("")
        report.append("Filings by Type:")
        for form_type, count in company_summary['filings_by_type'].items():
            report.append(f"  {form_type}: {count} filings")
        report.append("")
        
        # Detailed filing analysis
        report.append("RECENT FILINGS ANALYSIS")
        report.append("-" * 80)
        
        for form_type, filings in company_summary['filings'].items():
            if filings:
                report.append(f"\n{form_type} Filings:")
                report.append("-" * 40)
                
                for filing in filings[-3:]:  # Show last 3 filings
                    report.append(f"\n  Accession: {filing['accession_number']}")
                    report.append(f"  File Size: {filing['file_size']:,} bytes")
                    
                    # Show sections found
                    if filing.get('sections'):
                        report.append(f"  Sections Found: {', '.join(filing['sections'].keys())}")
                    
                    # Show financial metrics
                    if filing.get('metrics'):
                        report.append(f"  Financial Metrics:")
                        for metric, value in filing['metrics'].items():
                            report.append(f"    {metric}: {value}")
                    
                    # Show risk factors
                    if filing.get('risks'):
                        report.append(f"  Key Risk Factors:")
                        for risk in filing['risks'][:3]:
                            report.append(f"    - {risk}")
        
        report.append("")
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_company_report(self, cik: str, report: str):
        """Save company report to file"""
        # Normalize CIK for lookup
        normalized_cik = str(int(cik))
        company_info = self.company_map.get(normalized_cik, self.company_map.get(cik, {'ticker': 'UNKNOWN'}))
        ticker = company_info.get('ticker', 'UNKNOWN')
        
        # Debug logging
        if ticker == 'UNKNOWN':
            logger.warning(f"Could not find ticker for CIK {cik} (normalized: {normalized_cik})")
        else:
            logger.info(f"Found ticker {ticker} for CIK {cik}")
        
        # Create company directory
        company_dir = self.output_dir / ticker
        company_dir.mkdir(parents=True, exist_ok=True)
        
        # Save report
        report_file = company_dir / f"{ticker}_filing_analysis.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Saved company report to {report_file}")
        
        # Also save JSON summary
        summary_file = company_dir / f"{ticker}_filing_summary.json"
        company_summary = self.organize_company_filings(cik)
        with open(summary_file, 'w') as f:
            json.dump(company_summary, f, indent=2)
        
        logger.info(f"Saved company summary to {summary_file}")
    
    def analyze_all_companies(self, limit: Optional[int] = None):
        """Analyze all companies with filings"""
        logger.info("Analyzing all companies with filings...")
        
        # Get all unique CIKs from filings
        ciks = set()
        for form_type_dir in self.filings_dir.iterdir():
            if form_type_dir.is_dir():
                for cik_dir in form_type_dir.iterdir():
                    if cik_dir.is_dir():
                        ciks.add(cik_dir.name)
        
        logger.info(f"Found {len(ciks)} companies with filings")
        
        if limit:
            ciks = list(ciks)[:limit]
            logger.info(f"Analyzing first {limit} companies")
        
        analyzed_count = 0
        for cik in ciks:
            try:
                report = self.create_company_report(cik)
                self.save_company_report(cik, report)
                analyzed_count += 1
                
                if analyzed_count % 10 == 0:
                    logger.info(f"Analyzed {analyzed_count}/{len(ciks)} companies")
                    
            except Exception as e:
                logger.error(f"Error analyzing company {cik}: {e}")
        
        logger.info(f"Completed analysis of {analyzed_count} companies")
    
    def create_master_index(self):
        """Create master index of all company analyses"""
        logger.info("Creating master index of company analyses...")
        
        index_data = []
        
        for company_dir in self.output_dir.iterdir():
            if company_dir.is_dir():
                summary_file = company_dir / f"{company_dir.name}_filing_summary.json"
                if summary_file.exists():
                    with open(summary_file, 'r') as f:
                        summary = json.load(f)
                    
                    company_info = summary['company_info']
                    index_data.append({
                        'ticker': company_info['ticker'],
                        'name': company_info['name'],
                        'cik': company_info['cik'],
                        'total_filings': summary['total_filings'],
                        'last_updated': summary['last_updated']
                    })
        
        # Save index
        index_df = pd.DataFrame(index_data)
        index_file = self.output_dir / "company_analysis_index.csv"
        index_df.to_csv(index_file, index=False)
        
        logger.info(f"Saved master index to {index_file}")
        logger.info(f"Total companies analyzed: {len(index_data)}")


def main():
    """Main execution function"""
    analyzer = CompanyFilingAnalyzer()
    
    # Analyze all companies (limit to 10 for testing)
    analyzer.analyze_all_companies(limit=10)
    
    # Create master index
    analyzer.create_master_index()
    
    logger.info("Company filing analysis completed")


if __name__ == "__main__":
    main()
