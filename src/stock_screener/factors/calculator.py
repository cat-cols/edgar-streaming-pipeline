"""
Factor calculator for value, quality, momentum, and other factors
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FactorCalculator:
    """Calculate financial factors for stock screening"""
    
    def __init__(self):
        pass
    
    def calculate_value_factors(self, fundamentals: Dict[str, Dict]) -> pd.DataFrame:
        """Calculate value factors (P/E, P/B, EV/EBITDA, etc.)"""
        logger.info("Calculating value factors...")
        
        data = []
        for ticker, fund in fundamentals.items():
            if fund:
                data.append({
                    'ticker': ticker,
                    'pe_ratio': fund.get('pe_ratio', np.nan),
                    'pb_ratio': fund.get('pb_ratio', np.nan),
                    'ps_ratio': fund.get('ps_ratio', np.nan),
                    'ev_ebitda': fund.get('ev_ebitda', np.nan),
                    'dividend_yield': fund.get('dividend_yield', np.nan),
                })
        
        df = pd.DataFrame(data)
        df.set_index('ticker', inplace=True)
        
        # Calculate value scores (lower ratios = better value)
        df['value_score_pe'] = -df['pe_ratio'].rank(pct=True)
        df['value_score_pb'] = -df['pb_ratio'].rank(pct=True)
        df['value_score_ev'] = -df['ev_ebitda'].rank(pct=True)
        df['value_score_div'] = df['dividend_yield'].rank(pct=True)
        
        # Combined value score
        df['value_score'] = (
            df['value_score_pe'] * 0.3 +
            df['value_score_pb'] * 0.3 +
            df['value_score_ev'] * 0.2 +
            df['value_score_div'] * 0.2
        )
        
        logger.info(f"Calculated value factors for {len(df)} stocks")
        return df
    
    def calculate_quality_factors(self, fundamentals: Dict[str, Dict]) -> pd.DataFrame:
        """Calculate quality factors (ROE, ROA, margins, debt levels)"""
        logger.info("Calculating quality factors...")
        
        data = []
        for ticker, fund in fundamentals.items():
            if fund:
                data.append({
                    'ticker': ticker,
                    'roe': fund.get('roe', np.nan),
                    'roa': fund.get('roa', np.nan),
                    'profit_margin': fund.get('profit_margin', np.nan),
                    'operating_margin': fund.get('operating_margin', np.nan),
                    'debt_to_equity': fund.get('debt_to_equity', np.nan),
                    'current_ratio': fund.get('current_ratio', np.nan),
                    'quick_ratio': fund.get('quick_ratio', np.nan),
                })
        
        df = pd.DataFrame(data)
        df.set_index('ticker', inplace=True)
        
        # Calculate quality scores (higher ROE/ROA/margins = better quality)
        df['quality_score_roe'] = df['roe'].rank(pct=True)
        df['quality_score_roa'] = df['roa'].rank(pct=True)
        df['quality_score_pm'] = df['profit_margin'].rank(pct=True)
        df['quality_score_om'] = df['operating_margin'].rank(pct=True)
        df['quality_score_de'] = -df['debt_to_equity'].rank(pct=True)  # Lower debt = better
        df['quality_score_cr'] = df['current_ratio'].rank(pct=True)
        
        # Combined quality score
        df['quality_score'] = (
            df['quality_score_roe'] * 0.25 +
            df['quality_score_roa'] * 0.15 +
            df['quality_score_pm'] * 0.2 +
            df['quality_score_om'] * 0.15 +
            df['quality_score_de'] * 0.15 +
            df['quality_score_cr'] * 0.1
        )
        
        logger.info(f"Calculated quality factors for {len(df)} stocks")
        return df
    
    def calculate_momentum_factors(self, technical_indicators: Dict[str, Dict]) -> pd.DataFrame:
        """Calculate momentum factors (price momentum, technical indicators)"""
        logger.info("Calculating momentum factors...")
        
        data = []
        for ticker, tech in technical_indicators.items():
            if tech:
                data.append({
                    'ticker': ticker,
                    'momentum_3m': tech.get('momentum_3m', np.nan),
                    'momentum_6m': tech.get('momentum_6m', np.nan),
                    'momentum_12m': tech.get('momentum_12m', np.nan),
                    'rsi': tech.get('rsi', np.nan),
                    'price_above_sma50': tech.get('price_above_sma50', np.nan),
                    'price_above_sma200': tech.get('price_above_sma200', np.nan),
                    'volatility': tech.get('volatility', np.nan),
                })
        
        df = pd.DataFrame(data)
        
        # Handle empty DataFrame
        if df.empty:
            logger.warning("No technical indicators data available, returning empty DataFrame")
            return pd.DataFrame()
        
        df.set_index('ticker', inplace=True)
        
        # Calculate momentum scores (higher momentum = better)
        df['momentum_score_3m'] = df['momentum_3m'].rank(pct=True)
        df['momentum_score_6m'] = df['momentum_6m'].rank(pct=True)
        df['momentum_score_12m'] = df['momentum_12m'].rank(pct=True)
        df['momentum_score_trend'] = (
            df['price_above_sma50'].astype(float) * 0.5 +
            df['price_above_sma200'].astype(float) * 0.5
        )
        
        # RSI score (avoid overbought >70, avoid oversold <30)
        df['rsi_score'] = 1 - np.abs(df['rsi'] - 50) / 50  # Closer to 50 is better
        
        # Combined momentum score
        df['momentum_score'] = (
            df['momentum_score_3m'] * 0.2 +
            df['momentum_score_6m'] * 0.3 +
            df['momentum_score_12m'] * 0.3 +
            df['momentum_score_trend'] * 0.1 +
            df['rsi_score'] * 0.1
        )
        
        logger.info(f"Calculated momentum factors for {len(df)} stocks")
        return df
    
    def calculate_low_volatility_factors(self, fundamentals: Dict[str, Dict], 
                                        technical_indicators: Dict[str, Dict]) -> pd.DataFrame:
        """Calculate low volatility factors (beta, historical volatility)"""
        logger.info("Calculating low volatility factors...")
        
        data = []
        for ticker in set(list(fundamentals.keys()) + list(technical_indicators.keys())):
            fund = fundamentals.get(ticker, {})
            tech = technical_indicators.get(ticker, {})
            
            data.append({
                'ticker': ticker,
                'beta': fund.get('beta', np.nan) if fund else np.nan,
                'volatility': tech.get('volatility', np.nan) if tech else np.nan,
            })
        
        df = pd.DataFrame(data)
        
        # Handle empty DataFrame
        if df.empty:
            logger.warning("No data available for low volatility factors, returning empty DataFrame")
            return pd.DataFrame()
        
        df.set_index('ticker', inplace=True)
        
        # Calculate low volatility scores (lower beta/volatility = better)
        df['lowvol_score_beta'] = -df['beta'].rank(pct=True)
        df['lowvol_score_vol'] = -df['volatility'].rank(pct=True)
        
        # Combined low volatility score
        df['lowvol_score'] = (
            df['lowvol_score_beta'] * 0.6 +
            df['lowvol_score_vol'] * 0.4
        )
        
        logger.info(f"Calculated low volatility factors for {len(df)} stocks")
        return df
    
    def combine_all_factors(self, value_df: pd.DataFrame, quality_df: pd.DataFrame,
                          momentum_df: pd.DataFrame, lowvol_df: pd.DataFrame,
                          weights: Dict[str, float] = None) -> pd.DataFrame:
        """Combine all factor scores into a composite score"""
        logger.info("Combining all factors...")
        
        if weights is None:
            weights = {
                'value': 0.3,
                'quality': 0.3,
                'momentum': 0.25,
                'lowvol': 0.15
            }
        
        # Handle empty DataFrames
        dfs_to_concat = []
        if not value_df.empty and 'value_score' in value_df.columns:
            dfs_to_concat.append(value_df[['value_score']])
        else:
            logger.warning("Value factors DataFrame is empty or missing value_score")
            
        if not quality_df.empty and 'quality_score' in quality_df.columns:
            dfs_to_concat.append(quality_df[['quality_score']])
        else:
            logger.warning("Quality factors DataFrame is empty or missing quality_score")
            
        if not momentum_df.empty and 'momentum_score' in momentum_df.columns:
            dfs_to_concat.append(momentum_df[['momentum_score']])
        else:
            logger.warning("Momentum factors DataFrame is empty or missing momentum_score")
            
        if not lowvol_df.empty and 'lowvol_score' in lowvol_df.columns:
            dfs_to_concat.append(lowvol_df[['lowvol_score']])
        else:
            logger.warning("Low volatility factors DataFrame is empty or missing lowvol_score")
        
        if not dfs_to_concat:
            logger.error("No valid factor DataFrames to combine")
            return pd.DataFrame()
        
        # Merge all factor DataFrames
        all_factors = pd.concat(dfs_to_concat, axis=1, join='outer')
        
        # Calculate composite score (handle missing scores)
        composite_score = pd.Series(0.0, index=all_factors.index)
        
        if 'value_score' in all_factors.columns:
            composite_score += all_factors['value_score'] * weights['value']
        else:
            logger.warning("Missing value_score in composite calculation")
            
        if 'quality_score' in all_factors.columns:
            composite_score += all_factors['quality_score'] * weights['quality']
        else:
            logger.warning("Missing quality_score in composite calculation")
            
        if 'momentum_score' in all_factors.columns:
            composite_score += all_factors['momentum_score'] * weights['momentum']
        else:
            logger.warning("Missing momentum_score in composite calculation")
            
        if 'lowvol_score' in all_factors.columns:
            composite_score += all_factors['lowvol_score'] * weights['lowvol']
        else:
            logger.warning("Missing lowvol_score in composite calculation")
        
        all_factors['composite_score'] = composite_score
        
        # Rank stocks by composite score
        all_factors['rank'] = all_factors['composite_score'].rank(ascending=False)
        
        logger.info(f"Combined factors for {len(all_factors)} stocks")
        return all_factors
