"""
Financial Ratios

Functions for calculating key financial ratios used in company analysis.
"""

from typing import Union


def gross_margin(revenue: float, cost_of_goods_sold: float) -> float:
    """
    Calculate gross margin.
    
    Formula: Gross Margin = (Revenue - COGS) / Revenue
    
    Args:
        revenue: Total revenue
        cost_of_goods_sold: Cost of goods sold
        
    Returns:
        Gross margin as a decimal
        
    Example:
        >>> gross_margin(1000, 600)
        0.4
    """
    if revenue == 0:
        raise ValueError("Revenue cannot be zero")
    return (revenue - cost_of_goods_sold) / revenue


def operating_margin(operating_income: float, revenue: float) -> float:
    """
    Calculate operating margin.
    
    Formula: Operating Margin = Operating Income / Revenue
    
    Args:
        operating_income: Operating income
        revenue: Total revenue
        
    Returns:
        Operating margin as a decimal
        
    Example:
        >>> operating_margin(150, 1000)
        0.15
    """
    if revenue == 0:
        raise ValueError("Revenue cannot be zero")
    return operating_income / revenue


def net_margin(net_income: float, revenue: float) -> float:
    """
    Calculate net margin.
    
    Formula: Net Margin = Net Income / Revenue
    
    Args:
        net_income: Net income
        revenue: Total revenue
        
    Returns:
        Net margin as a decimal
        
    Example:
        >>> net_margin(100, 1000)
        0.1
    """
    if revenue == 0:
        raise ValueError("Revenue cannot be zero")
    return net_income / revenue


def return_on_assets(net_income: float, total_assets: float) -> float:
    """
    Calculate Return on Assets (ROA).
    
    Formula: ROA = Net Income / Total Assets
    
    Args:
        net_income: Net income
        total_assets: Total assets
        
    Returns:
        ROA as a decimal
        
    Example:
        >>> return_on_assets(100, 1000)
        0.1
    """
    if total_assets == 0:
        raise ValueError("Total assets cannot be zero")
    return net_income / total_assets


def return_on_equity(net_income: float, shareholder_equity: float) -> float:
    """
    Calculate Return on Equity (ROE).
    
    Formula: ROE = Net Income / Shareholder Equity
    
    Args:
        net_income: Net income
        shareholder_equity: Shareholder equity
        
    Returns:
        ROE as a decimal
        
    Example:
        >>> return_on_equity(100, 500)
        0.2
    """
    if shareholder_equity == 0:
        raise ValueError("Shareholder equity cannot be zero")
    return net_income / shareholder_equity


def current_ratio(current_assets: float, current_liabilities: float) -> float:
    """
    Calculate current ratio.
    
    Formula: Current Ratio = Current Assets / Current Liabilities
    
    Args:
        current_assets: Current assets
        current_liabilities: Current liabilities
        
    Returns:
        Current ratio
        
    Example:
        >>> current_ratio(200, 100)
        2.0
    """
    if current_liabilities == 0:
        raise ValueError("Current liabilities cannot be zero")
    return current_assets / current_liabilities


def quick_ratio(current_assets: float, inventory: float, current_liabilities: float) -> float:
    """
    Calculate quick ratio (acid test ratio).
    
    Formula: Quick Ratio = (Current Assets - Inventory) / Current Liabilities
    
    Args:
        current_assets: Current assets
        inventory: Inventory value
        current_liabilities: Current liabilities
        
    Returns:
        Quick ratio
        
    Example:
        >>> quick_ratio(200, 50, 100)
        1.5
    """
    if current_liabilities == 0:
        raise ValueError("Current liabilities cannot be zero")
    return (current_assets - inventory) / current_liabilities


def debt_to_equity(total_debt: float, shareholder_equity: float) -> float:
    """
    Calculate debt-to-equity ratio.
    
    Formula: D/E = Total Debt / Shareholder Equity
    
    Args:
        total_debt: Total debt
        shareholder_equity: Shareholder equity
        
    Returns:
        Debt-to-equity ratio
        
    Example:
        >>> debt_to_equity(300, 500)
        0.6
    """
    if shareholder_equity == 0:
        raise ValueError("Shareholder equity cannot be zero")
    return total_debt / shareholder_equity


def interest_coverage(ebit: float, interest_expense: float) -> float:
    """
    Calculate interest coverage ratio.
    
    Formula: Interest Coverage = EBIT / Interest Expense
    
    Args:
        ebit: Earnings before interest and taxes
        interest_expense: Interest expense
        
    Returns:
        Interest coverage ratio
        
    Example:
        >>> interest_coverage(200, 40)
        5.0
    """
    if interest_expense == 0:
        return float('inf')
    return ebit / interest_expense


def asset_turnover(revenue: float, total_assets: float) -> float:
    """
    Calculate asset turnover ratio.
    
    Formula: Asset Turnover = Revenue / Total Assets
    
    Args:
        revenue: Total revenue
        total_assets: Total assets
        
    Returns:
        Asset turnover ratio
        
    Example:
        >>> asset_turnover(1000, 500)
        2.0
    """
    if total_assets == 0:
        raise ValueError("Total assets cannot be zero")
    return revenue / total_assets


def inventory_turnover(cost_of_goods_sold: float, average_inventory: float) -> float:
    """
    Calculate inventory turnover ratio.
    
    Formula: Inventory Turnover = COGS / Average Inventory
    
    Args:
        cost_of_goods_sold: Cost of goods sold
        average_inventory: Average inventory
        
    Returns:
        Inventory turnover ratio
        
    Example:
        >>> inventory_turnover(600, 100)
        6.0
    """
    if average_inventory == 0:
        raise ValueError("Average inventory cannot be zero")
    return cost_of_goods_sold / average_inventory


def receivables_turnover(revenue: float, average_accounts_receivable: float) -> float:
    """
    Calculate receivables turnover ratio.
    
    Formula: Receivables Turnover = Revenue / Average Accounts Receivable
    
    Args:
        revenue: Total revenue
        average_accounts_receivable: Average accounts receivable
        
    Returns:
        Receivables turnover ratio
        
    Example:
        >>> receivables_turnover(1000, 200)
        5.0
    """
    if average_accounts_receivable == 0:
        raise ValueError("Average accounts receivable cannot be zero")
    return revenue / average_accounts_receivable


def days_sales_outstanding(revenue: float, average_accounts_receivable: float, days: int = 365) -> float:
    """
    Calculate days sales outstanding (DSO).
    
    Formula: DSO = (Average Accounts Receivable / Revenue) * Days
    
    Args:
        revenue: Total revenue
        average_accounts_receivable: Average accounts receivable
        days: Number of days (default: 365)
        
    Returns:
        Days sales outstanding
        
    Example:
        >>> days_sales_outstanding(1000, 200)
        73.0
    """
    if revenue == 0:
        raise ValueError("Revenue cannot be zero")
    return (average_accounts_receivable / revenue) * days


def days_inventory_outstanding(cost_of_goods_sold: float, average_inventory: float, days: int = 365) -> float:
    """
    Calculate days inventory outstanding (DIO).
    
    Formula: DIO = (Average Inventory / COGS) * Days
    
    Args:
        cost_of_goods_sold: Cost of goods sold
        average_inventory: Average inventory
        days: Number of days (default: 365)
        
    Returns:
        Days inventory outstanding
        
    Example:
        >>> days_inventory_outstanding(600, 100)
        60.83...
    """
    if cost_of_goods_sold == 0:
        raise ValueError("Cost of goods sold cannot be zero")
    return (average_inventory / cost_of_goods_sold) * days


def days_payables_outstanding(cost_of_goods_sold: float, average_accounts_payable: float, days: int = 365) -> float:
    """
    Calculate days payables outstanding (DPO).
    
    Formula: DPO = (Average Accounts Payable / COGS) * Days
    
    Args:
        cost_of_goods_sold: Cost of goods sold
        average_accounts_payable: Average accounts payable
        days: Number of days (default: 365)
        
    Returns:
        Days payables outstanding
        
    Example:
        >>> days_payables_outstanding(600, 150)
        91.25
    """
    if cost_of_goods_sold == 0:
        raise ValueError("Cost of goods sold cannot be zero")
    return (average_accounts_payable / cost_of_goods_sold) * days


def cash_conversion_cycle(dio: float, dso: float, dpo: float) -> float:
    """
    Calculate cash conversion cycle.
    
    Formula: CCC = DIO + DSO - DPO
    
    Args:
        dio: Days inventory outstanding
        dso: Days sales outstanding
        dpo: Days payables outstanding
        
    Returns:
        Cash conversion cycle in days
        
    Example:
        >>> cash_conversion_cycle(60, 45, 30)
        75.0
    """
    return dio + dso - dpo
