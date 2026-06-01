"""
Portfolio Metrics

Functions for calculating portfolio-level metrics and trading performance.
"""

import numpy as np
from typing import List, Union


def portfolio_return(weights: List[float], returns: List[float]) -> float:
    """
    Calculate portfolio return.
    
    Formula: R_p = Σ(w_i * R_i)
    
    Args:
        weights: List of asset weights (must sum to 1)
        returns: List of asset returns
        
    Returns:
        Portfolio return as a decimal
        
    Example:
        >>> portfolio_return([0.5, 0.5], [0.1, 0.2])
        0.15
    """
    if len(weights) != len(returns):
        raise ValueError("Weights and returns must have same length")
    
    if not np.isclose(sum(weights), 1.0, atol=1e-6):
        raise ValueError("Weights must sum to 1")
    
    return sum(w * r for w, r in zip(weights, returns))


def portfolio_variance(weights: List[float], cov_matrix: List[List[float]]) -> float:
    """
    Calculate portfolio variance.
    
    Formula: σ_p² = Σ_i Σ_j w_i w_j σ_i σ_j ρ_ij
    
    Args:
        weights: List of asset weights
        cov_matrix: Covariance matrix of asset returns
        
    Returns:
        Portfolio variance
        
    Example:
        >>> portfolio_variance([0.5, 0.5], [[0.01, 0.005], [0.005, 0.02]])
        0.0125
    """
    if len(weights) != len(cov_matrix):
        raise ValueError("Weights length must match covariance matrix dimensions")
    
    weights_array = np.array(weights)
    cov_array = np.array(cov_matrix)
    
    return float(weights_array.T @ cov_array @ weights_array)


def portfolio_std_dev(weights: List[float], cov_matrix: List[List[float]]) -> float:
    """
    Calculate portfolio standard deviation.
    
    Formula: σ_p = sqrt(σ_p²)
    
    Args:
        weights: List of asset weights
        cov_matrix: Covariance matrix of asset returns
        
    Returns:
        Portfolio standard deviation
        
    Example:
        >>> portfolio_std_dev([0.5, 0.5], [[0.01, 0.005], [0.005, 0.02]])
        0.1118...
    """
    return np.sqrt(portfolio_variance(weights, cov_matrix))


def treynor_ratio(portfolio_return: float, risk_free_rate: float, portfolio_beta: float) -> float:
    """
    Calculate Treynor ratio.
    
    Formula: Treynor = (R_p - R_f) / β_p
    
    Args:
        portfolio_return: Portfolio return as decimal
        risk_free_rate: Risk-free rate as decimal
        portfolio_beta: Portfolio beta
        
    Returns:
        Treynor ratio
        
    Example:
        >>> treynor_ratio(0.15, 0.02, 1.2)
        0.1083...
    """
    if portfolio_beta == 0:
        raise ValueError("Portfolio beta cannot be zero")
    return (portfolio_return - risk_free_rate) / portfolio_beta


def jensens_alpha(portfolio_return: float, risk_free_rate: float, market_return: float, portfolio_beta: float) -> float:
    """
    Calculate Jensen's Alpha.

    Formula: α_J = R_p - [R_f + β_p(R_m - R_f)]

    Args:
        portfolio_return: Portfolio return as decimal
        risk_free_rate: Risk-free rate as decimal
        market_return: Market return as decimal
        portfolio_beta: Portfolio beta

    Returns:
        Jensen's alpha as decimal

    Example:
        >>> jensens_alpha(0.15, 0.02, 0.10, 1.2)
        0.016
    """
    expected_return = risk_free_rate + portfolio_beta * (market_return - risk_free_rate)
    return portfolio_return - expected_return


def win_rate(trades: List[float]) -> float:
    """
    Calculate win rate.

    Formula: Win Rate = Number of Winning Trades / Total Trades

    Args:
        trades: List of trade returns (positive = win, negative = loss)

    Returns:
        Win rate as a decimal

    Example:
        >>> win_rate([0.1, -0.05, 0.08, 0.12, -0.03])
        0.6
    """
    if not trades:
        raise ValueError("Trades list cannot be empty")

    winning_trades = sum(1 for trade in trades if trade > 0)
    return winning_trades / len(trades)


def risk_reward_ratio(winning_trades: List[float], losing_trades: List[float]) -> float:
    """
    Calculate risk-reward ratio.

    Formula: R/R = Average Win / Average Loss

    Args:
        winning_trades: List of winning trade returns
        losing_trades: List of losing trade returns (as positive values)

    Returns:
        Risk-reward ratio
        
    Example:
        >>> risk_reward_ratio([0.1, 0.08, 0.12], [0.05, 0.03])
        2.0
    """
    if not winning_trades:
        raise ValueError("Winning trades list cannot be empty")
    if not losing_trades:
        return float('inf')
    
    avg_win = np.mean(winning_trades)
    avg_loss = np.mean(losing_trades)
    
    if avg_loss == 0:
        return float('inf')
    
    return avg_win / avg_loss


def profit_factor(gross_profit: float, gross_loss: float) -> float:
    """
    Calculate profit factor.
    
    Formula: Profit Factor = Gross Profit / Gross Loss
    
    Args:
        gross_profit: Total gross profit
        gross_loss: Total gross loss (as positive value)
        
    Returns:
        Profit factor
        
    Example:
        >>> profit_factor(1000, 500)
        2.0
    """
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    return gross_profit / gross_loss


def expectancy(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """
    Calculate expectancy (expected value per trade).
    
    Formula: Expectancy = (P_win × Avg Win) - (P_loss × Avg Loss)
    
    Args:
        win_rate: Probability of winning as decimal
        avg_win: Average winning trade return
        avg_loss: Average losing trade return (as positive value)
        
    Returns:
        Expectancy per trade
        
    Example:
        >>> expectancy(0.6, 0.1, 0.05)
        0.035
    """
    loss_rate = 1 - win_rate
    return (win_rate * avg_win) - (loss_rate * avg_loss)


def average_trade(trades: List[float]) -> float:
    """
    Calculate average trade return.
    
    Formula: Average Trade = Σ(Trade Returns) / Number of Trades
    
    Args:
        trades: List of trade returns
        
    Returns:
        Average trade return as decimal
        
    Example:
        >>> average_trade([0.1, -0.05, 0.08, 0.12, -0.03])
        0.044
    """
    if not trades:
        raise ValueError("Trades list cannot be empty")
    return np.mean(trades)


def total_return(trades: List[float]) -> float:
    """
    Calculate total return from a series of trades.
    
    Formula: Total Return = (1 + r_1) * (1 + r_2) * ... * (1 + r_n) - 1
    
    Args:
        trades: List of trade returns as decimals
        
    Returns:
        Total return as decimal
        
    Example:
        >>> total_return([0.1, -0.05, 0.08])
        0.1226
    """
    if not trades:
        raise ValueError("Trades list cannot be empty")
    
    cumulative = 1.0
    for trade in trades:
        cumulative *= (1 + trade)
    
    return cumulative - 1


def calmar_ratio(portfolio_return: float, max_drawdown: float) -> float:
    """
    Calculate Calmar ratio.
    
    Formula: Calmar = Portfolio Return / |Max Drawdown|
    
    Args:
        portfolio_return: Portfolio return as decimal
        max_drawdown: Maximum drawdown as decimal (negative value)
        
    Returns:
        Calmar ratio
        
    Example:
        >>> calmar_ratio(0.15, -0.10)
        1.5
    """
    if max_drawdown == 0:
        return float('inf') if portfolio_return > 0 else 0.0
    return portfolio_return / abs(max_drawdown)


def omega_ratio(returns: List[float], threshold: float = 0.0) -> float:
    """
    Calculate Omega ratio.
    
    Formula: Omega = Σ(max(r - threshold, 0)) / Σ(max(threshold - r, 0))
    
    Args:
        returns: List of returns
        threshold: Threshold return (default: 0)
        
    Returns:
        Omega ratio
        
    Example:
        >>> omega_ratio([0.1, -0.05, 0.08, 0.12, -0.03])
        2.0
    """
    if not returns:
        raise ValueError("Returns list cannot be empty")
    
    gains = sum(max(r - threshold, 0) for r in returns)
    losses = sum(max(threshold - r, 0) for r in returns)
    
    if losses == 0:
        return float('inf') if gains > 0 else 0.0
    
    return gains / losses
