"""
Risk Metrics

Functions for calculating risk metrics including volatility, beta, and risk-adjusted returns.
"""

import numpy as np
from typing import List, Union


def standard_deviation(values: List[float], sample: bool = True) -> float:
    """
    Calculate standard deviation (volatility).
    
    Formula: σ = sqrt(Σ(x_i - μ)² / n)
    
    Args:
        values: List of values
        sample: If True, use sample standard deviation (n-1 denominator)
        
    Returns:
        Standard deviation
        
    Example:
        >>> standard_deviation([1, 2, 3, 4, 5])
        1.5811388300841898
    """
    if len(values) < 2:
        raise ValueError("At least 2 values required")
    return np.std(values, ddof=1 if sample else 0)


def annualized_volatility(daily_returns: List[float], periods_per_year: int = 252) -> float:
    """
    Calculate annualized volatility from daily returns.
    
    Formula: σ_annual = σ_daily * sqrt(periods_per_year)
    
    Args:
        daily_returns: List of daily returns as decimals
        periods_per_year: Number of trading periods per year (default: 252)
        
    Returns:
        Annualized volatility
        
    Example:
        >>> annualized_volatility([0.01] * 252)
        0.158...
    """
    daily_vol = standard_deviation(daily_returns)
    return daily_vol * np.sqrt(periods_per_year)


def beta(asset_returns: List[float], market_returns: List[float]) -> float:
    """
    Calculate beta (systematic risk).
    
    Formula: β = Cov(r_i, r_m) / Var(r_m)
    
    Args:
        asset_returns: List of asset returns
        market_returns: List of market returns
        
    Returns:
        Beta coefficient
        
    Example:
        >>> beta([0.1, 0.05, -0.02], [0.08, 0.04, -0.01])
        1.25...
    """
    if len(asset_returns) != len(market_returns):
        raise ValueError("Asset and market returns must have same length")
    
    covariance = np.cov(asset_returns, market_returns)[0][1]
    market_variance = np.var(market_returns, ddof=1)
    
    if market_variance == 0:
        raise ValueError("Market variance cannot be zero")
    
    return covariance / market_variance


def sharpe_ratio(returns: List[float], risk_free_rate: float, periods_per_year: int = 252) -> float:
    """
    Calculate Sharpe ratio (risk-adjusted return).
    
    Formula: Sharpe = (R_p - R_f) / σ_p
    
    Args:
        returns: List of portfolio returns
        risk_free_rate: Annual risk-free rate as decimal
        periods_per_year: Number of periods per year (default: 252)
        
    Returns:
        Sharpe ratio
        
    Example:
        >>> sharpe_ratio([0.01] * 252, 0.02)
        1.26...
    """
    if not returns:
        raise ValueError("Returns list cannot be empty")
    
    excess_returns = np.array(returns) - (risk_free_rate / periods_per_year)
    excess_std = standard_deviation(excess_returns.tolist())
    
    if excess_std == 0:
        return 0.0
    
    return np.mean(excess_returns) / excess_std * np.sqrt(periods_per_year)


def sortino_ratio(returns: List[float], risk_free_rate: float, periods_per_year: int = 252) -> float:
    """
    Calculate Sortino ratio (downside risk-adjusted return).
    
    Formula: Sortino = (R_p - R_f) / σ_downside
    
    Args:
        returns: List of portfolio returns
        risk_free_rate: Annual risk-free rate as decimal
        periods_per_year: Number of periods per year (default: 252)
        
    Returns:
        Sortino ratio
        
    Example:
        >>> sortino_ratio([0.01] * 252, 0.02)
        1.78...
    """
    if not returns:
        raise ValueError("Returns list cannot be empty")
    
    excess_returns = np.array(returns) - (risk_free_rate / periods_per_year)
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0:
        return float('inf') if np.mean(excess_returns) > 0 else 0.0
    
    downside_std = standard_deviation(downside_returns.tolist())
    
    if downside_std == 0:
        return 0.0
    
    return np.mean(excess_returns) / downside_std * np.sqrt(periods_per_year)


def information_ratio(portfolio_returns: List[float], benchmark_returns: List[float], periods_per_year: int = 252) -> float:
    """
    Calculate Information Ratio (active risk-adjusted return).
    
    Formula: IR = (R_p - R_b) / σ_{p-b}
    
    Args:
        portfolio_returns: List of portfolio returns
        benchmark_returns: List of benchmark returns
        periods_per_year: Number of periods per year (default: 252)
        
    Returns:
        Information ratio
        
    Example:
        >>> information_ratio([0.01] * 252, [0.008] * 252)
        3.16...
    """
    if len(portfolio_returns) != len(benchmark_returns):
        raise ValueError("Portfolio and benchmark returns must have same length")
    
    excess_returns = np.array(portfolio_returns) - np.array(benchmark_returns)
    tracking_error = standard_deviation(excess_returns.tolist())
    
    if tracking_error == 0:
        return 0.0
    
    return np.mean(excess_returns) / tracking_error * np.sqrt(periods_per_year)


def alpha(portfolio_returns: List[float], market_returns: List[float], risk_free_rate: float, periods_per_year: int = 252) -> float:
    """
    Calculate Jensen's Alpha (CAPM-based alpha).
    
    Formula: α = R_p - [R_f + β(R_m - R_f)]
    
    Args:
        portfolio_returns: List of portfolio returns
        market_returns: List of market returns
        risk_free_rate: Annual risk-free rate as decimal
        periods_per_year: Number of periods per year (default: 252)
        
    Returns:
        Alpha as annualized decimal
        
    Example:
        >>> alpha([0.01] * 252, [0.008] * 252, 0.02)
        0.002...
    """
    if len(portfolio_returns) != len(market_returns):
        raise ValueError("Portfolio and market returns must have same length")
    
    portfolio_return = np.mean(portfolio_returns) * periods_per_year
    market_return = np.mean(market_returns) * periods_per_year
    beta_coeff = beta(portfolio_returns, market_returns)
    
    expected_return = risk_free_rate + beta_coeff * (market_return - risk_free_rate)
    return portfolio_return - expected_return


def tracking_error(portfolio_returns: List[float], benchmark_returns: List[float], periods_per_year: int = 252) -> float:
    """
    Calculate tracking error (standard deviation of excess returns).
    
    Formula: Tracking Error = σ(R_p - R_b)
    
    Args:
        portfolio_returns: List of portfolio returns
        benchmark_returns: List of benchmark returns
        periods_per_year: Number of periods per year (default: 252)
        
    Returns:
        Annualized tracking error
        
    Example:
        >>> tracking_error([0.01] * 252, [0.008] * 252)
        0.002...
    """
    if len(portfolio_returns) != len(benchmark_returns):
        raise ValueError("Portfolio and benchmark returns must have same length")
    
    excess_returns = np.array(portfolio_returns) - np.array(benchmark_returns)
    return standard_deviation(excess_returns.tolist()) * np.sqrt(periods_per_year)


def max_drawdown(values: List[float]) -> float:
    """
    Calculate maximum drawdown.
    
    Formula: MDD = (Peak Value - Trough Value) / Peak Value
    
    Args:
        values: List of portfolio values or cumulative returns
        
    Returns:
        Maximum drawdown as a decimal (negative value)
        
    Example:
        >>> max_drawdown([100, 110, 105, 95, 90, 100])
        -0.1818...
    """
    if not values:
        raise ValueError("Values list cannot be empty")
    
    values = np.array(values)
    peak = np.maximum.accumulate(values)
    drawdown = (values - peak) / peak
    return np.min(drawdown)


def value_at_risk(returns: List[float], confidence_level: float = 0.95) -> float:
    """
    Calculate historical Value at Risk (VaR).
    
    Args:
        returns: List of returns
        confidence_level: Confidence level (default: 0.95 for 95% VaR)
        
    Returns:
        VaR at the specified confidence level (negative value)
        
    Example:
        >>> value_at_risk([0.01, -0.02, 0.03, -0.01, 0.02], 0.95)
        -0.02
    """
    if not returns:
        raise ValueError("Returns list cannot be empty")
    
    return np.percentile(returns, (1 - confidence_level) * 100)
