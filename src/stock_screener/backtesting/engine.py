"""
Backtesting engine for stock screening strategies
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BacktestEngine:
    """Backtest stock screening strategies"""
    
    def __init__(self):
        pass
    
    def walk_forward_backtest(self, price_data: Dict[str, pd.DataFrame],
                             screening_function,
                             rebalance_freq: str = 'M',
                             lookback_period: int = 252) -> Dict:
        """
        Perform walk-forward backtesting
        
        Args:
            price_data: Historical price data for stocks
            screening_function: Function that screens stocks and returns selected tickers
            rebalance_freq: Rebalancing frequency ('D', 'W', 'M')
            lookback_period: Lookback period in days
        """
        logger.info("Starting walk-forward backtest...")
        
        # Get common date range
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        
        # Determine rebalancing dates
        if rebalance_freq == 'D':
            rebalance_dates = all_dates[lookback_period::1]
        elif rebalance_freq == 'W':
            rebalance_dates = all_dates[lookback_period::5]
        elif rebalance_freq == 'M':
            rebalance_dates = all_dates[lookback_period::20]
        else:
            rebalance_dates = all_dates[lookback_period::20]
        
        portfolio_returns = []
        portfolio_weights = []
        
        for i, rebalance_date in enumerate(rebalance_dates):
            # Get lookback data
            lookback_start = all_dates[max(0, all_dates.index(rebalance_date) - lookback_period)]
            
            # Prepare lookback data for screening
            lookback_data = {}
            for ticker, df in price_data.items():
                lookback_data[ticker] = df.loc[lookback_start:rebalance_date]
            
            # Screen stocks
            selected_stocks = screening_function(lookback_data)
            
            # Calculate forward returns (next period)
            next_date_idx = all_dates.index(rebalance_date) + 1
            if next_date_idx < len(all_dates):
                next_date = all_dates[next_date_idx]
                
                # Calculate equal-weight returns
                returns = []
                for ticker in selected_stocks:
                    if ticker in price_data:
                        if rebalance_date in price_data[ticker].index and next_date in price_data[ticker].index:
                            stock_return = (price_data[ticker].loc[next_date, 'Close'] / 
                                          price_data[ticker].loc[rebalance_date, 'Close'] - 1)
                            returns.append(stock_return)
                
                if returns:
                    portfolio_return = np.mean(returns)
                    portfolio_returns.append({
                        'date': rebalance_date,
                        'return': portfolio_return,
                        'num_stocks': len(selected_stocks)
                    })
            
            if i % 10 == 0:
                logger.info(f"Processed {i+1}/{len(rebalance_dates)} rebalancing periods")
        
        # Calculate performance metrics
        returns_df = pd.DataFrame(portfolio_returns)
        returns_df.set_index('date', inplace=True)
        
        if len(returns_df) > 0:
            metrics = self._calculate_performance_metrics(returns_df['return'])
        else:
            metrics = {}
        
        results = {
            'returns': returns_df,
            'metrics': metrics,
            'rebalance_dates': rebalance_dates
        }
        
        logger.info("Walk-forward backtest completed")
        return results
    
    def _calculate_performance_metrics(self, returns: pd.Series) -> Dict:
        """Calculate performance metrics"""
        metrics = {}
        
        if len(returns) > 0:
            metrics['total_return'] = (1 + returns).prod() - 1
            metrics['annual_return'] = returns.mean() * 252
            metrics['annual_volatility'] = returns.std() * np.sqrt(252)
            metrics['sharpe_ratio'] = (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
            metrics['max_drawdown'] = self._calculate_max_drawdown(returns)
            metrics['win_rate'] = (returns > 0).sum() / len(returns)
        
        return metrics
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def compare_to_benchmark(self, strategy_returns: pd.Series,
                            benchmark_returns: pd.Series) -> Dict:
        """Compare strategy performance to benchmark"""
        logger.info("Comparing to benchmark...")
        
        # Align returns
        aligned = pd.concat([strategy_returns, benchmark_returns], axis=1, join='inner')
        aligned.columns = ['strategy', 'benchmark']
        
        # Calculate excess returns
        aligned['excess'] = aligned['strategy'] - aligned['benchmark']
        
        metrics = {
            'excess_return': aligned['excess'].mean() * 252,
            'tracking_error': aligned['excess'].std() * np.sqrt(252),
            'information_ratio': (aligned['excess'].mean() * 252) / (aligned['excess'].std() * np.sqrt(252)) if aligned['excess'].std() > 0 else 0,
            'correlation': aligned['strategy'].corr(aligned['benchmark']),
        }
        
        logger.info(f"Benchmark comparison: {metrics}")
        return metrics
    
    def monte_carlo_simulation(self, returns: pd.Series, 
                              num_simulations: int = 1000,
                              time_horizon: int = 252) -> Dict:
        """Perform Monte Carlo simulation for future returns"""
        logger.info(f"Running Monte Carlo simulation with {num_simulations} paths...")
        
        mean_return = returns.mean()
        std_return = returns.std()
        
        simulations = []
        for i in range(num_simulations):
            # Generate random returns
            random_returns = np.random.normal(mean_return, std_return, time_horizon)
            cumulative_return = (1 + random_returns).prod() - 1
            simulations.append(cumulative_return)
        
        simulations = np.array(simulations)
        
        results = {
            'mean': np.mean(simulations),
            'median': np.median(simulations),
            'std': np.std(simulations),
            'percentile_5': np.percentile(simulations, 5),
            'percentile_25': np.percentile(simulations, 25),
            'percentile_75': np.percentile(simulations, 75),
            'percentile_95': np.percentile(simulations, 95),
        }
        
        logger.info(f"Monte Carlo simulation completed")
        return results
