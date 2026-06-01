"""
Time Series Rolling Window Calculations

Functions for calculating rolling window versions of financial metrics
for time-series analysis and charting.
"""

import numpy as np
import pandas as pd
from typing import List, Union, Optional

from .risk_metrics import beta, sharpe_ratio, standard_deviation
from .returns import simple_return


def rolling_beta(
    asset_returns: List[float], 
    market_returns: List[float], 
    window: int = 60
) -> List[float]:
    """
    Calculate rolling beta using a sliding window.
    
    Args:
        asset_returns: List of asset returns
        market_returns: List of market returns (same length as asset_returns)
        window: Window size for rolling calculation (default: 60)
        
    Returns:
        List of rolling beta values (NaN for positions where full window not available)
        
    Example:
        >>> rolling_beta([0.01] * 100, [0.008] * 100, 30)
        [nan, nan, ..., 1.25, 1.25, ...]
    """
    if len(asset_returns) != len(market_returns):
        raise ValueError("Asset and market returns must have same length")
    
    if window < 2:
        raise ValueError("Window size must be at least 2")
    
    rolling_betas = []
    
    for i in range(len(asset_returns)):
        if i < window - 1:
            rolling_betas.append(np.nan)
        else:
            window_asset = asset_returns[i - window + 1:i + 1]
            window_market = market_returns[i - window + 1:i + 1]
            
            try:
                beta_val = beta(window_asset, window_market)
                rolling_betas.append(beta_val)
            except (ValueError, ZeroDivisionError):
                rolling_betas.append(np.nan)
    
    return rolling_betas


def rolling_return(
    prices: List[float], 
    window: int = 60,
    return_type: str = "simple"
) -> List[float]:
    """
    Calculate rolling return over a sliding window.
    
    Args:
        prices: List of prices
        window: Window size for rolling calculation (default: 60)
        return_type: Type of return - "simple" or "log" (default: "simple")
        
    Returns:
        List of rolling returns (NaN for positions where full window not available)
        
    Example:
        >>> rolling_return([100, 101, 102, 103, 104], 3)
        [nan, nan, 0.03, 0.0297, 0.0294]
    """
    if window < 2:
        raise ValueError("Window size must be at least 2")
    
    rolling_returns = []
    
    for i in range(len(prices)):
        if i < window - 1:
            rolling_returns.append(np.nan)
        else:
            start_price = prices[i - window + 1]
            end_price = prices[i]
            
            if return_type == "simple":
                ret = simple_return(end_price, start_price)
            elif return_type == "log":
                if start_price <= 0 or end_price <= 0:
                    rolling_returns.append(np.nan)
                    continue
                ret = np.log(end_price / start_price)
            else:
                raise ValueError("return_type must be 'simple' or 'log'")
            
            rolling_returns.append(ret)
    
    return rolling_returns


def rolling_treynor_ratio(
    asset_prices: List[float],
    market_prices: List[float],
    risk_free_rate: float,
    window: int = 60,
    periods_per_year: int = 252
) -> List[float]:
    """
    Calculate rolling Treynor ratio using a sliding window.
    
    Formula: Treynor = (R_p - R_f) / β_p
    
    Args:
        asset_prices: List of asset prices
        market_prices: List of market benchmark prices (same length as asset_prices)
        risk_free_rate: Annual risk-free rate as decimal
        window: Window size for rolling calculation (default: 60)
        periods_per_year: Number of periods per year (default: 252 for daily)
        
    Returns:
        List of rolling Treynor ratios (NaN for positions where full window not available)
        
    Example:
        >>> rolling_treynor_ratio([100, 101, 102, ...], [4000, 4020, 4040, ...], 0.02, 30)
        [nan, nan, ..., 0.15, 0.16, ...]
    """
    if len(asset_prices) != len(market_prices):
        raise ValueError("Asset and market prices must have same length")
    
    # Convert prices to returns
    asset_returns = [simple_return(asset_prices[i], asset_prices[i-1]) 
                    for i in range(1, len(asset_prices))]
    market_returns = [simple_return(market_prices[i], market_prices[i-1]) 
                     for i in range(1, len(market_prices))]
    
    # Calculate rolling beta
    rolling_betas = rolling_beta(asset_returns, market_returns, window)
    
    # Calculate rolling returns
    rolling_returns_list = rolling_return(asset_prices, window, "simple")
    
    # Calculate Treynor ratio for each window
    treynor_ratios = []
    
    for i in range(len(rolling_returns_list)):
        if np.isnan(rolling_returns_list[i]) or np.isnan(rolling_betas[i]):
            treynor_ratios.append(np.nan)
        else:
            beta_val = rolling_betas[i]
            if beta_val == 0:
                treynor_ratios.append(np.nan)
            else:
                # Annualize the return
                annualized_return = rolling_returns_list[i] * (periods_per_year / window)
                treynor = (annualized_return - risk_free_rate) / beta_val
                treynor_ratios.append(treynor)
    
    return treynor_ratios


def rolling_sharpe_ratio(
    returns: List[float],
    risk_free_rate: float,
    window: int = 60,
    periods_per_year: int = 252
) -> List[float]:
    """
    Calculate rolling Sharpe ratio using a sliding window.
    
    Args:
        returns: List of returns
        risk_free_rate: Annual risk-free rate as decimal
        window: Window size for rolling calculation (default: 60)
        periods_per_year: Number of periods per year (default: 252 for daily)
        
    Returns:
        List of rolling Sharpe ratios (NaN for positions where full window not available)
        
    Example:
        >>> rolling_sharpe_ratio([0.01, -0.005, 0.02, ...], 0.02, 30)
        [nan, nan, ..., 1.5, 1.6, ...]
    """
    if window < 2:
        raise ValueError("Window size must be at least 2")
    
    rolling_sharpe = []
    
    for i in range(len(returns)):
        if i < window - 1:
            rolling_sharpe.append(np.nan)
        else:
            window_returns = returns[i - window + 1:i + 1]
            
            try:
                sharpe = sharpe_ratio(window_returns, risk_free_rate, periods_per_year)
                rolling_sharpe.append(sharpe)
            except (ValueError, ZeroDivisionError):
                rolling_sharpe.append(np.nan)
    
    return rolling_sharpe


def rolling_volatility(
    returns: List[float],
    window: int = 60,
    periods_per_year: int = 252
) -> List[float]:
    """
    Calculate rolling volatility (annualized standard deviation).
    
    Args:
        returns: List of returns
        window: Window size for rolling calculation (default: 60)
        periods_per_year: Number of periods per year (default: 252 for daily)
        
    Returns:
        List of rolling volatilities (NaN for positions where full window not available)
        
    Example:
        >>> rolling_volatility([0.01, -0.005, 0.02, ...], 30)
        [nan, nan, ..., 0.15, 0.16, ...]
    """
    if window < 2:
        raise ValueError("Window size must be at least 2")
    
    rolling_vols = []
    
    for i in range(len(returns)):
        if i < window - 1:
            rolling_vols.append(np.nan)
        else:
            window_returns = returns[i - window + 1:i + 1]
            
            try:
                vol = standard_deviation(window_returns) * np.sqrt(periods_per_year)
                rolling_vols.append(vol)
            except ValueError:
                rolling_vols.append(np.nan)
    
    return rolling_vols


def rolling_max_drawdown(
    prices: List[float],
    window: int = 252
) -> List[float]:
    """
    Calculate rolling maximum drawdown over a sliding window.
    
    Args:
        prices: List of prices
        window: Window size for rolling calculation (default: 252 for one year)
        
    Returns:
        List of rolling maximum drawdowns (NaN for positions where full window not available)
        
    Example:
        >>> rolling_max_drawdown([100, 110, 105, 95, 90, 100], 4)
        [nan, nan, nan, -0.136, -0.181, -0.181]
    """
    if window < 2:
        raise ValueError("Window size must be at least 2")
    
    rolling_mdd = []
    
    for i in range(len(prices)):
        if i < window - 1:
            rolling_mdd.append(np.nan)
        else:
            window_prices = prices[i - window + 1:i + 1]
            window_prices_array = np.array(window_prices)
            peak = np.maximum.accumulate(window_prices_array)
            drawdown = (window_prices_array - peak) / peak
            rolling_mdd.append(np.min(drawdown))
    
    return rolling_mdd


def rolling_sortino_ratio(
    returns: List[float],
    risk_free_rate: float,
    window: int = 60,
    periods_per_year: int = 252
) -> List[float]:
    """
    Calculate rolling Sortino ratio using a sliding window.
    
    Args:
        returns: List of returns
        risk_free_rate: Annual risk-free rate as decimal
        window: Window size for rolling calculation (default: 60)
        periods_per_year: Number of periods per year (default: 252 for daily)
        
    Returns:
        List of rolling Sortino ratios (NaN for positions where full window not available)
    """
    from .risk_metrics import sortino_ratio
    
    if window < 2:
        raise ValueError("Window size must be at least 2")
    
    rolling_sortino = []
    
    for i in range(len(returns)):
        if i < window - 1:
            rolling_sortino.append(np.nan)
        else:
            window_returns = returns[i - window + 1:i + 1]
            
            try:
                sortino = sortino_ratio(window_returns, risk_free_rate, periods_per_year)
                rolling_sortino.append(sortino)
            except (ValueError, ZeroDivisionError):
                rolling_sortino.append(np.nan)
    
    return rolling_sortino


def create_rolling_metrics_dataframe(
    prices: List[float],
    market_prices: List[float],
    risk_free_rate: float,
    window: int = 60,
    periods_per_year: int = 252
) -> pd.DataFrame:
    """
    Create a DataFrame with multiple rolling metrics for easy charting.
    
    Args:
        prices: List of asset prices
        market_prices: List of market benchmark prices
        risk_free_rate: Annual risk-free rate as decimal
        window: Window size for rolling calculations (default: 60)
        periods_per_year: Number of periods per year (default: 252 for daily)
        
    Returns:
        DataFrame with columns: price, rolling_return, rolling_beta, 
        rolling_treynor, rolling_sharpe, rolling_volatility, rolling_max_drawdown
        
    Example:
        >>> df = create_rolling_metrics_dataframe(prices, market_prices, 0.02, 30)
        >>> df.plot(subplots=True)
    """
    # Convert prices to returns
    returns = [simple_return(prices[i], prices[i-1]) for i in range(1, len(prices))]
    
    # Pad returns with NaN to match price length
    returns_padded = [np.nan] + returns
    
    # Calculate all rolling metrics
    rolling_returns_list = rolling_return(prices, window)
    rolling_betas = rolling_beta(returns, 
                                 [simple_return(market_prices[i], market_prices[i-1]) 
                                  for i in range(1, len(market_prices))], 
                                 window)
    rolling_betas_padded = [np.nan] + rolling_betas
    
    rolling_treynor = rolling_treynor_ratio(prices, market_prices, risk_free_rate, window, periods_per_year)
    rolling_sharpe = rolling_sharpe_ratio(returns_padded, risk_free_rate, window, periods_per_year)
    rolling_vol = rolling_volatility(returns_padded, window, periods_per_year)
    rolling_mdd = rolling_max_drawdown(prices, window)
    
    # Create DataFrame
    df = pd.DataFrame({
        'price': prices,
        'rolling_return': rolling_returns_list,
        'rolling_beta': rolling_betas_padded,
        'rolling_treynor': rolling_treynor,
        'rolling_sharpe': rolling_sharpe,
        'rolling_volatility': rolling_vol,
        'rolling_max_drawdown': rolling_mdd
    })
    
    return df
