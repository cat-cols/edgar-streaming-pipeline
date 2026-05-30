"""
Helper functions for stock screener
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_scores(scores: pd.Series) -> pd.Series:
    """Normalize scores to 0-1 range"""
    min_val = scores.min()
    max_val = scores.max()
    
    if max_val == min_val:
        return pd.Series([0.5] * len(scores), index=scores.index)
    
    return (scores - min_val) / (max_val - min_val)


def z_score_normalization(scores: pd.Series) -> pd.Series:
    """Calculate z-scores"""
    mean = scores.mean()
    std = scores.std()
    
    if std == 0:
        return pd.Series([0.0] * len(scores), index=scores.index)
    
    return (scores - mean) / std


def rank_normalization(scores: pd.Series, ascending: bool = False) -> pd.Series:
    """Rank-based normalization (percentiles)"""
    return scores.rank(pct=True, ascending=ascending)


def winsorize(series: pd.Series, lower: float = 0.05, upper: float = 0.95) -> pd.Series:
    """Winsorize series to handle outliers"""
    lower_bound = series.quantile(lower)
    upper_bound = series.quantile(upper)
    
    return series.clip(lower=lower_bound, upper=upper_bound)


def calculate_correlation_matrix(returns_dict: Dict[str, pd.Series]) -> pd.DataFrame:
    """Calculate correlation matrix for multiple return series"""
    returns_df = pd.DataFrame(returns_dict)
    return returns_df.corr()


def calculate_covariance_matrix(returns_dict: Dict[str, pd.Series]) -> pd.DataFrame:
    """Calculate covariance matrix for multiple return series"""
    returns_df = pd.DataFrame(returns_dict)
    return returns_df.cov()


def align_data_series(series_dict: Dict[str, pd.Series]) -> pd.DataFrame:
    """Align multiple time series to common dates"""
    return pd.DataFrame(series_dict)


def calculate_rolling_metrics(returns: pd.Series, window: int = 20) -> Dict:
    """Calculate rolling metrics for returns"""
    rolling_mean = returns.rolling(window=window).mean()
    rolling_std = returns.rolling(window=window).std()
    rolling_sharpe = rolling_mean / rolling_std
    
    return {
        'rolling_mean': rolling_mean,
        'rolling_std': rolling_std,
        'rolling_sharpe': rolling_sharpe,
    }


def format_number(value: float, decimals: int = 2) -> str:
    """Format number for display"""
    if pd.isna(value):
        return "N/A"
    
    if abs(value) >= 1e9:
        return f"${value/1e9:.{decimals}f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:.{decimals}f}M"
    elif abs(value) >= 1e3:
        return f"${value/1e3:.{decimals}f}K"
    else:
        return f"{value:.{decimals}f}"


def calculate_information_ratio(strategy_returns: pd.Series, 
                               benchmark_returns: pd.Series) -> float:
    """Calculate information ratio"""
    # Align returns
    aligned = pd.concat([strategy_returns, benchmark_returns], axis=1, join='inner')
    aligned.columns = ['strategy', 'benchmark']
    
    excess_returns = aligned['strategy'] - aligned['benchmark']
    
    if excess_returns.std() == 0:
        return 0.0
    
    return excess_returns.mean() / excess_returns.std()


def calculate_beta(stock_returns: pd.Series, market_returns: pd.Series) -> float:
    """Calculate beta relative to market"""
    # Align returns
    aligned = pd.concat([stock_returns, market_returns], axis=1, join='inner')
    aligned.columns = ['stock', 'market']
    
    covariance = aligned['stock'].cov(aligned['market'])
    market_variance = aligned['market'].var()
    
    if market_variance == 0:
        return 1.0
    
    return covariance / market_variance


def calculate_alpha(stock_returns: pd.Series, market_returns: pd.Series, 
                   risk_free_rate: float = 0.02) -> float:
    """Calculate alpha (CAPM)"""
    beta = calculate_beta(stock_returns, market_returns)
    
    stock_return = stock_returns.mean() * 252
    market_return = market_returns.mean() * 252
    
    expected_return = risk_free_rate + beta * (market_return - risk_free_rate)
    alpha = stock_return - expected_return
    
    return alpha


def save_to_csv(data: pd.DataFrame, filepath: str):
    """Save DataFrame to CSV"""
    data.to_csv(filepath, index=False)
    logger.info(f"Saved data to {filepath}")


def load_from_csv(filepath: str) -> pd.DataFrame:
    """Load DataFrame from CSV"""
    data = pd.read_csv(filepath)
    logger.info(f"Loaded data from {filepath}")
    return data
