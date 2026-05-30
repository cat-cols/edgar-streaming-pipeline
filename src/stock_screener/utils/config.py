"""
Configuration file for stock screener
"""

# Data configuration
DATA_CONFIG = {
    'asset_universe_path': 'assets/compiled/comprehensive_asset_list.csv',
    'cache_dir': 'data/cache',
    'default_period': '2y',
    'default_interval': '1d',
}

# Factor weights
FACTOR_WEIGHTS = {
    'value': 0.3,
    'quality': 0.3,
    'momentum': 0.25,
    'lowvol': 0.15,
}

# Screening filters
SCREENING_FILTERS = {
    'min_market_cap': 1e9,  # $1B minimum
    'min_roe': 0.05,  # 5% minimum ROE
    'max_debt_to_equity': 3.0,  # Maximum 3x debt-to-equity
    'min_current_ratio': 1.0,  # Minimum 1.0 current ratio
    'min_profit_margin': 0.0,  # Non-negative profit margin
}

# Portfolio construction
PORTFOLIO_CONFIG = {
    'default_capital': 100000,
    'max_position_size': 0.1,  # Maximum 10% per position
    'min_position_size': 0.01,  # Minimum 1% per position
    'max_stocks': 30,  # Maximum number of stocks in portfolio
}

# Backtesting
BACKTEST_CONFIG = {
    'default_lookback_period': 252,  # 1 year
    'default_rebalance_freq': 'M',  # Monthly
    'transaction_cost': 0.001,  # 0.1% per trade
}

# Risk management
RISK_CONFIG = {
    'max_portfolio_volatility': 0.20,  # 20% annual volatility
    'max_drawdown_limit': 0.20,  # 20% maximum drawdown
    'var_confidence': 0.95,  # 95% VaR
}
