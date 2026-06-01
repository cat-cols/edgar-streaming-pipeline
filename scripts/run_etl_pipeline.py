"""
Unified ETL Pipeline for Financial Data Ingestion
Orchestrates all data ingestion scripts in proper sequence
"""

import subprocess
import sys
import logging
from datetime import datetime
from pathlib import Path
import json
import os

# Create logs directory
logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'etl_pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """Unified ETL pipeline for financial data ingestion"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        self.pipeline_config = {
            'steps': [
                {
                    'name': 'SEC Data Ingestion',
                    'script': 'ingest_sec_data.py',
                    'required': True,
                    'description': 'Ingest company tickers and ETF data from SEC EDGAR API'
                },
                {
                    'name': 'SEC Filing Monitoring',
                    'script': 'monitor_filings.py',
                    'required': False,
                    'description': 'Monitor and download new SEC filings'
                },
                {
                    'name': 'Filing Analysis',
                    'script': 'analyze_company_filings.py',
                    'required': False,
                    'description': 'Analyze and organize SEC filings by company'
                },
                {
                    'name': 'Historical Price Fetching',
                    'script': 'fetch_historical_prices.py',
                    'required': True,
                    'description': 'Fetch historical price data for all stocks'
                },
                {
                    'name': 'Stock Valuation',
                    'script': 'stock_valuation.py',
                    'required': False,
                    'description': 'Calculate stock valuation metrics'
                },
                {
                    'name': 'Market Scanning',
                    'script': 'advanced_market_scanner.py',
                    'required': False,
                    'description': 'Scan market for potential investment opportunities'
                }
            ],
            'max_retries': 2,
            'timeout_seconds': 3600
        }
        
        self.results = {
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'status': 'running',
            'steps': [],
            'errors': []
        }
    
    def run_script(self, script_name: str, step_config: dict) -> dict:
        """Run a single script and return results"""
        script_path = self.scripts_dir / script_name
        step_result = {
            'name': step_config['name'],
            'script': script_name,
            'status': 'pending',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'output': '',
            'error': None,
            'required': step_config['required']
        }
        
        if not script_path.exists():
            error_msg = f"Script not found: {script_path}"
            logger.error(error_msg)
            step_result['status'] = 'failed'
            step_result['error'] = error_msg
            step_result['end_time'] = datetime.now().isoformat()
            return step_result
        
        try:
            logger.info(f"Running step: {step_config['name']} ({script_name})")
            step_result['status'] = 'running'
            
            # Run the script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=self.pipeline_config['timeout_seconds']
            )
            
            step_result['output'] = result.stdout
            step_result['end_time'] = datetime.now().isoformat()
            
            if result.returncode == 0:
                step_result['status'] = 'completed'
                logger.info(f"Step completed successfully: {step_config['name']}")
            else:
                step_result['status'] = 'failed'
                step_result['error'] = result.stderr
                logger.error(f"Step failed: {step_config['name']}")
                logger.error(f"Error output: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            error_msg = f"Script timeout after {self.pipeline_config['timeout_seconds']} seconds"
            logger.error(error_msg)
            step_result['status'] = 'failed'
            step_result['error'] = error_msg
            step_result['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            step_result['status'] = 'failed'
            step_result['error'] = error_msg
            step_result['end_time'] = datetime.now().isoformat()
        
        return step_result
    
    def run_pipeline(self):
        """Run the complete ETL pipeline"""
        logger.info("=" * 80)
        logger.info("Starting ETL Pipeline")
        logger.info("=" * 80)
        
        completed_steps = 0
        failed_required_steps = 0
        
        for step_config in self.pipeline_config['steps']:
            step_result = self.run_script(step_config['script'], step_config)
            self.results['steps'].append(step_result)
            
            if step_result['status'] == 'completed':
                completed_steps += 1
            elif step_result['status'] == 'failed' and step_result['required']:
                failed_required_steps += 1
                self.results['errors'].append({
                    'step': step_config['name'],
                    'error': step_result['error']
                })
            
            # Log progress
            progress = (completed_steps / len(self.pipeline_config['steps'])) * 100
            logger.info(f"Pipeline progress: {progress:.1f}% ({completed_steps}/{len(self.pipeline_config['steps'])} steps completed)")
        
        # Determine overall status
        self.results['end_time'] = datetime.now().isoformat()
        
        if failed_required_steps > 0:
            self.results['status'] = 'failed'
            logger.error(f"Pipeline failed: {failed_required_steps} required steps failed")
        elif completed_steps == len(self.pipeline_config['steps']):
            self.results['status'] = 'completed'
            logger.info("Pipeline completed successfully")
        else:
            self.results['status'] = 'partial'
            logger.warning(f"Pipeline partially completed: {completed_steps}/{len(self.pipeline_config['steps'])} steps")
        
        # Save results
        self.save_results()
        
        return self.results['status'] == 'completed'
    
    def save_results(self):
        """Save pipeline execution results"""
        results_file = self.logs_dir / f"etl_pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Pipeline results saved to {results_file}")
        
        # Also save latest results
        latest_file = self.logs_dir / "etl_pipeline_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def generate_report(self):
        """Generate human-readable pipeline report"""
        report = []
        report.append("=" * 80)
        report.append("ETL PIPELINE EXECUTION REPORT")
        report.append("=" * 80)
        report.append(f"Start Time: {self.results['start_time']}")
        report.append(f"End Time: {self.results['end_time']}")
        report.append(f"Overall Status: {self.results['status'].upper()}")
        report.append("")
        
        report.append("STEP DETAILS:")
        report.append("-" * 80)
        
        for step in self.results['steps']:
            report.append(f"{step['name']}: {step['status'].upper()}")
            report.append(f"  Script: {step['script']}")
            report.append(f"  Required: {step['required']}")
            if step['error']:
                report.append(f"  Error: {step['error']}")
            report.append("")
        
        if self.results['errors']:
            report.append("ERRORS:")
            report.append("-" * 80)
            for error in self.results['errors']:
                report.append(f"{error['step']}: {error['error']}")
            report.append("")
        
        report.append("=" * 80)
        
        report_text = "\n".join(report)
        
        # Save report
        report_file = self.logs_dir / f"etl_pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report_text)
        
        logger.info(f"Pipeline report saved to {report_file}")
        
        return report_text


def main():
    """Main execution function"""
    pipeline = ETLPipeline()
    
    try:
        success = pipeline.run_pipeline()
        report = pipeline.generate_report()
        
        print("\n" + report)
        
        if success:
            logger.info("ETL Pipeline completed successfully")
            sys.exit(0)
        else:
            logger.error("ETL Pipeline failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
