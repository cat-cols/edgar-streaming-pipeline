"""
Stock ranking and filtering based on factor scores
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockRanker:
    """Rank and filter stocks based on factor scores"""
    
    def __init__(self):
        pass
    
    def apply_quality_filters(self, factors_df: pd.DataFrame, 
                            fundamentals: Dict[str, Dict]) -> pd.DataFrame:
        """Apply minimum quality thresholds to filter out poor quality stocks"""
        logger.info("Applying quality filters...")
        
        filtered_tickers = []
        for ticker in factors_df.index:
            fund = fundamentals.get(ticker, {})
            
            # Quality filters
            if not fund:
                continue
            
            # Minimum ROE
            if fund.get('roe', 0) < 0.05:  # 5% minimum ROE
                continue
            
            # Maximum debt-to-equity
            if fund.get('debt_to_equity', 999) > 3:  # Max 3x debt-to-equity
                continue
            
            # Minimum current ratio
            if fund.get('current_ratio', 0) < 1.0:  # Minimum 1.0 current ratio
                continue
            
            # Positive profit margin
            if fund.get('profit_margin', 0) < 0:
                continue
            
            filtered_tickers.append(ticker)
        
        filtered_df = factors_df.loc[filtered_tickers]
        logger.info(f"Quality filter: {len(factors_df)} -> {len(filtered_df)} stocks")
        return filtered_df
    
    def apply_liquidity_filters(self, factors_df: pd.DataFrame,
                               fundamentals: Dict[str, Dict],
                               min_market_cap: float = 1e9,  # $1B minimum
                               min_volume: float = 1e6) -> pd.DataFrame:
        """Apply liquidity filters (market cap, volume)"""
        logger.info("Applying liquidity filters...")
        
        filtered_tickers = []
        for ticker in factors_df.index:
            fund = fundamentals.get(ticker, {})
            
            if not fund:
                continue
            
            # Minimum market cap
            if fund.get('market_cap', 0) < min_market_cap:
                continue
            
            filtered_tickers.append(ticker)
        
        filtered_df = factors_df.loc[filtered_tickers]
        logger.info(f"Liquidity filter: {len(factors_df)} -> {len(filtered_df)} stocks")
        return filtered_df
    
    def rank_by_composite_score(self, factors_df: pd.DataFrame, 
                                 top_n: Optional[int] = None) -> pd.DataFrame:
        """Rank stocks by composite score"""
        logger.info("Ranking stocks by composite score...")
        
        ranked = factors_df.sort_values('composite_score', ascending=False)
        
        if top_n:
            ranked = ranked.head(top_n)
            logger.info(f"Top {top_n} stocks selected")
        
        return ranked
    
    def apply_sector_diversification(self, ranked_df: pd.DataFrame,
                                    fundamentals: Dict[str, Dict],
                                    max_per_sector: int = 5) -> pd.DataFrame:
        """Apply sector diversification constraints"""
        logger.info("Applying sector diversification...")
        
        # Group by sector (simplified - in practice, you'd need sector data)
        # For now, we'll just limit total number of stocks
        selected = ranked_df.head(max_per_sector * 10)  # Assume ~10 sectors
        
        logger.info(f"Sector diversification: {len(ranked_df)} -> {len(selected)} stocks")
        return selected
    
    def generate_screening_report(self, ranked_df: pd.DataFrame,
                                 fundamentals: Dict[str, Dict],
                                 technical_indicators: Dict[str, Dict]) -> pd.DataFrame:
        """Generate a comprehensive screening report"""
        logger.info("Generating screening report...")
        
        report_data = []
        for ticker in ranked_df.index:
            fund = fundamentals.get(ticker, {})
            tech = technical_indicators.get(ticker, {})
            
            report_data.append({
                'ticker': ticker,
                'composite_score': ranked_df.loc[ticker, 'composite_score'],
                'rank': ranked_df.loc[ticker, 'rank'],
                'value_score': ranked_df.loc[ticker, 'value_score'] if 'value_score' in ranked_df.columns else np.nan,
                'quality_score': ranked_df.loc[ticker, 'quality_score'] if 'quality_score' in ranked_df.columns else np.nan,
                'momentum_score': ranked_df.loc[ticker, 'momentum_score'] if 'momentum_score' in ranked_df.columns else np.nan,
                'lowvol_score': ranked_df.loc[ticker, 'lowvol_score'] if 'lowvol_score' in ranked_df.columns else np.nan,
                'pe_ratio': fund.get('pe_ratio', np.nan) if fund else np.nan,
                'pb_ratio': fund.get('pb_ratio', np.nan) if fund else np.nan,
                'roe': fund.get('roe', np.nan) if fund else np.nan,
                'debt_to_equity': fund.get('debt_to_equity', np.nan) if fund else np.nan,
                'momentum_12m': tech.get('momentum_12m', np.nan) if tech else np.nan,
                'beta': fund.get('beta', np.nan) if fund else np.nan,
            })
        
        report_df = pd.DataFrame(report_data)
        report_df = report_df.sort_values('composite_score', ascending=False)
        
        logger.info(f"Generated report for {len(report_df)} stocks")
        return report_df
    
    def save_report(self, report_df: pd.DataFrame, output_path: str):
        """Save screening report to file"""
        report_df.to_csv(output_path, index=False)
        logger.info(f"Saved report to {output_path}")
