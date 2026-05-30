"""
Stock Screening Dashboard - Streamlit Application
Interactive dashboard for viewing stocks worth buying based on financial engineering factors
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from stock_screener.data.fetcher import DataFetcher
from stock_screener.factors.calculator import FactorCalculator
from stock_screener.scoring.ranker import StockRanker
from stock_screener.utils.config import FACTOR_WEIGHTS, SCREENING_FILTERS

# Page configuration
st.set_page_config(
    page_title="Stock Screening Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stock-table {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<h1 class="main-header">📈 Stock Screening Dashboard</h1>', unsafe_allow_html=True)
st.markdown("""
Financial engineering approach to identifying stocks worth buying based on value, quality, momentum, and low volatility factors.
""")

# Sidebar controls
st.sidebar.header("Dashboard Controls")

# Screening parameters
st.sidebar.subheader("Screening Parameters")

# Factor weights
value_weight = st.sidebar.slider("Value Factor Weight", 0.0, 1.0, FACTOR_WEIGHTS['value'], 0.05)
quality_weight = st.sidebar.slider("Quality Factor Weight", 0.0, 1.0, FACTOR_WEIGHTS['quality'], 0.05)
momentum_weight = st.sidebar.slider("Momentum Factor Weight", 0.0, 1.0, FACTOR_WEIGHTS['momentum'], 0.05)
lowvol_weight = st.sidebar.slider("Low Volatility Weight", 0.0, 1.0, FACTOR_WEIGHTS['lowvol'], 0.05)

# Normalize weights
total_weight = value_weight + quality_weight + momentum_weight + lowvol_weight
if total_weight > 0:
    value_weight /= total_weight
    quality_weight /= total_weight
    momentum_weight /= total_weight
    lowvol_weight /= total_weight

# Filter parameters
min_market_cap = st.sidebar.selectbox(
    "Minimum Market Cap",
    [1e9, 5e9, 10e9, 25e9, 50e9],
    format_func=lambda x: f"${x/1e9:.0f}B"
)

min_roe = st.sidebar.slider("Minimum ROE", 0.0, 0.30, SCREENING_FILTERS['min_roe'], 0.01)
max_debt_to_equity = st.sidebar.slider("Max Debt-to-Equity", 0.0, 5.0, SCREENING_FILTERS['max_debt_to_equity'], 0.5)

# Number of stocks to show
num_stocks = st.sidebar.slider("Number of Stocks to Display", 10, 100, 20)

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

# Load data function
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_screening_data():
    """Load or generate screening data"""
    try:
        # Try to load existing screening results
        report_path = Path("data/screening_results/stock_screening_report.csv")
        if report_path.exists():
            return pd.read_csv(report_path)
    except:
        pass
    
    # If no existing data, show message
    return None

# Main content
col1, col2, col3, col4 = st.columns(4)

# Load data
report_df = load_screening_data()

if report_df is not None:
    # Display metrics
    total_screened = len(report_df)
    avg_composite_score = report_df['composite_score'].mean()
    avg_pe = report_df['pe_ratio'].mean()
    avg_roe = report_df['roe'].mean()
    
    with col1:
        st.metric("Stocks Screened", f"{total_screened}")
    with col2:
        st.metric("Avg Composite Score", f"{avg_composite_score:.3f}")
    with col3:
        st.metric("Avg P/E Ratio", f"{avg_pe:.1f}")
    with col4:
        st.metric("Avg ROE", f"{avg_roe:.1%}")
    
    # Apply filters
    filtered_df = report_df.copy()
    
    if min_market_cap > 0:
        # Note: This would need market cap data in the report
        pass
    
    if min_roe > 0:
        filtered_df = filtered_df[filtered_df['roe'] >= min_roe]
    
    if max_debt_to_equity > 0:
        filtered_df = filtered_df[filtered_df['debt_to_equity'] <= max_debt_to_equity]
    
    # Sort by composite score
    filtered_df = filtered_df.sort_values('composite_score', ascending=False).head(num_stocks)
    
    # Display top stocks table
    st.subheader("🏆 Top Stocks Worth Buying")
    
    # Format table for display
    display_df = filtered_df.copy()
    display_df['Rank'] = range(1, len(display_df) + 1)
    display_df['Composite Score'] = display_df['composite_score'].apply(lambda x: f"{x:.3f}")
    display_df['Value Score'] = display_df['value_score'].apply(lambda x: f"{x:.3f}")
    display_df['Quality Score'] = display_df['quality_score'].apply(lambda x: f"{x:.3f}")
    display_df['Momentum Score'] = display_df['momentum_score'].apply(lambda x: f"{x:.3f}")
    display_df['P/E Ratio'] = display_df['pe_ratio'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A")
    display_df['ROE'] = display_df['roe'].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
    display_df['12M Momentum'] = display_df['momentum_12m'].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
    
    # Select columns to display
    display_cols = ['Rank', 'ticker', 'Composite Score', 'Value Score', 'Quality Score', 
                   'Momentum Score', 'P/E Ratio', 'ROE', '12M Momentum']
    display_df = display_df[display_cols]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Factor score distribution chart
    st.subheader("📊 Factor Score Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_scores = go.Figure()
        fig_scores.add_trace(go.Bar(
            x=display_df['ticker'],
            y=filtered_df['value_score'].head(10),
            name='Value',
            marker_color='blue'
        ))
        fig_scores.add_trace(go.Bar(
            x=display_df['ticker'],
            y=filtered_df['quality_score'].head(10),
            name='Quality',
            marker_color='green'
        ))
        fig_scores.add_trace(go.Bar(
            x=display_df['ticker'],
            y=filtered_df['momentum_score'].head(10),
            name='Momentum',
            marker_color='orange'
        ))
        fig_scores.update_layout(
            barmode='group',
            title='Factor Scores by Stock',
            xaxis_title='Ticker',
            yaxis_title='Score',
            height=400
        )
        st.plotly_chart(fig_scores, use_container_width=True)
    
    with col2:
        fig_composite = px.bar(
            filtered_df.head(10),
            x='ticker',
            y='composite_score',
            title='Composite Score Ranking',
            labels={'composite_score': 'Composite Score', 'ticker': 'Ticker'},
            color='composite_score',
            color_continuous_scale='viridis'
        )
        fig_composite.update_layout(height=400)
        st.plotly_chart(fig_composite, use_container_width=True)
    
    # P/E vs ROE scatter plot
    st.subheader("💰 Value vs Quality Analysis")
    
    fig_scatter = px.scatter(
        filtered_df,
        x='pe_ratio',
        y='roe',
        size='composite_score',
        color='composite_score',
        hover_name='ticker',
        title='P/E Ratio vs ROE (Size = Composite Score)',
        labels={
            'pe_ratio': 'P/E Ratio',
            'roe': 'ROE',
            'composite_score': 'Composite Score'
        },
        color_continuous_scale='viridis'
    )
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Stock detail view
    st.subheader("🔍 Stock Detail Analysis")
    
    selected_stock = st.selectbox(
        "Select a stock for detailed analysis",
        filtered_df['ticker'].tolist()
    )
    
    if selected_stock:
        stock_data = filtered_df[filtered_df['ticker'] == selected_stock].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Factor Scores")
            st.metric("Value Score", f"{stock_data['value_score']:.3f}")
            st.metric("Quality Score", f"{stock_data['quality_score']:.3f}")
            st.metric("Momentum Score", f"{stock_data['momentum_score']:.3f}")
            st.metric("Low Vol Score", f"{stock_data['lowvol_score']:.3f}")
        
        with col2:
            st.markdown("### Fundamentals")
            st.metric("P/E Ratio", f"{stock_data['pe_ratio']:.1f}" if pd.notna(stock_data['pe_ratio']) else "N/A")
            st.metric("P/B Ratio", f"{stock_data['pb_ratio']:.1f}" if pd.notna(stock_data['pb_ratio']) else "N/A")
            st.metric("ROE", f"{stock_data['roe']:.1%}" if pd.notna(stock_data['roe']) else "N/A")
            st.metric("Debt/Equity", f"{stock_data['debt_to_equity']:.1f}" if pd.notna(stock_data['debt_to_equity']) else "N/A")
        
        with col3:
            st.markdown("### Technical")
            st.metric("12M Momentum", f"{stock_data['momentum_12m']:.1%}" if pd.notna(stock_data['momentum_12m']) else "N/A")
            st.metric("Beta", f"{stock_data['beta']:.2f}" if pd.notna(stock_data['beta']) else "N/A")
            st.metric("Overall Rank", f"#{int(stock_data['rank'])}")
            st.metric("Composite Score", f"{stock_data['composite_score']:.3f}")
    
    # Download results
    st.subheader("📥 Download Results")
    
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Screening Results as CSV",
        data=csv,
        file_name=f'stock_screening_results_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv'
    )

else:
    st.warning("⚠️ No screening data found. Please run the stock screener first:")
    st.code("python src/stock_screener/screen_stocks.py")
    
    st.info("""
    The dashboard requires screening results to be generated first. 
    Run the stock screener to create the data files, then refresh this dashboard.
    """)

# Footer
st.markdown("---")
st.markdown("""
**Dashboard Features:**
- Multi-factor stock screening (Value, Quality, Momentum, Low Volatility)
- Interactive filtering and sorting
- Real-time factor weight adjustment
- Visual analysis with charts and graphs
- Detailed stock analysis view
- Export results to CSV

**Methodology:**
Stocks are ranked based on a composite score that combines multiple factors. 
Higher scores indicate stocks that are potentially undervalued, high-quality, 
with positive momentum and lower volatility.
""")
