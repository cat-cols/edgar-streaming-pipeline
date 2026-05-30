# Stock Screening Dashboard

Interactive Streamlit dashboard for viewing stocks worth buying based on financial engineering factors.

## Overview

This dashboard provides an interactive interface to explore stocks that have been screened using multi-factor analysis. It visualizes factor scores, fundamental metrics, and provides tools for filtering and analyzing potential investment opportunities.

## Features

- **Interactive Filtering**: Adjust factor weights and screening parameters in real-time
- **Visual Analytics**: Charts showing factor score distributions and relationships
- **Stock Rankings**: Top stocks ranked by composite score
- **Detail View**: In-depth analysis of individual stocks
- **Export Functionality**: Download screening results as CSV
- **Real-time Updates**: Refresh data with a single click

## Installation

### Requirements

```bash
pip install streamlit plotly pandas numpy yfinance
```

### Running the Dashboard

1. First, generate screening data:
```bash
python src/stock_screener/screen_stocks.py
```

2. Then run the dashboard:
```bash
streamlit run src/dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Dashboard Components

### Sidebar Controls

**Factor Weights**
- Value Factor Weight (0-100%)
- Quality Factor Weight (0-100%)
- Momentum Factor Weight (0-100%)
- Low Volatility Weight (0-100%)

**Screening Parameters**
- Minimum Market Cap ($1B - $50B)
- Minimum ROE (0-30%)
- Max Debt-to-Equity (0-5x)

**Display Options**
- Number of stocks to display (10-100)
- Refresh button to update data

### Main Display

**Metrics Overview**
- Total stocks screened
- Average composite score
- Average P/E ratio
- Average ROE

**Top Stocks Table**
- Rank, ticker, and factor scores
- Fundamental metrics (P/E, ROE)
- Momentum indicators
- Sortable by any column

**Visualizations**
- Factor Score Distribution (bar chart)
- Composite Score Ranking
- P/E vs ROE scatter plot
- Size represents composite score

**Stock Detail Analysis**
- Individual stock breakdown
- Factor scores
- Fundamental metrics
- Technical indicators
- Overall ranking

## Factor Model

The dashboard uses a multi-factor model combining:

### Value Factors (30% default)
- P/E Ratio (lower = better)
- P/B Ratio (lower = better)
- EV/EBITDA (lower = better)
- Dividend Yield (higher = better)

### Quality Factors (30% default)
- ROE (higher = better)
- ROA (higher = better)
- Profit Margins (higher = better)
- Debt-to-Equity (lower = better)

### Momentum Factors (25% default)
- 3-Month Price Momentum
- 6-Month Price Momentum
- 12-Month Price Momentum
- Technical Indicators (RSI, Moving Averages)

### Low Volatility Factors (15% default)
- Beta (lower = better)
- Historical Volatility (lower = better)

## Usage Workflow

1. **Generate Screening Data**
   ```bash
   python src/stock_screener/screen_stocks.py
   ```
   This creates the screening results in `data/screening_results/`

2. **Launch Dashboard**
   ```bash
   streamlit run src/dashboard/app.py
   ```

3. **Explore Results**
   - Adjust factor weights in sidebar
   - Apply screening filters
   - View top-ranked stocks
   - Analyze individual stocks

4. **Export Data**
   - Use download button to export results
   - CSV format for further analysis

## Customization

### Modify Factor Weights

Edit `src/stock_screener/utils/config.py`:

```python
FACTOR_WEIGHTS = {
    'value': 0.3,
    'quality': 0.3,
    'momentum': 0.25,
    'lowvol': 0.15,
}
```

### Add New Filters

Edit the filtering logic in `src/dashboard/app.py`:

```python
# Add custom filters
if custom_filter_condition:
    filtered_df = filtered_df[condition]
```

### Customize Visualizations

Modify the Plotly charts in `src/dashboard/app.py` to add new visualizations or change existing ones.

## Data Sources

- **Stock Universe**: SEC EDGAR company_tickers.json (10,000+ stocks)
- **Price Data**: Yahoo Finance via yfinance
- **Fundamentals**: Yahoo Finance via yfinance
- **Technical Indicators**: Calculated from price data

## Integration with EDGAR Pipeline

The dashboard integrates with your EDGAR streaming pipeline:

1. Uses the compiled asset universe
2. Can be enhanced with SEC filing analysis
3. Supports factor models based on fundamental data
4. Enables systematic stock selection

## Performance Considerations

- Data is cached for 1 hour to improve performance
- Initial load may take 10-30 seconds depending on data size
- Refreshing data re-runs the screening process
- For large universes, consider using a subset for faster performance

## Troubleshooting

### No Data Found
If you see "No screening data found", run the stock screener first:
```bash
python src/stock_screener/screen_stocks.py
```

### Slow Performance
- Reduce the number of stocks displayed
- Use a smaller sample size in the screener
- Clear browser cache

### Chart Not Displaying
- Ensure Plotly is installed: `pip install plotly`
- Check browser console for errors
- Try refreshing the page

## Future Enhancements

- Real-time price updates
- Sector analysis views
- Portfolio tracking
- Backtesting visualization
- Alert system for new opportunities
- Mobile-responsive design
- User authentication
- Custom watchlists

## Security Notes

- Dashboard runs locally by default
- No data is transmitted externally
- Suitable for personal use
- For production deployment, consider authentication and HTTPS

## Support

For issues or questions:
1. Check the stock screener documentation
2. Review the troubleshooting section
3. Verify data files exist in `data/screening_results/`
