"""
Interactive Stock Analysis Dashboard
Allows individual stock analysis with financial health, fundamental analysis, and technical analysis
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Dashboard",
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
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .positive {
        color: green;
        font-weight: bold;
    }
    .negative {
        color: red;
        font-weight: bold;
    }
    .neutral {
        color: orange;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


class StockAnalysisDashboard:
    """Interactive dashboard for individual stock analysis"""
    
    def __init__(self):
        self.ticker = None
        self.stock = None
        self.info = None
        self.history = None
    
    def load_stock_data(self, ticker: str):
        """Load stock data from yfinance"""
        try:
            self.ticker = ticker.upper()
            self.stock = yf.Ticker(self.ticker)
            self.info = self.stock.info
            self.history = self.stock.history(period="1y")
            return True
        except Exception as e:
            st.error(f"Error loading data for {ticker}: {e}")
            return False
    
    def display_header(self):
        """Display dashboard header"""
        st.markdown(f"<h1 class='main-header'>📈 {self.ticker} Stock Analysis Dashboard</h1>", unsafe_allow_html=True)
        
        # Company info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Company Name", self.info.get('longName', 'N/A'))
        with col2:
            st.metric("Sector", self.info.get('sector', 'N/A'))
        with col3:
            st.metric("Industry", self.info.get('industry', 'N/A'))
    
    def display_price_info(self):
        """Display current price information"""
        st.subheader("💰 Current Price Information")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        current_price = self.info.get('currentPrice') or self.info.get('regularMarketPrice')
        previous_close = self.info.get('previousClose')
        change = current_price - previous_close if current_price and previous_close else 0
        change_percent = (change / previous_close * 100) if previous_close else 0
        
        with col1:
            st.metric("Current Price", f"${current_price:.2f}" if current_price else "N/A")
        with col2:
            delta_color = "normal" if change >= 0 else "inverse"
            st.metric("Change", f"${change:.2f}", delta=f"{change_percent:.2f}%", delta_color=delta_color)
        with col3:
            st.metric("52W High", f"${self.info.get('fiftyTwoWeekHigh', 0):.2f}")
        with col4:
            st.metric("52W Low", f"${self.info.get('fiftyTwoWeekLow', 0):.2f}")
        with col5:
            market_cap = self.info.get('marketCap')
            if market_cap:
                if market_cap >= 1e12:
                    st.metric("Market Cap", f"${market_cap/1e12:.2f}T")
                elif market_cap >= 1e9:
                    st.metric("Market Cap", f"${market_cap/1e9:.2f}B")
                else:
                    st.metric("Market Cap", f"${market_cap/1e6:.2f}M")
            else:
                st.metric("Market Cap", "N/A")
    
    def display_financial_health(self):
        """Display financial health analysis"""
        st.subheader("🏥 Financial Health Analysis")
        
        # Financial health metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_ratio = self.info.get('currentRatio')
            if current_ratio:
                status = "✅ Good" if current_ratio >= 2 else "⚠️ Fair" if current_ratio >= 1 else "❌ Poor"
                st.metric("Current Ratio", f"{current_ratio:.2f}", status)
            else:
                st.metric("Current Ratio", "N/A")
        
        with col2:
            debt_to_equity = self.info.get('debtToEquity')
            if debt_to_equity:
                status = "✅ Safe" if debt_to_equity <= 1 else "⚠️ Moderate" if debt_to_equity <= 2 else "❌ Risky"
                st.metric("Debt/Equity", f"{debt_to_equity:.2f}", status)
            else:
                st.metric("Debt/Equity", "N/A")
        
        with col3:
            quick_ratio = self.info.get('quickRatio')
            if quick_ratio:
                status = "✅ Good" if quick_ratio >= 1 else "⚠️ Fair" if quick_ratio >= 0.5 else "❌ Poor"
                st.metric("Quick Ratio", f"{quick_ratio:.2f}", status)
            else:
                st.metric("Quick Ratio", "N/A")
        
        with col4:
            total_debt = self.info.get('totalDebt')
            if total_debt:
                if total_debt >= 1e9:
                    st.metric("Total Debt", f"${total_debt/1e9:.2f}B")
                else:
                    st.metric("Total Debt", f"${total_debt/1e6:.2f}M")
            else:
                st.metric("Total Debt", "N/A")
        
        # Financial health score
        health_score = self.calculate_financial_health_score()
        st.markdown(f"**Financial Health Score: {health_score}/100**")
        
        if health_score >= 80:
            st.markdown("<span class='positive'>Excellent Financial Health</span>", unsafe_allow_html=True)
        elif health_score >= 60:
            st.markdown("<span class='neutral'>Good Financial Health</span>", unsafe_allow_html=True)
        elif health_score >= 40:
            st.markdown("<span class='negative'>Fair Financial Health</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='negative'>Poor Financial Health</span>", unsafe_allow_html=True)
    
    def calculate_financial_health_score(self) -> int:
        """Calculate financial health score"""
        score = 0
        
        # Current ratio (20 points)
        current_ratio = self.info.get('currentRatio')
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
        debt_to_equity = self.info.get('debtToEquity')
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
        quick_ratio = self.info.get('quickRatio')
        if quick_ratio:
            if quick_ratio >= 1:
                score += 15
            elif quick_ratio >= 0.5:
                score += 10
            elif quick_ratio >= 0.3:
                score += 5
        
        # Profit margin (20 points)
        profit_margin = self.info.get('profitMargins')
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
        roe = self.info.get('returnOnEquity')
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
    
    def display_fundamental_analysis(self):
        """Display fundamental analysis"""
        st.subheader("📊 Fundamental Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Valuation Metrics**")
            pe_ratio = self.info.get('trailingPE') or self.info.get('forwardPE')
            pb_ratio = self.info.get('priceToBook')
            ps_ratio = self.info.get('priceToSalesTrailing12Months')
            
            if pe_ratio:
                pe_status = "Undervalued" if pe_ratio < 15 else "Fair" if pe_ratio < 25 else "Overvalued"
                st.metric(f"P/E Ratio ({pe_status})", f"{pe_ratio:.2f}")
            if pb_ratio:
                st.metric("P/B Ratio", f"{pb_ratio:.2f}")
            if ps_ratio:
                st.metric("P/S Ratio", f"{ps_ratio:.2f}")
        
        with col2:
            st.markdown("**Profitability Metrics**")
            roe = self.info.get('returnOnEquity')
            roa = self.info.get('returnOnAssets')
            profit_margin = self.info.get('profitMargins')
            operating_margin = self.info.get('operatingMargins')
            
            if roe:
                st.metric("ROE", f"{roe:.2%}")
            if roa:
                st.metric("ROA", f"{roa:.2%}")
            if profit_margin:
                st.metric("Profit Margin", f"{profit_margin:.2%}")
            if operating_margin:
                st.metric("Operating Margin", f"{operating_margin:.2%}")
        
        with col3:
            st.markdown("**Growth Metrics**")
            revenue_growth = self.info.get('revenueGrowth')
            earnings_growth = self.info.get('earningsGrowth')
            earnings_quarterly_growth = self.info.get('earningsQuarterlyGrowth')
            
            if revenue_growth:
                st.metric("Revenue Growth", f"{revenue_growth:.2%}")
            if earnings_growth:
                st.metric("Earnings Growth", f"{earnings_growth:.2%}")
            if earnings_quarterly_growth:
                st.metric("Quarterly Earnings Growth", f"{earnings_quarterly_growth:.2%}")
        
        # Fundamental score
        fundamental_score = self.calculate_fundamental_score()
        st.markdown(f"**Fundamental Score: {fundamental_score}/100**")
        
        if fundamental_score >= 80:
            st.markdown("<span class='positive'>Excellent Fundamentals</span>", unsafe_allow_html=True)
        elif fundamental_score >= 60:
            st.markdown("<span class='neutral'>Good Fundamentals</span>", unsafe_allow_html=True)
        elif fundamental_score >= 40:
            st.markdown("<span class='negative'>Fair Fundamentals</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='negative'>Poor Fundamentals</span>", unsafe_allow_html=True)
    
    def calculate_fundamental_score(self) -> int:
        """Calculate fundamental analysis score"""
        score = 0
        
        # P/E Ratio (15 points)
        pe_ratio = self.info.get('trailingPE') or self.info.get('forwardPE')
        if pe_ratio:
            if pe_ratio < 15:
                score += 15
            elif pe_ratio < 20:
                score += 10
            elif pe_ratio < 25:
                score += 5
        
        # ROE (25 points)
        roe = self.info.get('returnOnEquity')
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
        profit_margin = self.info.get('profitMargins')
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
        revenue_growth = self.info.get('revenueGrowth')
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
        debt_to_equity = self.info.get('debtToEquity')
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
    
    def display_technical_analysis(self):
        """Display technical analysis"""
        st.subheader("📈 Technical Analysis")
        
        if self.history is None or self.history.empty:
            st.warning("No historical data available for technical analysis")
            return
        
        # Calculate technical indicators
        self.history['SMA_50'] = self.history['Close'].rolling(window=50).mean()
        self.history['SMA_200'] = self.history['Close'].rolling(window=200).mean()
        
        # RSI
        delta = self.history['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.history['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = self.history['Close'].ewm(span=12, adjust=False).mean()
        exp2 = self.history['Close'].ewm(span=26, adjust=False).mean()
        self.history['MACD'] = exp1 - exp2
        self.history['Signal'] = self.history['MACD'].ewm(span=9, adjust=False).mean()
        
        # Display price chart with moving averages
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=self.history.index,
            open=self.history['Open'],
            high=self.history['High'],
            low=self.history['Low'],
            close=self.history['Close'],
            name='Price'
        ))
        
        fig.add_trace(go.Scatter(
            x=self.history.index,
            y=self.history['SMA_50'],
            mode='lines',
            name='SMA 50',
            line=dict(color='orange', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=self.history.index,
            y=self.history['SMA_200'],
            mode='lines',
            name='SMA 200',
            line=dict(color='blue', width=1)
        ))
        
        fig.update_layout(
            title=f'{self.ticker} Price Chart with Moving Averages',
            xaxis_title='Date',
            yaxis_title='Price',
            template='plotly_white',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Technical indicators
        col1, col2, col3 = st.columns(3)
        
        with col1:
            current_rsi = self.history['RSI'].iloc[-1]
            if pd.notna(current_rsi):
                rsi_status = "Oversold" if current_rsi < 30 else "Overbought" if current_rsi > 70 else "Neutral"
                st.metric(f"RSI ({rsi_status})", f"{current_rsi:.2f}")
            else:
                st.metric("RSI", "N/A")
        
        with col2:
            current_macd = self.history['MACD'].iloc[-1]
            current_signal = self.history['Signal'].iloc[-1]
            if pd.notna(current_macd) and pd.notna(current_signal):
                macd_status = "Bullish" if current_macd > current_signal else "Bearish"
                st.metric(f"MACD ({macd_status})", f"{current_macd:.2f}")
            else:
                st.metric("MACD", "N/A")
        
        with col3:
            sma_50 = self.history['SMA_50'].iloc[-1]
            sma_200 = self.history['SMA_200'].iloc[-1]
            if pd.notna(sma_50) and pd.notna(sma_200):
                trend_status = "Uptrend" if sma_50 > sma_200 else "Downtrend"
                st.metric(f"50/200 SMA ({trend_status})", f"{sma_50:.2f} / {sma_200:.2f}")
            else:
                st.metric("50/200 SMA", "N/A")
        
        # Technical score
        technical_score = self.calculate_technical_score()
        st.markdown(f"**Technical Score: {technical_score}/100**")
        
        if technical_score >= 80:
            st.markdown("<span class='positive'>Bullish Technicals</span>", unsafe_allow_html=True)
        elif technical_score >= 60:
            st.markdown("<span class='neutral'>Moderately Bullish</span>", unsafe_allow_html=True)
        elif technical_score >= 40:
            st.markdown("<span class='neutral'>Neutral Technicals</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='negative'>Bearish Technicals</span>", unsafe_allow_html=True)
    
    def calculate_technical_score(self) -> int:
        """Calculate technical analysis score"""
        score = 0
        
        if self.history is None or self.history.empty:
            return 50  # Neutral if no data
        
        # RSI (30 points)
        current_rsi = self.history['RSI'].iloc[-1]
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
        current_macd = self.history['MACD'].iloc[-1]
        current_signal = self.history['Signal'].iloc[-1]
        if pd.notna(current_macd) and pd.notna(current_signal):
            if current_macd > current_signal:
                score += 30
            else:
                score += 10
        
        # Moving averages (40 points)
        sma_50 = self.history['SMA_50'].iloc[-1]
        sma_200 = self.history['SMA_200'].iloc[-1]
        current_price = self.history['Close'].iloc[-1]
        
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
    
    def display_overall_assessment(self):
        """Display overall investment assessment"""
        st.subheader("🎯 Overall Investment Assessment")
        
        financial_score = self.calculate_financial_health_score()
        fundamental_score = self.calculate_fundamental_score()
        technical_score = self.calculate_technical_score()
        
        # Weighted overall score
        overall_score = (financial_score * 0.35 + fundamental_score * 0.40 + technical_score * 0.25)
        
        # Determine recommendation
        if overall_score >= 80:
            recommendation = "Strong Buy"
            color = "green"
        elif overall_score >= 70:
            recommendation = "Buy"
            color = "lightgreen"
        elif overall_score >= 60:
            recommendation = "Hold"
            color = "orange"
        elif overall_score >= 40:
            recommendation = "Sell"
            color = "lightcoral"
        else:
            recommendation = "Strong Sell"
            color = "red"
        
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
        
        # Score breakdown
        fig = go.Figure(go.Bar(
            x=['Financial Health', 'Fundamental', 'Technical'],
            y=[financial_score, fundamental_score, technical_score],
            marker_color=['#3498db', '#2ecc71', '#e74c3c']
        ))
        
        fig.update_layout(
            title='Score Breakdown',
            yaxis_title='Score',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def run_analysis(self):
        """Run complete stock analysis"""
        self.display_header()
        self.display_price_info()
        
        tab1, tab2, tab3, tab4 = st.tabs(["Financial Health", "Fundamental Analysis", "Technical Analysis", "Overall Assessment"])
        
        with tab1:
            self.display_financial_health()
        
        with tab2:
            self.display_fundamental_analysis()
        
        with tab3:
            self.display_technical_analysis()
        
        with tab4:
            self.display_overall_assessment()


def main():
    """Main execution function"""
    st.title("📊 Interactive Stock Analysis Dashboard")
    
    # Sidebar
    st.sidebar.header("Stock Selection")
    ticker = st.sidebar.text_input("Enter Stock Ticker", value="AAPL", max_chars=10).upper()
    
    st.sidebar.header("Analysis Options")
    period = st.sidebar.selectbox("Time Period", ["1y", "6mo", "3mo", "1mo"])
    
    # Main content
    if ticker:
        dashboard = StockAnalysisDashboard()
        
        if dashboard.load_stock_data(ticker):
            dashboard.run_analysis()
        else:
            st.error(f"Could not load data for {ticker}. Please check the ticker symbol.")
    else:
        st.warning("Please enter a stock ticker symbol to begin analysis.")


if __name__ == "__main__":
    main()
