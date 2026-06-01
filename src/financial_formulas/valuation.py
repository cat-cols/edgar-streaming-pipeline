"""
Valuation Formulas

Functions for time value of money, dividend discount models, and relative valuation.
"""

import numpy as np
from typing import List, Union


def future_value(present_value: float, rate: float, periods: int) -> float:
    """
    Calculate future value.
    
    Formula: FV = PV * (1 + r)^n
    
    Args:
        present_value: Present value (PV)
        rate: Interest rate per period as decimal
        periods: Number of periods (n)
        
    Returns:
        Future value
        
    Example:
        >>> future_value(1000, 0.05, 10)
        1628.894626777442
    """
    return present_value * (1 + rate) ** periods


def present_value(future_value: float, rate: float, periods: int) -> float:
    """
    Calculate present value.
    
    Formula: PV = FV / (1 + r)^n
    
    Args:
        future_value: Future value (FV)
        rate: Discount rate per period as decimal
        periods: Number of periods (n)
        
    Returns:
        Present value
        
    Example:
        >>> present_value(1628.89, 0.05, 10)
        1000.0...
    """
    return future_value / (1 + rate) ** periods


def net_present_value(cash_flows: List[float], rate: float) -> float:
    """
    Calculate net present value of a series of cash flows.
    
    Formula: NPV = Σ(CF_t / (1 + r)^t)
    
    Args:
        cash_flows: List of cash flows (first element is typically initial investment)
        rate: Discount rate per period as decimal
        
    Returns:
        Net present value
        
    Example:
        >>> net_present_value([-1000, 300, 300, 300, 300], 0.1)
        -49.18...
    """
    npv = 0
    for t, cf in enumerate(cash_flows):
        npv += cf / ((1 + rate) ** t)
    return npv


def internal_rate_of_return(cash_flows: List[float]) -> float:
    """
    Calculate internal rate of return using numerical methods.
    
    Args:
        cash_flows: List of cash flows (first element is initial investment)
        
    Returns:
        IRR as a decimal
        
    Example:
        >>> internal_rate_of_return([-1000, 300, 300, 300, 300])
        0.077...
    """
    from scipy.optimize import newton
    
    def npv_function(rate):
        return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cash_flows))
    
    try:
        return newton(npv_function, 0.1)
    except:
        return np.nan


def gordon_growth_model(dividend_next_year: float, required_return: float, growth_rate: float) -> float:
    """
    Calculate stock price using Gordon Growth Model (Dividend Discount Model).
    
    Formula: P = D_1 / (r - g)
    
    Args:
        dividend_next_year: Expected dividend next year (D_1)
        required_return: Required rate of return as decimal (r)
        growth_rate: Constant growth rate as decimal (g)
        
    Returns:
        Intrinsic stock price
        
    Example:
        >>> gordon_growth_model(2.0, 0.10, 0.05)
        40.0
    """
    if required_return <= growth_rate:
        raise ValueError("Required return must be greater than growth rate")
    return dividend_next_year / (required_return - growth_rate)


def pe_ratio(price_per_share: float, earnings_per_share: float) -> float:
    """
    Calculate Price-to-Earnings ratio.
    
    Formula: P/E = Price per Share / Earnings per Share
    
    Args:
        price_per_share: Current stock price
        earnings_per_share: Earnings per share
        
    Returns:
        P/E ratio
        
    Example:
        >>> pe_ratio(100, 5)
        20.0
    """
    if earnings_per_share == 0:
        raise ValueError("Earnings per share cannot be zero")
    return price_per_share / earnings_per_share


def pb_ratio(market_cap: float, book_value: float) -> float:
    """
    Calculate Price-to-Book ratio.
    
    Formula: P/B = Market Cap / Book Value
    
    Args:
        market_cap: Market capitalization
        book_value: Book value of equity
        
    Returns:
        P/B ratio
        
    Example:
        >>> pb_ratio(1000000, 800000)
        1.25
    """
    if book_value == 0:
        raise ValueError("Book value cannot be zero")
    return market_cap / book_value


def ev_ebitda(enterprise_value: float, ebitda: float) -> float:
    """
    Calculate Enterprise Value to EBITDA ratio.
    
    Formula: EV/EBITDA = Enterprise Value / EBITDA
    
    Args:
        enterprise_value: Enterprise value
        ebitda: Earnings before interest, taxes, depreciation, and amortization
        
    Returns:
        EV/EBITDA ratio
        
    Example:
        >>> ev_ebitda(1200000, 200000)
        6.0
    """
    if ebitda == 0:
        raise ValueError("EBITDA cannot be zero")
    return enterprise_value / ebitda


def dividend_yield(dividend_per_share: float, price_per_share: float) -> float:
    """
    Calculate dividend yield.
    
    Formula: Dividend Yield = Dividend per Share / Price per Share
    
    Args:
        dividend_per_share: Annual dividend per share
        price_per_share: Current stock price
        
    Returns:
        Dividend yield as a decimal
        
    Example:
        >>> dividend_yield(2.0, 100)
        0.02
    """
    if price_per_share == 0:
        raise ValueError("Price per share cannot be zero")
    return dividend_per_share / price_per_share
