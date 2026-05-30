"""
Stock Valuation Analysis Script
Calculates investment worthiness using market prices and fundamental analysis
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


class StockValuationAnalyzer:
    """Analyze stocks for investment worthiness using fundamental analysis"""

    def __init__(self, prices_dir: str = "data/raw/prices",
                 output_dir: str = "data/processed/valuation"):
        self.prices_dir = Path(prices_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Valuation thresholds
        self.thresholds = {
            'pe_ratio': {'undervalued': 15, 'overvalued': 25},
            'pb_ratio': {'undervalued': 1.5, 'overvalued': 3.0},
            'ps_ratio': {'undervalued': 2.0, 'overvalued': 5.0},
            'ev_ebitda': {'undervalued': 10, 'overvalued': 15},
            'roe': {'good': 0.15, 'excellent': 0.20},
            'debt_to_equity': {'safe': 1.0, 'risky': 2.0},
            'current_ratio': {'good': 2.0, 'poor': 1.0},
            'profit_margin': {'good': 0.10, 'excellent': 0.20}
        }

    def get_current_price(self, ticker: str) -> Optional[float]:
        """Get current market price for a stock"""
        try:
            price_file = self.prices_dir / ticker / f"{ticker}_prices.csv"
            if price_file.exists():
                df = pd.read_csv(price_file)
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date')
                return df.iloc[-1]['Close']
        except Exception as e:
            logger.error(f"Error reading price data for {ticker}: {e}")
        
        # Fallback to yfinance
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return info.get('currentPrice') or info.get('regularMarketPrice')
        except Exception as e:
            logger.error(f"Error fetching current price for {ticker}: {e}")
            return None
    
    def get_fundamental_data(self, ticker: str) -> Optional[Dict]:
        """Get fundamental data from yfinance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            fundamental_data = {
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE') or info.get('forwardPE'),
                'pb_ratio': info.get('priceToBook'),
                'ps_ratio': info.get('priceToSalesTrailing12Months'),
                'ev_ebitda': info.get('enterpriseToEbitda'),
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                'beta': info.get('beta'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'analyst_rating': info.get('recommendationKey'),
                'target_price': info.get('targetMeanPrice'),
                'number_of_analysts': info.get('numberOfAnalystsOpining')
            }
            
            return fundamental_data
            
        except Exception as e:
            logger.error(f"Error fetching fundamental data for {ticker}: {e}")
            return None
    
    def calculate_valuation_metrics(self, ticker: str, current_price: float, 
                                   fundamental_data: Dict) -> Dict:
        """Calculate comprehensive valuation metrics"""
        metrics = {
            'ticker': ticker,
            'current_price': current_price,
            'analysis_date': datetime.now().isoformat()
        }
        
        # Add fundamental data
        metrics.update(fundamental_data)
        
        # Calculate valuation scores
        metrics['valuation_scores'] = self.calculate_valuation_scores(fundamental_data)
        
        # Calculate distance from 52-week high/low
        if fundamental_data.get('52_week_high') and fundamental_data.get('52_week_low'):
            high = fundamental_data['52_week_high']
            low = fundamental_data['52_week_low']
            metrics['distance_from_high'] = (high - current_price) / high * 100
            metrics['distance_from_low'] = (current_price - low) / low * 100
            metrics['position_in_range'] = (current_price - low) / (high - low) * 100
        
        # Calculate intrinsic value (simplified DCF)
        metrics['intrinsic_value'] = self.calculate_intrinsic_value(fundamental_data)
        if metrics['intrinsic_value']:
            metrics['discount_to_intrinsic'] = (metrics['intrinsic_value'] - current_price) / metrics['intrinsic_value'] * 100
        
        # Calculate overall investment score
        metrics['investment_score'] = self.calculate_investment_score(metrics)
        
        return metrics
    
    def calculate_valuation_scores(self, fundamental_data: Dict) -> Dict:
        """Calculate individual valuation scores"""
        scores = {}
        
        # P/E Ratio Score
        pe = fundamental_data.get('pe_ratio')
        if pe:
            if pe < self.thresholds['pe_ratio']['undervalued']:
                scores['pe_score'] = 100
            elif pe < self.thresholds['pe_ratio']['overvalued']:
                scores['pe_score'] = 50
            else:
                scores['pe_score'] = 0
        
        # P/B Ratio Score
        pb = fundamental_data.get('pb_ratio')
        if pb:
            if pb < self.thresholds['pb_ratio']['undervalued']:
                scores['pb_score'] = 100
            elif pb < self.thresholds['pb_ratio']['overvalued']:
                scores['pb_score'] = 50
            else:
                scores['pb_score'] = 0
        
        # ROE Score
        roe = fundamental_data.get('roe')
        if roe:
            if roe > self.thresholds['roe']['excellent']:
                scores['roe_score'] = 100
            elif roe > self.thresholds['roe']['good']:
                scores['roe_score'] = 75
            else:
                scores['roe_score'] = 50
        
        # Debt/Equity Score
        d_e = fundamental_data.get('debt_to_equity')
        if d_e:
            if d_e < self.thresholds['debt_to_equity']['safe']:
                scores['debt_score'] = 100
            elif d_e < self.thresholds['debt_to_equity']['risky']:
                scores['debt_score'] = 50
            else:
                scores['debt_score'] = 0
        
        # Profit Margin Score
        pm = fundamental_data.get('profit_margin')
        if pm:
            if pm > self.thresholds['profit_margin']['excellent']:
                scores['margin_score'] = 100
            elif pm > self.thresholds['profit_margin']['good']:
                scores['margin_score'] = 75
            else:
                scores['margin_score'] = 50
        
        return scores
    
    def calculate_intrinsic_value(self, fundamental_data: Dict) -> Optional[float]:
        """Calculate intrinsic value using simplified DCF"""
        try:
            # Simplified DCF calculation
            current_price = fundamental_data.get('currentPrice') or 0
            pe_ratio = fundamental_data.get('pe_ratio') or 20
            earnings_growth = fundamental_data.get('earnings_growth') or 0.05
            
            if current_price and pe_ratio:
                # Estimate earnings per share
                eps = current_price / pe_ratio
                
                # Project future earnings (5 years)
                future_eps = eps * (1 + earnings_growth) ** 5
                
                # Apply conservative P/E multiple
                future_pe = min(pe_ratio * 0.8, 15)  # Conservative multiple
                
                # Calculate intrinsic value
                intrinsic_value = future_eps * future_pe
                
                return intrinsic_value
                
        except Exception as e:
            logger.error(f"Error calculating intrinsic value: {e}")
        
        return None
    
    def calculate_investment_score(self, metrics: Dict) -> Dict:
        """Calculate overall investment score and recommendation"""
        valuation_scores = metrics.get('valuation_scores', {})
        
        # Calculate weighted average score
        weights = {
            'pe_score': 0.25,
            'pb_score': 0.15,
            'roe_score': 0.20,
            'debt_score': 0.15,
            'margin_score': 0.15,
            'growth_score': 0.10
        }
        
        total_score = 0
        total_weight = 0
        
        for score_name, weight in weights.items():
            if score_name in valuation_scores:
                total_score += valuation_scores[score_name] * weight
                total_weight += weight
        
        if total_weight > 0:
            overall_score = total_score / total_weight
        else:
            overall_score = 50  # Neutral if no scores available
        
        # Add discount to intrinsic value bonus
        if metrics.get('discount_to_intrinsic'):
            discount = metrics['discount_to_intrinsic']
            if discount > 20:
                overall_score += 15
            elif discount > 10:
                overall_score += 10
            elif discount > 0:
                overall_score += 5
        
        # Cap score at 100
        overall_score = min(overall_score, 100)
        
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
            'confidence': 'High' if len(valuation_scores) >= 4 else 'Low'
        }
    
    def analyze_stock(self, ticker: str) -> Optional[Dict]:
        """Perform comprehensive stock analysis"""
        logger.info(f"Analyzing {ticker}...")
        
        # Get current price
        current_price = self.get_current_price(ticker)
        if not current_price:
            logger.warning(f"Could not get current price for {ticker}")
            return None
        
        # Get fundamental data
        fundamental_data = self.get_fundamental_data(ticker)
        if not fundamental_data:
            logger.warning(f"Could not get fundamental data for {ticker}")
            return None
        
        # Calculate valuation metrics
        metrics = self.calculate_valuation_metrics(ticker, current_price, fundamental_data)
        
        logger.info(f"Analysis complete for {ticker}: {metrics['investment_score']['recommendation']}")
        return metrics
    
    def analyze_multiple_stocks(self, tickers: List[str]) -> List[Dict]:
        """Analyze multiple stocks"""
        logger.info(f"Analyzing {len(tickers)} stocks...")
        
        results = []
        for i, ticker in enumerate(tickers):
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{len(tickers)} stocks analyzed")
            
            analysis = self.analyze_stock(ticker)
            if analysis:
                results.append(analysis)
        
        logger.info(f"Analysis complete: {len(results)} stocks analyzed")
        return results
    
    def analyze_stocks_from_prices(self, sample_size: Optional[int] = None) -> List[Dict]:
        """Analyze stocks that have price data"""
        tickers = []
        
        for ticker_dir in self.prices_dir.iterdir():
            if ticker_dir.is_dir() and ticker_dir.name not in ['processed_stocks.json', 'fetching_summary.txt', 'price_data_index.csv']:
                tickers.append(ticker_dir.name)
        
        if sample_size:
            tickers = tickers[:sample_size]
            logger.info(f"Analyzing sample of {sample_size} stocks")
        
        return self.analyze_multiple_stocks(tickers)
    
    def save_analysis_results(self, results: List[Dict]):
        """Save analysis results to files"""
        if not results:
            logger.warning("No analysis results to save")
            return
        
        # Save as JSON
        json_file = self.output_dir / "stock_analysis_results.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Saved analysis results to {json_file}")
        
        # Save as CSV (summary)
        summary_data = []
        for result in results:
            summary = {
                'ticker': result['ticker'],
                'current_price': result['current_price'],
                'pe_ratio': result.get('pe_ratio'),
                'pb_ratio': result.get('pb_ratio'),
                'roe': result.get('roe'),
                'debt_to_equity': result.get('debt_to_equity'),
                'overall_score': result['investment_score']['overall_score'],
                'recommendation': result['investment_score']['recommendation'],
                'intrinsic_value': result.get('intrinsic_value'),
                'discount_to_intrinsic': result.get('discount_to_intrinsic')
            }
            summary_data.append(summary)
        
        summary_df = pd.DataFrame(summary_data)
        csv_file = self.output_dir / "stock_analysis_summary.csv"
        summary_df.to_csv(csv_file, index=False)
        
        logger.info(f"Saved analysis summary to {csv_file}")
        
        # Create ranking report
        self.create_ranking_report(summary_df)
    
    def create_ranking_report(self, summary_df: pd.DataFrame):
        """Create ranking report of analyzed stocks"""
        # Sort by overall score
        ranked_df = summary_df.sort_values('overall_score', ascending=False)
        
        report = []
        report.append("=" * 80)
        report.append("STOCK INVESTMENT RANKING REPORT")
        report.append("=" * 80)
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Stocks Analyzed: {len(ranked_df)}")
        report.append("")
        
        # Top recommendations
        report.append("TOP BUY RECOMMENDATIONS:")
        report.append("-" * 80)
        top_buys = ranked_df[ranked_df['recommendation'].isin(['Strong Buy', 'Buy'])].head(10)
        for _, row in top_buys.iterrows():
            report.append(f"{row['ticker']}: {row['recommendation']} (Score: {row['overall_score']})")
            report.append(f"  Price: ${row['current_price']:.2f} | P/E: {row['pe_ratio']:.2f} | ROE: {row['roe']:.2%}")
        
        report.append("")
        report.append("TOP SELL RECOMMENDATIONS:")
        report.append("-" * 80)
        top_sells = ranked_df[ranked_df['recommendation'].isin(['Sell', 'Strong Sell'])].head(10)
        for _, row in top_sells.iterrows():
            report.append(f"{row['ticker']}: {row['recommendation']} (Score: {row['overall_score']})")
            report.append(f"  Price: ${row['current_price']:.2f} | P/E: {row['pe_ratio']:.2f} | ROE: {row['roe']:.2%}")
        
        report.append("")
        report.append("=" * 80)
        
        report_text = "\n".join(report)
        
        # Save report
        report_file = self.output_dir / "investment_ranking_report.txt"
        with open(report_file, 'w') as f:
            f.write(report_text)
        
        logger.info(f"Saved ranking report to {report_file}")
    
    def generate_detailed_report(self, ticker: str, analysis: Dict) -> str:
        """Generate detailed analysis report for a single stock"""
        report = []
        report.append("=" * 80)
        report.append(f"DETAILED STOCK ANALYSIS: {ticker}")
        report.append("=" * 80)
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("INVESTMENT SUMMARY")
        report.append("-" * 80)
        report.append(f"Current Price: ${analysis['current_price']:.2f}")
        report.append(f"Recommendation: {analysis['investment_score']['recommendation']}")
        report.append(f"Overall Score: {analysis['investment_score']['overall_score']}/100")
        report.append(f"Confidence: {analysis['investment_score']['confidence']}")
        report.append("")
        
        if analysis.get('intrinsic_value'):
            report.append("VALUATION METRICS")
            report.append("-" * 80)
            report.append(f"Intrinsic Value: ${analysis['intrinsic_value']:.2f}")
            report.append(f"Discount to Intrinsic: {analysis.get('discount_to_intrinsic', 0):.2f}%")
            report.append("")
        
        report.append("FUNDAMENTAL METRICS")
        report.append("-" * 80)
        report.append(f"P/E Ratio: {analysis.get('pe_ratio', 'N/A')}")
        report.append(f"P/B Ratio: {analysis.get('pb_ratio', 'N/A')}")
        report.append(f"P/S Ratio: {analysis.get('ps_ratio', 'N/A')}")
        report.append(f"EV/EBITDA: {analysis.get('ev_ebitda', 'N/A')}")
        report.append("")
        
        report.append("PROFITABILITY METRICS")
        report.append("-" * 80)
        report.append(f"ROE: {analysis.get('roe', 'N/A')}")
        report.append(f"ROA: {analysis.get('roa', 'N/A')}")
        report.append(f"Profit Margin: {analysis.get('profit_margin', 'N/A')}")
        report.append(f"Operating Margin: {analysis.get('operating_margin', 'N/A')}")
        report.append("")
        
        report.append("FINANCIAL HEALTH")
        report.append("-" * 80)
        report.append(f"Debt/Equity: {analysis.get('debt_to_equity', 'N/A')}")
        report.append(f"Current Ratio: {analysis.get('current_ratio', 'N/A')}")
        report.append(f"Quick Ratio: {analysis.get('quick_ratio', 'N/A')}")
        report.append("")
        
        report.append("GROWTH METRICS")
        report.append("-" * 80)
        report.append(f"Revenue Growth: {analysis.get('revenue_growth', 'N/A')}")
        report.append(f"Earnings Growth: {analysis.get('earnings_growth', 'N/A')}")
        report.append("")
        
        if analysis.get('valuation_scores'):
            report.append("VALUATION SCORES")
            report.append("-" * 80)
            for score_name, score_value in analysis['valuation_scores'].items():
                report.append(f"{score_name}: {score_value}/100")
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Main execution function"""
    analyzer = StockValuationAnalyzer()
    
    # Analyze stocks with price data
    logger.info("Starting stock valuation analysis...")
    
    # Analyze sample of stocks
    results = analyzer.analyze_stocks_from_prices(sample_size=10)
    
    # Save results
    analyzer.save_analysis_results(results)
    
    # Generate detailed report for top stock
    if results:
        top_stock = max(results, key=lambda x: x['investment_score']['overall_score'])
        detailed_report = analyzer.generate_detailed_report(top_stock['ticker'], top_stock)
        
        report_file = analyzer.output_dir / f"{top_stock['ticker']}_detailed_analysis.txt"
        with open(report_file, 'w') as f:
            f.write(detailed_report)
        
        logger.info(f"Saved detailed report for {top_stock['ticker']}")
    
    logger.info("Stock valuation analysis completed")


if __name__ == "__main__":
    main()
