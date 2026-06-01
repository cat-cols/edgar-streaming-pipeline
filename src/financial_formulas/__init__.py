"""
Financial Formulas Module

This module provides Python implementations of common financial formulas
used in analysis, valuation, and risk management.
"""

from .returns import (
    simple_return,
    log_return,
    total_return,
)

from .valuation import (
    future_value,
    present_value,
    net_present_value,
    gordon_growth_model,
    pe_ratio,
    pb_ratio,
    ev_ebitda,
)

from .risk_metrics import (
    standard_deviation,
    beta,
    sharpe_ratio,
    sortino_ratio,
    information_ratio,
    alpha,
    tracking_error,
    max_drawdown,
)

from .ratios import (
    gross_margin,
    operating_margin,
    net_margin,
    return_on_assets,
    return_on_equity,
    current_ratio,
    quick_ratio,
    debt_to_equity,
    interest_coverage,
    asset_turnover,
    inventory_turnover,
)

from .portfolio_metrics import (
    portfolio_return,
    portfolio_variance,
    treynor_ratio,
    jensens_alpha,
    win_rate,
    risk_reward_ratio,
    profit_factor,
    expectancy,
)

from .time_series import (
    rolling_beta,
    rolling_return,
    rolling_treynor_ratio,
    rolling_sharpe_ratio,
    rolling_volatility,
    rolling_max_drawdown,
    rolling_sortino_ratio,
    create_rolling_metrics_dataframe,
)

__all__ = [
    # Returns
    "simple_return",
    "log_return",
    "total_return",
    # Valuation
    "future_value",
    "present_value",
    "net_present_value",
    "gordon_growth_model",
    "pe_ratio",
    "pb_ratio",
    "ev_ebitda",
    # Risk Metrics
    "standard_deviation",
    "beta",
    "sharpe_ratio",
    "sortino_ratio",
    "information_ratio",
    "alpha",
    "tracking_error",
    "max_drawdown",
    # Ratios
    "gross_margin",
    "operating_margin",
    "net_margin",
    "return_on_assets",
    "return_on_equity",
    "current_ratio",
    "quick_ratio",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "inventory_turnover",
    # Portfolio Metrics
    "portfolio_return",
    "portfolio_variance",
    "treynor_ratio",
    "jensens_alpha",
    "win_rate",
    "risk_reward_ratio",
    "profit_factor",
    "expectancy",
    # Time Series
    "rolling_beta",
    "rolling_return",
    "rolling_treynor_ratio",
    "rolling_sharpe_ratio",
    "rolling_volatility",
    "rolling_max_drawdown",
    "rolling_sortino_ratio",
    "create_rolling_metrics_dataframe",
]
