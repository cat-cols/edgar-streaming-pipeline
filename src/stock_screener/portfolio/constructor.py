"""
Portfolio construction from screened stocks
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortfolioConstructor:
    """Construct portfolios from screened stocks"""
    
    def __init__(self):
        pass
    
    def equal_weight_portfolio(self, tickers: List[str], 
                              total_capital: float = 100000) -> Dict[str, float]:
        """Create equal-weight portfolio"""
        logger.info(f"Creating equal-weight portfolio with {len(tickers)} stocks")
        
        weight = 1.0 / len(tickers)
        portfolio = {ticker: weight for ticker in tickers}
        
        logger.info(f"Equal weight: {weight:.4f} per stock")
        return portfolio
    
    def value_weighted_portfolio(self, tickers: List[str],
                                fundamentals: Dict[str, Dict],
                                total_capital: float = 100000) -> Dict[str, float]:
        """Create value-weighted portfolio based on market cap"""
        logger.info(f"Creating value-weighted portfolio with {len(tickers)} stocks")
        
        # Get market caps
        market_caps = {}
        for ticker in tickers:
            fund = fundamentals.get(ticker, {})
            if fund:
                market_caps[ticker] = fund.get('market_cap', 1e9)
        
        total_market_cap = sum(market_caps.values())
        
        # Calculate weights
        portfolio = {}
        for ticker, market_cap in market_caps.items():
            portfolio[ticker] = market_cap / total_market_cap
        
        logger.info(f"Value-weighted portfolio created")
        return portfolio
    
    def risk_parity_portfolio(self, tickers: List[str],
                             returns: Dict[str, pd.Series],
                             total_capital: float = 100000) -> Dict[str, float]:
        """Create risk parity portfolio (equal risk contribution)"""
        logger.info(f"Creating risk parity portfolio with {len(tickers)} stocks")
        
        # Calculate volatilities
        volatilities = {}
        for ticker in tickers:
            if ticker in returns:
                volatilities[ticker] = returns[ticker].std()
        
        # Inverse volatility weighting
        inv_vols = {ticker: 1/vol for ticker, vol in volatilities.items() if vol > 0}
        total_inv_vol = sum(inv_vols.values())
        
        portfolio = {ticker: inv_vol/total_inv_vol for ticker, inv_vol in inv_vols.items()}
        
        logger.info(f"Risk parity portfolio created")
        return portfolio
    
    def kelly_criterion_weights(self, tickers: List[str],
                               expected_returns: Dict[str, float],
                               volatilities: Dict[str, float],
                               total_capital: float = 100000) -> Dict[str, float]:
        """Calculate Kelly criterion optimal weights"""
        logger.info(f"Calculating Kelly criterion weights for {len(tickers)} stocks")
        
        portfolio = {}
        for ticker in tickers:
            if ticker in expected_returns and ticker in volatilities:
                exp_ret = expected_returns[ticker]
                vol = volatilities[ticker]
                
                if vol > 0:
                    # Kelly fraction = expected_return / variance
                    kelly_fraction = exp_ret / (vol ** 2)
                    # Cap at 25% to avoid over-concentration
                    portfolio[ticker] = min(kelly_fraction, 0.25)
        
        # Normalize weights
        total_weight = sum(portfolio.values())
        if total_weight > 0:
            portfolio = {ticker: weight/total_weight for ticker, weight in portfolio.items()}
        
        logger.info(f"Kelly criterion weights calculated")
        return portfolio
    
    def calculate_portfolio_metrics(self, portfolio: Dict[str, float],
                                   returns: Dict[str, pd.Series]) -> Dict[str, float]:
        """Calculate portfolio-level metrics"""
        logger.info("Calculating portfolio metrics...")
        
        # Calculate portfolio returns
        portfolio_returns = pd.Series(0.0, index=next(iter(returns.values())).index)
        
        for ticker, weight in portfolio.items():
            if ticker in returns:
                # Align returns
                aligned_returns = returns[ticker].reindex(portfolio_returns.index, fill_value=0)
                portfolio_returns += aligned_returns * weight
        
        # Calculate metrics
        metrics = {
            'annual_return': portfolio_returns.mean() * 252,
            'annual_volatility': portfolio_returns.std() * np.sqrt(252),
            'sharpe_ratio': (portfolio_returns.mean() * 252) / (portfolio_returns.std() * np.sqrt(252)) if portfolio_returns.std() > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(portfolio_returns),
        }
        
        logger.info(f"Portfolio metrics: {metrics}")
        return metrics
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def optimize_portfolio(self, tickers: List[str],
                          expected_returns: Dict[str, float],
                          covariance_matrix: pd.DataFrame,
                          risk_aversion: float = 1.0) -> Dict[str, float]:
        """Optimize portfolio using mean-variance optimization"""
        logger.info(f"Optimizing portfolio for {len(tickers)} stocks")
        
        # Simplified optimization (in practice, use cvxpy or similar)
        # For now, use inverse variance weighting
        
        inv_variances = {}
        for ticker in tickers:
            if ticker in covariance_matrix.columns:
                var = covariance_matrix.loc[ticker, ticker]
                if var > 0:
                    inv_variances[ticker] = 1 / var
        
        total_inv_var = sum(inv_variances.values())
        portfolio = {ticker: inv_var/total_inv_var for ticker, inv_var in inv_variances.items()}
        
        logger.info(f"Portfolio optimized")
        return portfolio
