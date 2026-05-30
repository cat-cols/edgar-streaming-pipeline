# Factor Models

Quantitative finance factor models for asset pricing and risk management.

## Single-Factor Model

### Capital Asset Pricing Model (CAPM)
$$E(R_i) = R_f + \beta_i(E(R_m) - R_f)$$

- **$R_f$**: Risk-free rate
- **$E(R_m)$**: Expected market return
- **$\beta_i$**: Asset's sensitivity to market
- **$E(R_i)$**: Expected asset return

**Assumptions:**
- Investors are rational and risk-averse
- Markets are efficient
- Single period investment horizon
- No transaction costs or taxes

## Multi-Factor Models

### Fama-French Three-Factor Model
$$E(R_i) = R_f + \beta_i^{MKT}(R_m - R_f) + \beta_i^{SMB}SMB + \beta_i^{HML}HML$$

**Factors:**
- **MKT**: Market excess return
- **SMB**: Small Minus Big (size factor)
- **HML**: High Minus Low (value factor)

### Carhart Four-Factor Model
Adds momentum to Fama-French:
$$E(R_i) = R_f + \beta_i^{MKT}(R_m - R_f) + \beta_i^{SMB}SMB + \beta_i^{HML}HML + \beta_i^{UMD}UMD$$

**Additional Factor:**
- **UMD**: Up Minus Down (momentum factor)

### Fama-French Five-Factor Model
Adds profitability and investment factors:
$$E(R_i) = R_f + \beta_i^{MKT}(R_m - R_f) + \beta_i^{SMB}SMB + \beta_i^{HML}HML + \beta_i^{RMW}RMW + \beta_i^{CMA}CMA$$

**Additional Factors:**
- **RMW**: Robust Minus Weak (profitability)
- **CMA**: Conservative Minus Aggressive (investment)

## Custom Factor Models

### Industry Factors
- Sector-specific risk factors
- Industry momentum
- Industry rotation signals

### Style Factors
- Growth vs Value
- Quality factors
- Volatility factors
- Liquidity factors

### Macroeconomic Factors
- Interest rate changes
- Inflation expectations
- GDP growth
- Credit spreads

## Factor Construction

### Raw Factor
- Directly observable characteristic
- Examples: Market cap, P/E ratio, dividend yield

### Standardized Factor
- Z-score normalization
- Mean = 0, Std = 1
- Enables comparison across factors

### Weighted Factor
- Combination of multiple related factors
- Equal-weighted or optimized weights
- Reduces noise and improves robustness

## Factor Analysis

### Factor Exposure
- Sensitivity of asset returns to factors
- Measured by regression coefficients
- Can be time-varying

### Factor Returns
- Return attributable to each factor
- Can be positive or negative
- Used for performance attribution

### R-Squared
- Proportion of variance explained by factors
- Higher = better model fit
- Used to compare models

## Applications

### Portfolio Construction
- Factor-based portfolio optimization
- Smart beta strategies
- Risk parity approaches

### Performance Attribution
- Decompose returns into factor contributions
- Identify sources of alpha/beta
- Evaluate manager skill

### Risk Management
- Factor exposure limits
- Stress testing
- Scenario analysis

### Alpha Generation
- Identify mispriced securities
- Factor timing strategies
- Statistical arbitrage
