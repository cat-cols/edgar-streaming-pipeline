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
from financial_formulas import (
    # Ratios
    gross_margin, operating_margin, net_margin, return_on_assets, return_on_equity,
    current_ratio, quick_ratio, debt_to_equity, interest_coverage,
    # Risk metrics
    sharpe_ratio, sortino_ratio, beta,
    # Portfolio metrics
    treynor_ratio, information_ratio,
)
import yfinance as yf

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
    .healthy-metric {
        color: #2ecc71;
        font-weight: bold;
    }
    .warning-metric {
        color: #f39c12;
        font-weight: bold;
    }
    .danger-metric {
        color: #e74c3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Financial health thresholds
HEALTH_THRESHOLDS = {
    'pe_ratio': {'healthy': (0, 25), 'warning': (25, 40), 'danger': (40, float('inf'))},
    'pb_ratio': {'healthy': (0, 3), 'warning': (3, 5), 'danger': (5, float('inf'))},
    'roe': {'healthy': (0.15, float('inf')), 'warning': (0.10, 0.15), 'danger': (0, 0.10)},
    'roa': {'healthy': (0.05, float('inf')), 'warning': (0.02, 0.05), 'danger': (0, 0.02)},
    'debt_to_equity': {'healthy': (0, 1.0), 'warning': (1.0, 2.0), 'danger': (2.0, float('inf'))},
    'current_ratio': {'healthy': (1.5, float('inf')), 'warning': (1.0, 1.5), 'danger': (0, 1.0)},
    'gross_margin': {'healthy': (0.40, float('inf')), 'warning': (0.20, 0.40), 'danger': (0, 0.20)},
    'operating_margin': {'healthy': (0.15, float('inf')), 'warning': (0.08, 0.15), 'danger': (0, 0.08)},
    'net_margin': {'healthy': (0.10, float('inf')), 'warning': (0.05, 0.10), 'danger': (0, 0.05)},
    'beta': {'healthy': (0.8, 1.2), 'warning': (0.5, 0.8), 'danger': (0, 0.5)},
    'momentum_12m': {'healthy': (0.10, float('inf')), 'warning': (0.0, 0.10), 'danger': (float('-inf'), 0.0)},
}

def get_health_color(metric_name, value):
    """Return color class based on health thresholds"""
    if pd.isna(value):
        return ""
    
    if metric_name in HEALTH_THRESHOLDS:
        thresholds = HEALTH_THRESHOLDS[metric_name]
        if thresholds['healthy'][0] <= value <= thresholds['healthy'][1]:
            return "healthy-metric"
        elif thresholds['warning'][0] <= value <= thresholds['warning'][1]:
            return "warning-metric"
        else:
            return "danger-metric"
    return ""

def format_metric_with_health(value, metric_name):
    """Format metric value with health color coding"""
    if pd.isna(value):
        return "N/A"
    
    health_class = get_health_color(metric_name, value)
    
    # Format based on metric type
    if 'ratio' in metric_name or metric_name in ['pe_ratio', 'pb_ratio', 'debt_to_equity', 'beta']:
        formatted = f"{value:.2f}"
    elif metric_name in ['roe', 'roa', 'gross_margin', 'operating_margin', 'net_margin', 'momentum_12m']:
        formatted = f"{value:.1%}"
    else:
        formatted = f"{value:.2f}"
    
    if health_class:
        return f'<span class="{health_class}">{formatted}</span>'
    return formatted

# Stock Chart Functions
@st.cache_data(ttl=3600)
def fetch_stock_price_data(ticker, period="1y", interval="1d"):
    """Fetch historical price data for a stock"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

def calculate_technical_indicators_chart(data):
    """Calculate technical indicators for charting"""
    if data is None or len(data) == 0:
        return None
    
    df = data.copy()
    
    # Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * 2)
    df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * 2)
    
    # MACD
    exp12 = df['Close'].ewm(span=12, adjust=False).mean()
    exp26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp12 - exp26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    return df

def create_price_chart(df, ticker):
    """Create interactive price chart with moving averages"""
    if df is None or len(df) == 0:
        return None
    
    fig = go.Figure()
    
    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price',
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ))
    
    # Add moving averages
    if 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA_20'],
            mode='lines',
            name='SMA 20',
            line=dict(color='blue', width=1),
            opacity=0.7
        ))
    
    if 'SMA_50' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA_50'],
            mode='lines',
            name='SMA 50',
            line=dict(color='orange', width=1),
            opacity=0.7
        ))
    
    if 'SMA_200' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA_200'],
            mode='lines',
            name='SMA 200',
            line=dict(color='red', width=1),
            opacity=0.7
        ))
    
    fig.update_layout(
        title=f'{ticker} Price Chart with Moving Averages',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        height=500,
        xaxis_rangeslider_visible=False
    )
    
    return fig

def create_volume_chart(df, ticker):
    """Create volume chart"""
    if df is None or len(df) == 0:
        return None
    
    colors = ['#26a69a' if row['Close'] >= row['Open'] else '#ef5350' 
              for _, row in df.iterrows()]
    
    fig = go.Figure(data=go.Bar(
        x=df.index,
        y=df['Volume'],
        marker_color=colors,
        name='Volume'
    ))
    
    fig.update_layout(
        title=f'{ticker} Volume',
        xaxis_title='Date',
        yaxis_title='Volume',
        template='plotly_dark',
        height=300
    )
    
    return fig

def create_rsi_chart(df, ticker):
    """Create RSI indicator chart"""
    if df is None or len(df) == 0 or 'RSI' not in df.columns:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['RSI'],
        mode='lines',
        name='RSI',
        line=dict(color='purple', width=2)
    ))
    
    # Add overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
    
    fig.update_layout(
        title=f'{ticker} RSI (14)',
        xaxis_title='Date',
        yaxis_title='RSI',
        template='plotly_dark',
        height=300,
        yaxis_range=[0, 100]
    )
    
    return fig

def create_macd_chart(df, ticker):
    """Create MACD indicator chart"""
    if df is None or len(df) == 0 or 'MACD' not in df.columns:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['MACD'],
        mode='lines',
        name='MACD',
        line=dict(color='blue', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['MACD_Signal'],
        mode='lines',
        name='Signal',
        line=dict(color='orange', width=2)
    ))
    
    # Histogram
    colors = ['#26a69a' if x >= 0 else '#ef5350' for x in df['MACD_Hist']]
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['MACD_Hist'],
        name='Histogram',
        marker_color=colors,
        opacity=0.5
    ))
    
    fig.update_layout(
        title=f'{ticker} MACD',
        xaxis_title='Date',
        yaxis_title='MACD',
        template='plotly_dark',
        height=300
    )
    
    return fig

def create_bollinger_bands_chart(df, ticker):
    """Create Bollinger Bands chart"""
    if df is None or len(df) == 0 or 'BB_Upper' not in df.columns:
        return None
    
    fig = go.Figure()
    
    # Add price
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Price',
        line=dict(color='white', width=2)
    ))
    
    # Add Bollinger Bands
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['BB_Upper'],
        mode='lines',
        name='BB Upper',
        line=dict(color='rgba(255,0,0,0.5)', width=1),
        fill=None
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['BB_Lower'],
        mode='lines',
        name='BB Lower',
        line=dict(color='rgba(255,0,0,0.5)', width=1),
        fill='tonexty',
        fillcolor='rgba(255,0,0,0.1)'
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['BB_Middle'],
        mode='lines',
        name='BB Middle',
        line=dict(color='yellow', width=1, dash='dash')
    ))
    
    fig.update_layout(
        title=f'{ticker} Bollinger Bands',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        height=400
    )
    
    return fig

def display_stock_charts(ticker, period="1y", selected_indicators=None):
    """Display integrated stock chart with overlays and volume"""
    if selected_indicators is None:
        selected_indicators = ['SMA_20', 'SMA_50', 'SMA_200', 'Bollinger Bands', 'RSI', 'MACD']
    
    # Fetch price data
    price_data = fetch_stock_price_data(ticker, period=period)
    
    if price_data is None or len(price_data) == 0:
        st.warning(f"Unable to fetch price data for {ticker}")
        return
    
    # Calculate technical indicators
    df = calculate_technical_indicators_chart(price_data)
    
    # Create integrated chart with subplots
    from plotly.subplots import make_subplots
    
    # Create subplots: price chart on top, volume on bottom
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=('Price with Technical Indicators', 'Volume')
    )
    
    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price',
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ), row=1, col=1)
    
    # Add moving averages if selected
    if 'SMA_20' in selected_indicators and 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA_20'],
            mode='lines',
            name='SMA 20',
            line=dict(color='blue', width=1),
            opacity=0.7
        ), row=1, col=1)
    
    if 'SMA_50' in selected_indicators and 'SMA_50' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA_50'],
            mode='lines',
            name='SMA 50',
            line=dict(color='orange', width=1),
            opacity=0.7
        ), row=1, col=1)
    
    if 'SMA_200' in selected_indicators and 'SMA_200' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA_200'],
            mode='lines',
            name='SMA 200',
            line=dict(color='red', width=1),
            opacity=0.7
        ), row=1, col=1)
    
    # Add Bollinger Bands if selected
    if 'Bollinger Bands' in selected_indicators:
        if 'BB_Upper' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['BB_Upper'],
                mode='lines',
                name='BB Upper',
                line=dict(color='rgba(255,0,0,0.5)', width=1),
                fill=None
            ), row=1, col=1)
        
        if 'BB_Lower' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['BB_Lower'],
                mode='lines',
                name='BB Lower',
                line=dict(color='rgba(255,0,0,0.5)', width=1),
                fill='tonexty',
                fillcolor='rgba(255,0,0,0.1)'
            ), row=1, col=1)
        
        if 'BB_Middle' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['BB_Middle'],
                mode='lines',
                name='BB Middle',
                line=dict(color='yellow', width=1, dash='dash')
            ), row=1, col=1)
    
    # Add RSI on secondary y-axis if selected
    if 'RSI' in selected_indicators and 'RSI' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['RSI'],
            mode='lines',
            name='RSI',
            line=dict(color='purple', width=2),
            yaxis='y2'
        ), row=1, col=1)
    
    # Add MACD on tertiary y-axis if selected
    if 'MACD' in selected_indicators and 'MACD' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='cyan', width=1.5),
            yaxis='y3'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MACD_Signal'],
            mode='lines',
            name='MACD Signal',
            line=dict(color='magenta', width=1.5),
            yaxis='y3'
        ), row=1, col=1)
    
    # Add volume chart
    colors = ['#26a69a' if row['Close'] >= row['Open'] else '#ef5350' 
              for _, row in df.iterrows()]
    
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        marker_color=colors,
        name='Volume',
        showlegend=False
    ), row=2, col=1)
    
    # Update layout with multiple y-axes
    fig.update_layout(
        title=f'{ticker} Integrated Chart',
        template='plotly_dark',
        height=800,
        xaxis_rangeslider_visible=False,
        yaxis=dict(
            title='Price',
            side='left'
        ),
        yaxis2=dict(
            title='RSI',
            overlaying='y',
            side='right',
            range=[0, 100],
            showgrid=False,
            visible='RSI' in selected_indicators
        ),
        yaxis3=dict(
            title='MACD',
            overlaying='y',
            side='right',
            anchor='free',
            position=0.95,
            showgrid=False,
            visible='MACD' in selected_indicators
        ),
        yaxis4=dict(
            title='Volume',
            showgrid=False
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Update y-axis for volume subplot
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)

# Scoring Functions
def calculate_financial_health_score(stock_info: dict) -> int:
    """Calculate financial health score (0-100)"""
    score = 0
    
    # Current ratio (20 points)
    current_ratio = stock_info.get('currentRatio')
    if current_ratio:
        if current_ratio >= 2:
            score += 20
        elif current_ratio >= 1.5:
            score += 15
        elif current_ratio >= 1:
            score += 10
        else:
            score += 5
    
    # Debt/Equity (20 points)
    debt_to_equity = stock_info.get('debtToEquity')
    if debt_to_equity:
        if debt_to_equity <= 0.5:
            score += 20
        elif debt_to_equity <= 1:
            score += 15
        elif debt_to_equity <= 1.5:
            score += 10
        elif debt_to_equity <= 2:
            score += 5
    
    # Quick ratio (15 points)
    quick_ratio = stock_info.get('quickRatio')
    if quick_ratio:
        if quick_ratio >= 1:
            score += 15
        elif quick_ratio >= 0.5:
            score += 10
        elif quick_ratio >= 0.3:
            score += 5
    
    # Profit margin (20 points)
    profit_margin = stock_info.get('profitMargins')
    if profit_margin:
        if profit_margin >= 0.20:
            score += 20
        elif profit_margin >= 0.15:
            score += 15
        elif profit_margin >= 0.10:
            score += 10
        elif profit_margin >= 0.05:
            score += 5
    
    # ROE (25 points)
    roe = stock_info.get('returnOnEquity')
    if roe:
        if roe >= 0.20:
            score += 25
        elif roe >= 0.15:
            score += 20
        elif roe >= 0.10:
            score += 15
        elif roe >= 0.05:
            score += 10
        elif roe >= 0:
            score += 5
    
    return score

def calculate_fundamental_score(stock_info: dict) -> int:
    """Calculate fundamental analysis score (0-100)"""
    score = 0
    
    # P/E Ratio (15 points)
    pe_ratio = stock_info.get('trailingPE') or stock_info.get('forwardPE')
    if pe_ratio:
        if pe_ratio < 15:
            score += 15
        elif pe_ratio < 20:
            score += 10
        elif pe_ratio < 25:
            score += 5
    
    # ROE (25 points)
    roe = stock_info.get('returnOnEquity')
    if roe:
        if roe >= 0.20:
            score += 25
        elif roe >= 0.15:
            score += 20
        elif roe >= 0.10:
            score += 15
        elif roe >= 0.05:
            score += 10
        elif roe >= 0:
            score += 5
    
    # Profit Margin (20 points)
    profit_margin = stock_info.get('profitMargins')
    if profit_margin:
        if profit_margin >= 0.20:
            score += 20
        elif profit_margin >= 0.15:
            score += 15
        elif profit_margin >= 0.10:
            score += 10
        elif profit_margin >= 0.05:
            score += 5
    
    # Revenue Growth (20 points)
    revenue_growth = stock_info.get('revenueGrowth')
    if revenue_growth:
        if revenue_growth >= 0.20:
            score += 20
        elif revenue_growth >= 0.15:
            score += 15
        elif revenue_growth >= 0.10:
            score += 10
        elif revenue_growth >= 0.05:
            score += 5
        elif revenue_growth >= 0:
            score += 2
    
    # Debt/Equity (20 points)
    debt_to_equity = stock_info.get('debtToEquity')
    if debt_to_equity:
        if debt_to_equity <= 0.5:
            score += 20
        elif debt_to_equity <= 1:
            score += 15
        elif debt_to_equity <= 1.5:
            score += 10
        elif debt_to_equity <= 2:
            score += 5
    
    return score

def calculate_technical_score(df: pd.DataFrame) -> int:
    """Calculate technical analysis score (0-100)"""
    score = 0
    
    if df is None or len(df) == 0:
        return 50  # Neutral if no data
    
    # RSI (30 points)
    if 'RSI' in df.columns:
        current_rsi = df['RSI'].iloc[-1]
        if pd.notna(current_rsi):
            if 30 <= current_rsi <= 70:
                score += 30
            elif 25 <= current_rsi < 30 or 70 < current_rsi <= 75:
                score += 20
            elif 20 <= current_rsi < 25 or 75 < current_rsi <= 80:
                score += 10
            else:
                score += 5
    
    # MACD (30 points)
    if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
        current_macd = df['MACD'].iloc[-1]
        current_signal = df['MACD_Signal'].iloc[-1]
        if pd.notna(current_macd) and pd.notna(current_signal):
            if current_macd > current_signal:
                score += 30
            else:
                score += 10
    
    # Moving averages (40 points)
    if 'SMA_50' in df.columns and 'SMA_200' in df.columns:
        sma_50 = df['SMA_50'].iloc[-1]
        sma_200 = df['SMA_200'].iloc[-1]
        current_price = df['Close'].iloc[-1]
        
        if pd.notna(sma_50) and pd.notna(sma_200) and pd.notna(current_price):
            if current_price > sma_50 > sma_200:
                score += 40
            elif current_price > sma_50:
                score += 30
            elif sma_50 > sma_200:
                score += 20
            else:
                score += 10
    
    return score

def get_investment_recommendation(overall_score: float) -> tuple:
    """Get investment recommendation and color based on overall score"""
    if overall_score >= 80:
        return "Strong Buy", "green"
    elif overall_score >= 70:
        return "Buy", "lightgreen"
    elif overall_score >= 60:
        return "Hold", "orange"
    elif overall_score >= 40:
        return "Sell", "lightcoral"
    else:
        return "Strong Sell", "red"

# Title and description
st.markdown('<h1 class="main-header">📈 Stock Screening Dashboard</h1>', unsafe_allow_html=True)
st.markdown("""
Financial engineering approach to identifying stocks worth buying based on value, quality, momentum, and low volatility factors.
""")

# Sidebar controls
st.sidebar.header("Dashboard Controls")

# Individual Stock Analysis Section
st.sidebar.subheader("📊 Individual Stock Analysis")

# Initialize session state for stock watchlist
if 'stock_watchlist' not in st.session_state:
    st.session_state.stock_watchlist = []

# Add stock to watchlist
col_add1, col_add2 = st.sidebar.columns([3, 1])
with col_add1:
    new_stock = st.text_input("Add Stock Ticker", placeholder="AAPL", key="add_stock_input")
with col_add2:
    if st.button("Add", key="add_stock_btn"):
        if new_stock and new_stock.upper() not in st.session_state.stock_watchlist:
            st.session_state.stock_watchlist.append(new_stock.upper())
            st.rerun()

# Display watchlist
if st.session_state.stock_watchlist:
    st.sidebar.write("**Watchlist:**")
    for i, stock in enumerate(st.session_state.stock_watchlist):
        col_stock, col_remove = st.sidebar.columns([3, 1])
        with col_stock:
            st.write(f"• {stock}")
        with col_remove:
            if st.button("×", key=f"remove_{stock}"):
                st.session_state.stock_watchlist.pop(i)
                st.rerun()
else:
    st.sidebar.info("No stocks in watchlist. Add stocks above.")

# Metric Selection
st.sidebar.subheader("📈 Metric Selection")

# Fundamental metrics
fundamental_options = [
    'pe_ratio', 'pb_ratio', 'roe', 'roa', 'debt_to_equity',
    'current_ratio', 'gross_margin', 'operating_margin', 'net_margin'
]
selected_fundamental = st.sidebar.multiselect(
    "Fundamental Metrics",
    fundamental_options,
    default=['pe_ratio', 'pb_ratio', 'roe', 'debt_to_equity']
)

# Technical metrics
technical_options = [
    'beta', 'momentum_12m', 'volatility', 'rsi', 'macd',
    'sharpe_ratio', 'sortino_ratio', 'treynor_ratio'
]
selected_technical = st.sidebar.multiselect(
    "Technical Metrics",
    technical_options,
    default=['beta', 'momentum_12m']
)

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
    
    # Filter out rows with NaN composite_score for scatter plot
    scatter_df = filtered_df.dropna(subset=['composite_score', 'pe_ratio', 'roe'])
    
    if not scatter_df.empty:
        fig_scatter = px.scatter(
            scatter_df,
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
    else:
        st.warning("No valid data available for scatter plot")
    
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

# Individual Stock Analysis Section
if st.session_state.stock_watchlist:
    st.markdown("---")
    st.subheader("📊 Individual Stock Analysis")
    
    for stock_ticker in st.session_state.stock_watchlist:
        with st.expander(f"🔍 {stock_ticker} - Detailed Analysis", expanded=len(st.session_state.stock_watchlist) == 1):
            # Try to get data from screening results first
            stock_data = None
            if report_df is not None:
                stock_match = report_df[report_df['ticker'] == stock_ticker]
                if not stock_match.empty:
                    stock_data = stock_match.iloc[0]
            
            # Create columns for fundamental and technical metrics
            if selected_fundamental or selected_technical:
                if selected_fundamental and selected_technical:
                    col_fund, col_tech = st.columns(2)
                elif selected_fundamental:
                    col_fund = st.columns(1)[0]
                else:
                    col_tech = st.columns(1)[0]
                
                # Display fundamental metrics with color coding
                if selected_fundamental:
                    with col_fund if selected_technical else col_fund:
                        st.markdown("### 💰 Fundamental Analysis")
                        
                        for metric in selected_fundamental:
                            if stock_data is not None and metric in stock_data.index:
                                value = stock_data[metric]
                                display_name = metric.replace('_', ' ').title()
                                formatted_value = format_metric_with_health(value, metric)
                                st.markdown(f"**{display_name}:** {formatted_value}", unsafe_allow_html=True)
                            else:
                                st.markdown(f"**{metric.replace('_', ' ').title()}:** N/A")
                
                # Display technical metrics with color coding
                if selected_technical:
                    with col_tech if selected_fundamental else col_tech:
                        st.markdown("### 📈 Technical Analysis")
                        
                        for metric in selected_technical:
                            if stock_data is not None and metric in stock_data.index:
                                value = stock_data[metric]
                                display_name = metric.replace('_', ' ').title()
                                formatted_value = format_metric_with_health(value, metric)
                                st.markdown(f"**{display_name}:** {formatted_value}", unsafe_allow_html=True)
                            else:
                                st.markdown(f"**{metric.replace('_', ' ').title()}:** N/A")
            else:
                st.info("Select metrics from the sidebar to display analysis.")
            
            # Add financial health summary
            if stock_data is not None:
                st.markdown("---")
                st.markdown("### 🏥 Financial Health Summary")
                
                health_metrics = [m for m in (selected_fundamental + selected_technical) if m in HEALTH_THRESHOLDS]
                if health_metrics:
                    healthy_count = sum(1 for m in health_metrics if get_health_color(m, stock_data[m]) == "healthy-metric")
                    warning_count = sum(1 for m in health_metrics if get_health_color(m, stock_data[m]) == "warning-metric")
                    danger_count = sum(1 for m in health_metrics if get_health_color(m, stock_data[m]) == "danger-metric")
                    
                    col_h1, col_h2, col_h3 = st.columns(3)
                    with col_h1:
                        st.metric("Healthy", healthy_count, delta_color="normal")
                    with col_h2:
                        st.metric("Warning", warning_count, delta_color="off")
                    with col_h3:
                        st.metric("Danger", danger_count, delta_color="inverse")
                else:
                    st.info("No health thresholds defined for selected metrics.")
            
            # Add stock price charts
            st.markdown("---")
            st.markdown("### 📈 Price Charts & Technical Analysis")
            
            # Period selector for charts
            chart_period = st.selectbox(
                "Select Time Period",
                ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
                index=3,
                key=f"period_{stock_ticker}"
            )
            
            # Indicator selector
            available_indicators = ['SMA_20', 'SMA_50', 'SMA_200', 'Bollinger Bands', 'RSI', 'MACD']
            selected_indicators = st.multiselect(
                "Select Indicators to Overlay",
                available_indicators,
                default=available_indicators,
                key=f"indicators_{stock_ticker}"
            )
            
            display_stock_charts(stock_ticker, period=chart_period, selected_indicators=selected_indicators)
            
            # Add overall investment assessment
            st.markdown("---")
            st.markdown("### 🎯 Overall Investment Assessment")
            
            # Fetch stock info for scoring
            try:
                stock = yf.Ticker(stock_ticker)
                stock_info = stock.info
                
                # Calculate scores
                financial_score = calculate_financial_health_score(stock_info)
                fundamental_score = calculate_fundamental_score(stock_info)
                
                # Get price data for technical score
                price_data = fetch_stock_price_data(stock_ticker, period=chart_period)
                if price_data is not None:
                    df = calculate_technical_indicators_chart(price_data)
                    technical_score = calculate_technical_score(df)
                else:
                    technical_score = 50  # Neutral if no data
                
                # Weighted overall score
                overall_score = (financial_score * 0.35 + fundamental_score * 0.40 + technical_score * 0.25)
                
                # Get recommendation
                recommendation, color = get_investment_recommendation(overall_score)
                
                # Display scores
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Financial Health", f"{financial_score}/100")
                with col2:
                    st.metric("Fundamental", f"{fundamental_score}/100")
                with col3:
                    st.metric("Technical", f"{technical_score}/100")
                with col4:
                    st.metric("Overall Score", f"{overall_score:.1f}/100")
                
                # Recommendation
                st.markdown(f"<h2 style='text-align: center; color: {color}'>{recommendation}</h2>", unsafe_allow_html=True)
                
                # Score breakdown chart
                fig_scores = go.Figure(go.Bar(
                    x=['Financial Health', 'Fundamental', 'Technical'],
                    y=[financial_score, fundamental_score, technical_score],
                    marker_color=['#3498db', '#2ecc71', '#e74c3c']
                ))
                
                fig_scores.update_layout(
                    title='Score Breakdown',
                    yaxis_title='Score',
                    template='plotly_dark',
                    height=400,
                    yaxis=dict(range=[0, 100])
                )
                
                st.plotly_chart(fig_scores, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error calculating investment assessment: {e}")
    
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
