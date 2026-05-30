# Financial Metrics

Performance and risk metrics used in quantitative finance and portfolio management.

## Risk Metrics

### Standard Deviation (Volatility)
$$\sigma = \sqrt{\frac{\sum(x_i - \mu)^2}{n}}$$
- Measure of dispersion
- Annualized for daily returns: $\sigma_{annual} = \sigma_{daily} \times \sqrt{252}$
- Higher = more risk

### Beta
$$\beta = \frac{\text{Cov}(r_i, r_m)}{\text{Var}(r_m)}$$
- Sensitivity to market movements
- $\beta = 1$: moves with market
- $\beta > 1$: more volatile than market
- $\beta < 1$: less volatile than market

### Value at Risk (VaR)
- Maximum expected loss at confidence level
- 95% VaR: 5% chance of losing more than this amount
- Can be historical, parametric, or Monte Carlo

### Maximum Drawdown
$$\text{MDD} = \frac{\text{Peak Value} - \text{Trough Value}}{\text{Peak Value}}$$
- Largest peak-to-trough decline
- Important for risk management
- Lower is better

## Performance Metrics

### Sharpe Ratio
$$\text{Sharpe} = \frac{R_p - R_f}{\sigma_p}$$
- Risk-adjusted return
- Higher is better
- >1 is considered good
- >2 is excellent

### Sortino Ratio
$$\text{Sortino} = \frac{R_p - R_f}{\sigma_{downside}}$$
- Similar to Sharpe but only penalizes downside volatility
- Better for asymmetric return distributions
- Higher is better

### Information Ratio
$$\text{IR} = \frac{R_p - R_b}{\sigma_{p-b}}$$
- Risk-adjusted excess return over benchmark
- Measures active management skill
- Higher is better
- >0.5 is considered good

### Alpha
$$\alpha = R_p - [R_f + \beta(R_m - R_f)]$$
- Excess return over CAPM prediction
- Positive alpha = outperformance
- Negative alpha = underperformance

### Tracking Error
$$\text{Tracking Error} = \sigma(R_p - R_b)$$
- Standard deviation of excess returns
- Measures deviation from benchmark
- Higher = less consistent with benchmark

## Portfolio Metrics

### Portfolio Return
$$R_p = \sum w_i R_i$$
- Weighted average of individual returns
- Weights must sum to 1

### Portfolio Variance
$$\sigma_p^2 = \sum_i \sum_j w_i w_j \sigma_i \sigma_j \rho_{ij}$$
- Depends on individual variances and correlations
- Diversification reduces portfolio variance

### Treynor Ratio
$$\text{Treynor} = \frac{R_p - R_f}{\beta_p}$$
- Risk-adjusted return using beta
- Similar to Sharpe but uses systematic risk only
- Higher is better

### Jensen's Alpha
$$\alpha_J = R_p - [R_f + \beta_p(R_m - R_f)]$$
- CAPM-based alpha
- Measures risk-adjusted outperformance
- Positive indicates skill

## Trading Metrics

### Win Rate
$$\text{Win Rate} = \frac{\text{Number of Winning Trades}}{\text{Total Trades}}$$
- Percentage of profitable trades
- Higher is generally better
- Must consider risk-reward ratio

### Risk-Reward Ratio
$$\text{R/R} = \frac{\text{Average Win}}{\text{Average Loss}}$$
- Average profit vs average loss
- Higher is better
- >2 is considered good

### Profit Factor
$$\text{Profit Factor} = \frac{\text{Gross Profit}}{\text{Gross Loss}}$$
- Ratio of total wins to total losses
- >1 indicates profitability
- >2 is considered good

### Expectancy
$$\text{Expectancy} = (P_{win} \times \text{Avg Win}) - (P_{loss} \times \text{Avg Loss})$$
- Expected value per trade
- Positive = profitable system
- Negative = unprofitable system
