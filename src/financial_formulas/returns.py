"""
Return Calculations

Functions for calculating various types of investment returns.
"""

import numpy as np
from typing import Union, List


def simple_return(current_price: float, previous_price: float) -> float:
    """
    Calculate simple return.
    
    Formula: R = (P_t - P_{t-1}) / P_{t-1}
    
    Args:
        current_price: Current price (P_t)
        previous_price: Previous price (P_{t-1})
        
    Returns:
        Simple return as a decimal
        
    Example:
        >>> simple_return(110, 100)
        0.1
    """
    if previous_price == 0:
        raise ValueError("Previous price cannot be zero")
    return (current_price - previous_price) / previous_price


def log_return(current_price: float, previous_price: float) -> float:
    """
    Calculate logarithmic return.
    
    Formula: r = ln(P_t / P_{t-1})
    
    Args:
        current_price: Current price (P_t)
        previous_price: Previous price (P_{t-1})
        
    Returns:
        Log return as a decimal
        
    Example:
        >>> log_return(110, 100)
        0.09531017980432493
    """
    if previous_price <= 0 or current_price <= 0:
        raise ValueError("Prices must be positive")
    return np.log(current_price / previous_price)


def total_return(
    current_price: float, 
    previous_price: float, 
    dividends: float = 0
) -> float:
    """
    Calculate total return including price appreciation and dividends.
    
    Formula: Total Return = (P_t - P_{t-1} + Dividends) / P_{t-1}
    
    Args:
        current_price: Current price (P_t)
        previous_price: Previous price (P_{t-1})
        dividends: Dividends received (default: 0)
        
    Returns:
        Total return as a decimal
        
    Example:
        >>> total_return(110, 100, 5)
        0.15
    """
    if previous_price == 0:
        raise ValueError("Previous price cannot be zero")
    return (current_price - previous_price + dividends) / previous_price


def cumulative_returns(returns: List[float]) -> List[float]:
    """
    Calculate cumulative returns from a series of periodic returns.
    
    Formula: (1 + r_1) * (1 + r_2) * ... * (1 + r_n) - 1
    
    Args:
        returns: List of periodic returns as decimals
        
    Returns:
        List of cumulative returns
        
    Example:
        >>> cumulative_returns([0.1, 0.05, -0.02])
        [0.1, 0.155, 0.1319]
    """
    cumulative = []
    cumulative_product = 1.0
    
    for r in returns:
        cumulative_product *= (1 + r)
        cumulative.append(cumulative_product - 1)
    
    return cumulative


def annualized_return(returns: List[float], periods_per_year: int = 252) -> float:
    """
    Calculate annualized return from periodic returns.
    
    Formula: (1 + cumulative_return)^(periods_per_year / n) - 1
    
    Args:
        returns: List of periodic returns as decimals
        periods_per_year: Number of periods per year (default: 252 for daily)
        
    Returns:
        Annualized return as a decimal
        
    Example:
        >>> annualized_return([0.001] * 252)
        0.284...
    """
    if not returns:
        raise ValueError("Returns list cannot be empty")
    
    cumulative = (1 + np.array(returns)).prod() - 1
    n = len(returns)
    
    return (1 + cumulative) ** (periods_per_year / n) - 1
