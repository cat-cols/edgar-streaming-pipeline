"""
Advanced Market Scanner with Financial Formulas
Scans market for potential buys using advanced financial metrics and formulas
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedMarketScanner:
    """Scan market using advanced financial formulas and metrics"""
    
    def __init__(self, prices_dir: str = "data/raw/prices", 
                 output_dir: str = "data/processed/market_scanner"):
        self.prices_dir = Path(prices_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_stock_data(self, ticker: str) -> Optional[Dict]:
        """Get comprehensive stock data from yfinance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get financial statements
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cash_flow
            
            return {
                'info': info,
                'financials': financials,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow
            }
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None
    
    def calculate_graham_number(self, data: Dict) -> Optional[float]:
        """Calculate Graham Number for value investing"""
        try:
            info = data['info']
            
            # Get EPS and Book Value per Share
            eps = info.get('trailingEps')
            book_value_per_share = info.get('bookValue')
            
            if eps and book_value_per_share and eps > 0 and book_value_per_share > 0:
                # Graham Number = sqrt(22.5 * EPS * Book Value per Share)
                graham_number = np.sqrt(22.5 * eps * book_value_per_share)
                return graham_number
            
        except Exception as e:
            logger.error(f"Error calculating Graham Number: {e}")
        
        return None
    
    def calculate_intrinsic_value_dcf(self, data: Dict, growth_rate: float = 0.05, 
                                     discount_rate: float = 0.10, years: int = 10) -> Optional[float]:
        """Calculate intrinsic value using Discounted Cash Flow (DCF)"""
        try:
            info = data['info']
            financials = data['financials']
            
            if financials is None or financials.empty:
                return None
            
            # Get Free Cash Flow (most recent year)
            try:
                # Operating Cash Flow - Capital Expenditures
                operating_cf = info.get('operatingCashflow')
                capex = info.get('capitalExpenditures')
                
                if operating_cf and capex:
                    fcf = operating_cf - abs(capex)
                else:
                    # Fallback to net income
                    fcf = info.get('netIncome')
                
                if not fcf or fcf <= 0:
                    return None
                
                # Get shares outstanding
                shares = info.get('sharesOutstanding')
                if not shares:
                    return None
                
                fcf_per_share = fcf / shares
                
                # Calculate terminal value
                terminal_growth = 0.03  # 3% terminal growth
                terminal_value = (fcf_per_share * (1 + growth_rate) ** years * (1 + terminal_growth)) / (discount_rate - terminal_growth)
                
                # Calculate present value of future cash flows
                pv_cash_flows = 0
                for year in range(1, years + 1):
                    future_fcf = fcf_per_share * (1 + growth_rate) ** year
                    pv = future_fcf / ((1 + discount_rate) ** year)
                    pv_cash_flows += pv
                
                # Total intrinsic value
                intrinsic_value = pv_cash_flows + (terminal_value / ((1 + discount_rate) ** years))
                
                return intrinsic_value
                
            except Exception as e:
                logger.error(f"Error in DCF calculation: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error calculating DCF: {e}")
            return None
    
    def calculate_piotroski_f_score(self, data: Dict) -> Optional[int]:
        """Calculate Piotroski F-Score for financial strength"""
        try:
            score = 0
            info = data['info']
            financials = data['financials']
            balance_sheet = data['balance_sheet']
            
            if financials is None or financials.empty or balance_sheet is None or balance_sheet.empty:
                return None
            
            # Profitability Signals (4 points)
            # Positive net income
            net_income = info.get('netIncome')
            if net_income and net_income > 0:
                score += 1
            
            # Positive operating cash flow
            operating_cf = info.get('operatingCashflow')
            if operating_cf and operating_cf > 0:
                score += 1
            
            # ROA increased
            roa = info.get('returnOnAssets')
            if roa and roa > 0:
                score += 1
            
            # Accruals (operating cash flow > net income)
            if operating_cf and net_income and operating_cf > net_income:
                score += 1
            
            # Leverage, Liquidity, and Source of Funds (3 points)
            # Current ratio increased
            current_ratio = info.get('currentRatio')
            if current_ratio and current_ratio > 2:
                score += 1
            
            # Debt decreased
            debt_to_equity = info.get('debtToEquity')
            if debt_to_equity and debt_to_equity < 1:
                score += 1
            
            # No new shares issued
            shares = info.get('sharesOutstanding')
            if shares:
                score += 1  # Simplified - would need historical data
            
            # Operating Efficiency (3 points)
            # Gross margin increased
            gross_margin = info.get('grossMargins')
            if gross_margin and gross_margin > 0.4:
                score += 1
            
            # Asset turnover increased
            asset_turnover = info.get('assetTurnover')
            if asset_turnover and asset_turnover > 0.5:
                score += 1
            
            # Inventory decreased
            # Simplified - would need historical data
            score += 1
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating Piotroski F-Score: {e}")
            return None
    
    def calculate_altman_z_score(self, data: Dict) -> Optional[float]:
        """Calculate Altman Z-Score for bankruptcy prediction"""
        try:
            info = data['info']
            balance_sheet = data['balance_sheet']
            
            if balance_sheet is None or balance_sheet.empty:
                return None
            
            # Get key financial ratios
            working_capital = info.get('totalCurrentAssets', 0) - info.get('totalCurrentLiabilities', 0)
            total_assets = info.get('totalAssets')
            retained_earnings = info.get('retainedEarnings')
            ebit = info.get('ebit') or info.get('operatingIncome')
            market_cap = info.get('marketCap')
            total_liabilities = info.get('totalLiabilities')
            sales = info.get('totalRevenue')
            
            if not all([working_capital, total_assets, retained_earnings, ebit, market_cap, total_liabilities, sales]):
                return None
            
            # Altman Z-Score formula
            # Z = 1.2X1 + 1.4X2 + 3.3X3 + 0.6X4 + 1.0X5
            X1 = working_capital / total_assets
            X2 = retained_earnings / total_assets
            X3 = ebit / total_assets
            X4 = market_cap / total_liabilities
            X5 = sales / total_assets
            
            z_score = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 1.0 * X5
            
            return z_score
            
        except Exception as e:
            logger.error(f"Error calculating Altman Z-Score: {e}")
            return None
    
    def calculate_ev_ebitda(self, data: Dict) -> Optional[float]:
        """Calculate EV/EBITDA ratio"""
        try:
            info = data['info']
            
            enterprise_value = info.get('enterpriseValue')
            ebitda = info.get('ebitda')
            
            if enterprise_value and ebitda and ebitda > 0:
                return enterprise_value / ebitda
            
        except Exception as e:
            logger.error(f"Error calculating EV/EBITDA: {e}")
        
        return None
    
    def calculate_price_to_sales(self, data: Dict) -> Optional[float]:
        """Calculate Price to Sales ratio"""
        try:
            info = data['info']
            
            market_cap = info.get('marketCap')
            revenue = info.get('totalRevenue')
            
            if market_cap and revenue and revenue > 0:
                return market_cap / revenue
            
        except Exception as e:
            logger.error(f"Error calculating P/S ratio: {e}")
        
        return None
    
    def calculate_advanced_score(self, ticker: str, data: Dict, current_price: float) -> Dict:
        """Calculate comprehensive advanced score using multiple formulas"""
        logger.info(f"Calculating advanced metrics for {ticker}...")
        
        metrics = {
            'ticker': ticker,
            'current_price': current_price,
            'analysis_date': datetime.now().isoformat()
        }
        
        # Calculate advanced metrics
        metrics['graham_number'] = self.calculate_graham_number(data)
        metrics['intrinsic_value_dcf'] = self.calculate_intrinsic_value_dcf(data)
        metrics['piotroski_f_score'] = self.calculate_piotroski_f_score(data)
        metrics['altman_z_score'] = self.calculate_altman_z_score(data)
        metrics['ev_ebitda'] = self.calculate_ev_ebitda(data)
        metrics['price_to_sales'] = self.calculate_price_to_sales(data)
        
        # Calculate value scores
        metrics['value_scores'] = self.calculate_value_scores(metrics, current_price)
        
        # Calculate overall advanced score
        metrics['advanced_score'] = self.calculate_overall_advanced_score(metrics)
        
        return metrics
    
    def calculate_value_scores(self, metrics: Dict, current_price: float) -> Dict:
        """Calculate individual value scores based on advanced metrics"""
        scores = {}
        
        # Graham Number score
        graham_number = metrics.get('graham_number')
        if graham_number:
            if current_price < graham_number * 0.7:  # Significant discount
                scores['graham_score'] = 100
            elif current_price < graham_number:
                scores['graham_score'] = 75
            else:
                scores['graham_score'] = 25
        
        # DCF score
        intrinsic_value = metrics.get('intrinsic_value_dcf')
        if intrinsic_value:
            discount = (intrinsic_value - current_price) / intrinsic_value
            if discount > 0.30:  # 30%+ discount
                scores['dcf_score'] = 100
            elif discount > 0.15:  # 15%+ discount
                scores['dcf_score'] = 75
            elif discount > 0:
                scores['dcf_score'] = 50
            else:
                scores['dcf_score'] = 0
        
        # Piotroski F-Score
        f_score = metrics.get('piotroski_f_score')
        if f_score:
            if f_score >= 8:
                scores['piotroski_score'] = 100
            elif f_score >= 6:
                scores['piotroski_score'] = 75
            elif f_score >= 4:
                scores['piotroski_score'] = 50
            else:
                scores['piotroski_score'] = 25
        
        # Altman Z-Score
        z_score = metrics.get('altman_z_score')
        if z_score:
            if z_score > 3:  # Safe zone
                scores['altman_score'] = 100
            elif z_score > 1.8:  # Grey zone
                scores['altman_score'] = 50
            else:  # Distress zone
                scores['altman_score'] = 0
        
        # EV/EBITDA score
        ev_ebitda = metrics.get('ev_ebitda')
        if ev_ebitda:
            if ev_ebitda < 8:  # Undervalued
                scores['ev_ebitda_score'] = 100
            elif ev_ebitda < 12:  # Reasonable
                scores['ev_ebitda_score'] = 75
            elif ev_ebitda < 16:  # Fair
                scores['ev_ebitda_score'] = 50
            else:  # Overvalued
                scores['ev_ebitda_score'] = 25
        
        return scores
    
    def calculate_overall_advanced_score(self, metrics: Dict) -> Dict:
        """Calculate overall advanced score and recommendation"""
        value_scores = metrics.get('value_scores', {})
        
        # Calculate weighted average
        weights = {
            'graham_score': 0.20,
            'dcf_score': 0.25,
            'piotroski_score': 0.20,
            'altman_score': 0.20,
            'ev_ebitda_score': 0.15
        }
        
        total_score = 0
        total_weight = 0
        
        for score_name, weight in weights.items():
            if score_name in value_scores:
                total_score += value_scores[score_name] * weight
                total_weight += weight
        
        if total_weight > 0:
            overall_score = total_score / total_weight
        else:
            overall_score = 50  # Neutral if no scores available
        
        # Determine recommendation
        if overall_score >= 80:
            recommendation = "Strong Buy"
        elif overall_score >= 70:
            recommendation = "Buy"
        elif overall_score >= 60:
            recommendation = "Hold"
        elif overall_score >= 40:
            recommendation = "Sell"
        else:
            recommendation = "Strong Sell"
        
        return {
            'overall_score': round(overall_score, 2),
            'recommendation': recommendation,
            'confidence': 'High' if len(value_scores) >= 4 else 'Low'
        }
    
    def scan_stock(self, ticker: str) -> Optional[Dict]:
        """Scan a single stock using advanced formulas"""
        logger.info(f"Scanning {ticker}...")
        
        # Get current price
        try:
            stock = yf.Ticker(ticker)
            current_price = stock.info.get('currentPrice') or stock.info.get('regularMarketPrice')
            if not current_price:
                return None
        except:
            return None
        
        # Get comprehensive data
        data = self.get_stock_data(ticker)
        if not data:
            return None
        
        # Calculate advanced metrics
        metrics = self.calculate_advanced_score(ticker, data, current_price)
        
        logger.info(f"Scan complete for {ticker}: {metrics['advanced_score']['recommendation']}")
        return metrics
    
    def scan_market(self, sample_size: Optional[int] = None) -> List[Dict]:
        """Scan market for potential buys using advanced formulas"""
        logger.info("Starting advanced market scan...")
        
        # Get stocks with price data
        tickers = []
        for ticker_dir in self.prices_dir.iterdir():
            if ticker_dir.is_dir() and ticker_dir.name not in ['processed_stocks.json', 'fetching_summary.txt', 'price_data_index.csv']:
                tickers.append(ticker_dir.name)
        
        if sample_size:
            tickers = tickers[:sample_size]
            logger.info(f"Scanning sample of {sample_size} stocks")
        
        results = []
        for i, ticker in enumerate(tickers):
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{len(tickers)} stocks scanned")
            
            scan_result = self.scan_stock(ticker)
            if scan_result:
                results.append(scan_result)
        
        logger.info(f"Market scan complete: {len(results)} stocks analyzed")
        return results
    
    def save_scan_results(self, results: List[Dict]):
        """Save scan results to files"""
        if not results:
            logger.warning("No scan results to save")
            return
        
        # Save as JSON
        json_file = self.output_dir / "advanced_scan_results.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Saved scan results to {json_file}")
        
        # Save as CSV (summary)
        summary_data = []
        for result in results:
            summary = {
                'ticker': result['ticker'],
                'current_price': result['current_price'],
                'graham_number': result.get('graham_number'),
                'intrinsic_value_dcf': result.get('intrinsic_value_dcf'),
                'piotroski_f_score': result.get('piotroski_f_score'),
                'altman_z_score': result.get('altman_z_score'),
                'ev_ebitda': result.get('ev_ebitda'),
                'overall_score': result['advanced_score']['overall_score'],
                'recommendation': result['advanced_score']['recommendation']
            }
            summary_data.append(summary)
        
        summary_df = pd.DataFrame(summary_data)
        csv_file = self.output_dir / "advanced_scan_summary.csv"
        summary_df.to_csv(csv_file, index=False)
        
        logger.info(f"Saved scan summary to {csv_file}")
        
        # Create potential buys list
        self.create_potential_buys_list(summary_df)
    
    def create_potential_buys_list(self, summary_df: pd.DataFrame):
        """Create list of potential buys based on advanced analysis"""
        # Filter for buy recommendations
        potential_buys = summary_df[summary_df['recommendation'].isin(['Strong Buy', 'Buy'])]
        
        # Sort by overall score
        potential_buys = potential_buys.sort_values('overall_score', ascending=False)
        
        # Save potential buys list
        buys_file = self.output_dir / "potential_buys_list.csv"
        potential_buys.to_csv(buys_file, index=False)
        
        logger.info(f"Saved potential buys list to {buys_file}")
        logger.info(f"Found {len(potential_buys)} potential buys")
        
        # Create detailed report
        report = []
        report.append("=" * 80)
        report.append("ADVANCED MARKET SCAN - POTENTIAL BUYS")
        report.append("=" * 80)
        report.append(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Potential Buys: {len(potential_buys)}")
        report.append("")
        
        for _, row in potential_buys.head(20).iterrows():
            report.append(f"{row['ticker']}: {row['recommendation']} (Score: {row['overall_score']})")
            report.append(f"  Price: ${row['current_price']:.2f}")
            report.append(f"  Graham Number: ${row['graham_number']:.2f}" if pd.notna(row['graham_number']) else "  Graham Number: N/A")
            report.append(f"  DCF Value: ${row['intrinsic_value_dcf']:.2f}" if pd.notna(row['intrinsic_value_dcf']) else "  DCF Value: N/A")
            report.append(f"  Piotroski F-Score: {row['piotroski_f_score']}" if pd.notna(row['piotroski_f_score']) else "  Piotroski F-Score: N/A")
            report.append(f"  Altman Z-Score: {row['altman_z_score']:.2f}" if pd.notna(row['altman_z_score']) else "  Altman Z-Score: N/A")
            report.append("")
        
        report_text = "\n".join(report)
        
        report_file = self.output_dir / "potential_buys_report.txt"
        with open(report_file, 'w') as f:
            f.write(report_text)
        
        logger.info(f"Saved potential buys report to {report_file}")


def main():
    """Main execution function"""
    scanner = AdvancedMarketScanner()
    
    # Scan market with advanced formulas
    logger.info("Starting advanced market scan...")
    
    # Scan sample of stocks
    results = scanner.scan_market(sample_size=15)
    
    # Save results
    scanner.save_scan_results(results)
    
    logger.info("Advanced market scan completed")


if __name__ == "__main__":
    main()
