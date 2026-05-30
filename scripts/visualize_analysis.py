"""
Stock Analysis Visualization Script
Creates graphs and charts for stock valuation analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
from typing import Dict, List
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class StockAnalysisVisualizer:
    """Create visualizations for stock valuation analysis"""
    
    def __init__(self, analysis_dir: str = "data/processed/valuation", 
                 output_dir: str = "data/processed/valuation/visualizations"):
        self.analysis_dir = Path(analysis_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load analysis data
        self.analysis_data = self.load_analysis_data()
    
    def load_analysis_data(self) -> List[Dict]:
        """Load stock analysis results"""
        json_file = self.analysis_dir / "stock_analysis_results.json"
        if json_file.exists():
            with open(json_file, 'r') as f:
                return json.load(f)
        return []
    
    def create_recommendation_distribution(self):
        """Create pie chart of recommendation distribution"""
        if not self.analysis_data:
            logger.warning("No analysis data available")
            return
        
        # Count recommendations
        recommendations = [item['investment_score']['recommendation'] for item in self.analysis_data]
        rec_counts = pd.Series(recommendations).value_counts()
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = {
            'Strong Buy': '#2ecc71',
            'Buy': '#27ae60', 
            'Hold': '#f39c12',
            'Sell': '#e74c3c',
            'Strong Sell': '#c0392b'
        }
        
        rec_colors = [colors.get(rec, '#95a5a6') for rec in rec_counts.index]
        
        wedges, texts, autotexts = ax.pie(rec_counts.values, labels=rec_counts.index, 
                                          autopct='%1.1f%%', colors=rec_colors, startangle=90)
        
        ax.set_title('Investment Recommendation Distribution', fontsize=16, fontweight='bold')
        ax.axis('equal')
        
        # Save
        plt.tight_layout()
        plt.savefig(self.output_dir / 'recommendation_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Created recommendation distribution chart")
    
    def create_score_distribution(self):
        """Create histogram of overall scores"""
        if not self.analysis_data:
            return
        
        scores = [item['investment_score']['overall_score'] for item in self.analysis_data]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.hist(scores, bins=20, color='#3498db', edgecolor='black', alpha=0.7)
        ax.axvline(x=50, color='red', linestyle='--', linewidth=2, label='Neutral (50)')
        ax.axvline(x=70, color='green', linestyle='--', linewidth=2, label='Buy Threshold (70)')
        ax.axvline(x=30, color='orange', linestyle='--', linewidth=2, label='Sell Threshold (30)')
        
        ax.set_xlabel('Overall Score', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Stocks', fontsize=12, fontweight='bold')
        ax.set_title('Distribution of Investment Scores', fontsize=16, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'score_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Created score distribution chart")
    
    def create_valuation_metrics_comparison(self):
        """Create comparison chart of key valuation metrics"""
        if not self.analysis_data:
            return
        
        # Extract key metrics
        metrics_data = []
        for item in self.analysis_data:
            metrics_data.append({
                'ticker': item['ticker'],
                'pe_ratio': item.get('pe_ratio'),
                'pb_ratio': item.get('pb_ratio'),
                'roe': item.get('roe'),
                'debt_to_equity': item.get('debt_to_equity'),
                'score': item['investment_score']['overall_score']
            })
        
        df = pd.DataFrame(metrics_data)
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # P/E Ratio
        ax1 = axes[0, 0]
        df_sorted = df.sort_values('pe_ratio', ascending=True).head(15)
        ax1.barh(df_sorted['ticker'], df_sorted['pe_ratio'], color='#3498db')
        ax1.axvline(x=15, color='green', linestyle='--', linewidth=2, label='Undervalued (15)')
        ax1.axvline(x=25, color='red', linestyle='--', linewidth=2, label='Overvalued (25)')
        ax1.set_xlabel('P/E Ratio', fontweight='bold')
        ax1.set_title('P/E Ratio by Stock', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # ROE
        ax2 = axes[0, 1]
        df_sorted = df.sort_values('roe', ascending=False).head(15)
        ax2.barh(df_sorted['ticker'], df_sorted['roe'], color='#2ecc71')
        ax2.axvline(x=0.15, color='green', linestyle='--', linewidth=2, label='Good (15%)')
        ax2.axvline(x=0.20, color='blue', linestyle='--', linewidth=2, label='Excellent (20%)')
        ax2.set_xlabel('Return on Equity', fontweight='bold')
        ax2.set_title('ROE by Stock', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Debt/Equity
        ax3 = axes[1, 0]
        df_sorted = df.sort_values('debt_to_equity', ascending=True).head(15)
        ax3.barh(df_sorted['ticker'], df_sorted['debt_to_equity'], color='#e74c3c')
        ax3.axvline(x=1.0, color='green', linestyle='--', linewidth=2, label='Safe (1.0)')
        ax3.axvline(x=2.0, color='red', linestyle='--', linewidth=2, label='Risky (2.0)')
        ax3.set_xlabel('Debt to Equity Ratio', fontweight='bold')
        ax3.set_title('Debt/Equity by Stock', fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Overall Score
        ax4 = axes[1, 1]
        df_sorted = df.sort_values('score', ascending=False).head(15)
        colors = ['#2ecc71' if score >= 70 else '#f39c12' if score >= 50 else '#e74c3c' 
                  for score in df_sorted['score']]
        ax4.barh(df_sorted['ticker'], df_sorted['score'], color=colors)
        ax4.axvline(x=70, color='green', linestyle='--', linewidth=2, label='Buy Threshold')
        ax4.axvline(x=50, color='orange', linestyle='--', linewidth=2, label='Hold Threshold')
        ax4.set_xlabel('Overall Score', fontweight='bold')
        ax4.set_title('Investment Score by Stock', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'valuation_metrics_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Created valuation metrics comparison chart")
    
    def create_scatter_analysis(self):
        """Create scatter plots for analysis"""
        if not self.analysis_data:
            return
        
        # Extract data
        metrics_data = []
        for item in self.analysis_data:
            metrics_data.append({
                'ticker': item['ticker'],
                'pe_ratio': item.get('pe_ratio'),
                'roe': item.get('roe'),
                'score': item['investment_score']['overall_score'],
                'recommendation': item['investment_score']['recommendation']
            })
        
        df = pd.DataFrame(metrics_data)
        df = df.dropna()
        
        # Create scatter plots
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # P/E vs ROE
        ax1 = axes[0]
        rec_colors = {
            'Strong Buy': '#2ecc71',
            'Buy': '#27ae60',
            'Hold': '#f39c12',
            'Sell': '#e74c3c',
            'Strong Sell': '#c0392b'
        }
        
        for rec in df['recommendation'].unique():
            rec_data = df[df['recommendation'] == rec]
            ax1.scatter(rec_data['pe_ratio'], rec_data['roe'], 
                       c=rec_colors.get(rec, '#95a5a6'), label=rec, alpha=0.7, s=100)
        
        # Add ticker labels for top stocks
        top_stocks = df.nlargest(5, 'score')
        for _, row in top_stocks.iterrows():
            ax1.annotate(row['ticker'], (row['pe_ratio'], row['roe']), 
                        fontsize=8, fontweight='bold')
        
        ax1.set_xlabel('P/E Ratio', fontweight='bold')
        ax1.set_ylabel('Return on Equity', fontweight='bold')
        ax1.set_title('P/E Ratio vs ROE', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Score vs P/E
        ax2 = axes[1]
        for rec in df['recommendation'].unique():
            rec_data = df[df['recommendation'] == rec]
            ax2.scatter(rec_data['pe_ratio'], rec_data['score'], 
                       c=rec_colors.get(rec, '#95a5a6'), label=rec, alpha=0.7, s=100)
        
        # Add ticker labels for top stocks
        for _, row in top_stocks.iterrows():
            ax2.annotate(row['ticker'], (row['pe_ratio'], row['score']), 
                        fontsize=8, fontweight='bold')
        
        ax2.set_xlabel('P/E Ratio', fontweight='bold')
        ax2.set_ylabel('Investment Score', fontweight='bold')
        ax2.set_title('P/E Ratio vs Investment Score', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'scatter_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Created scatter analysis charts")
    
    def create_top_bottom_stocks(self):
        """Create comparison of top and bottom stocks"""
        if not self.analysis_data:
            return
        
        # Sort by score
        sorted_data = sorted(self.analysis_data, key=lambda x: x['investment_score']['overall_score'], reverse=True)
        top_5 = sorted_data[:5]
        bottom_5 = sorted_data[-5:]
        
        # Create comparison chart
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Top 5
        ax1 = axes[0]
        tickers = [item['ticker'] for item in top_5]
        scores = [item['investment_score']['overall_score'] for item in top_5]
        prices = [item['current_price'] for item in top_5]
        
        x = np.arange(len(tickers))
        width = 0.35
        
        ax1.bar(x - width/2, scores, width, label='Score', color='#2ecc71')
        ax1.axhline(y=70, color='green', linestyle='--', linewidth=2, label='Buy Threshold')
        
        ax1.set_xlabel('Stock', fontweight='bold')
        ax1.set_ylabel('Score', fontweight='bold')
        ax1.set_title('Top 5 Stocks by Investment Score', fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(tickers)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Add price labels
        for i, (ticker, price) in enumerate(zip(tickers, prices)):
            ax1.text(i, scores[i] + 2, f'${price:.2f}', ha='center', fontweight='bold')
        
        # Bottom 5
        ax2 = axes[1]
        tickers = [item['ticker'] for item in bottom_5]
        scores = [item['investment_score']['overall_score'] for item in bottom_5]
        prices = [item['current_price'] for item in bottom_5]
        
        x = np.arange(len(tickers))
        
        ax2.bar(x - width/2, scores, width, label='Score', color='#e74c3c')
        ax2.axhline(y=30, color='orange', linestyle='--', linewidth=2, label='Sell Threshold')
        
        ax2.set_xlabel('Stock', fontweight='bold')
        ax2.set_ylabel('Score', fontweight='bold')
        ax2.set_title('Bottom 5 Stocks by Investment Score', fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(tickers)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Add price labels
        for i, (ticker, price) in enumerate(zip(tickers, prices)):
            ax2.text(i, scores[i] + 2, f'${price:.2f}', ha='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'top_bottom_stocks.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Created top/bottom stocks comparison chart")
    
    def create_radar_chart(self):
        """Create radar chart for top stock"""
        if not self.analysis_data:
            return
        
        # Get top stock
        top_stock = max(self.analysis_data, key=lambda x: x['investment_score']['overall_score'])
        
        # Extract valuation scores
        scores = top_stock.get('valuation_scores', {})
        
        if not scores:
            logger.warning("No valuation scores available for radar chart")
            return
        
        # Prepare data
        categories = list(scores.keys())
        values = list(scores.values())
        
        # Create radar chart
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Number of variables
        N = len(categories)
        
        # Compute angle for each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        # Add values
        values += values[:1]
        
        # Plot
        ax.plot(angles, values, 'o-', linewidth=2, color='#3498db')
        ax.fill(angles, values, alpha=0.25, color='#3498db')
        
        # Add category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=12)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], size=8)
        ax.grid(True)
        
        plt.title(f'Valuation Scores: {top_stock["ticker"]}\nScore: {top_stock["investment_score"]["overall_score"]}/100',
                 size=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / f'{top_stock["ticker"]}_radar_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Created radar chart for {top_stock['ticker']}")
    
    def create_summary_dashboard(self):
        """Create a summary dashboard with multiple charts"""
        if not self.analysis_data:
            return
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Recommendation distribution (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        recommendations = [item['investment_score']['recommendation'] for item in self.analysis_data]
        rec_counts = pd.Series(recommendations).value_counts()
        colors = {
            'Strong Buy': '#2ecc71',
            'Buy': '#27ae60',
            'Hold': '#f39c12',
            'Sell': '#e74c3c',
            'Strong Sell': '#c0392b'
        }
        rec_colors = [colors.get(rec, '#95a5a6') for rec in rec_counts.index]
        ax1.pie(rec_counts.values, labels=rec_counts.index, autopct='%1.1f%%', 
                colors=rec_colors, startangle=90)
        ax1.set_title('Recommendation Distribution', fontweight='bold')
        
        # 2. Score distribution (top middle)
        ax2 = fig.add_subplot(gs[0, 1])
        scores = [item['investment_score']['overall_score'] for item in self.analysis_data]
        ax2.hist(scores, bins=15, color='#3498db', edgecolor='black', alpha=0.7)
        ax2.axvline(x=50, color='red', linestyle='--', linewidth=2)
        ax2.set_xlabel('Score', fontweight='bold')
        ax2.set_ylabel('Count', fontweight='bold')
        ax2.set_title('Score Distribution', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # 3. Top stocks bar chart (top right)
        ax3 = fig.add_subplot(gs[0, 2])
        sorted_data = sorted(self.analysis_data, key=lambda x: x['investment_score']['overall_score'], reverse=True)[:10]
        tickers = [item['ticker'] for item in sorted_data]
        scores = [item['investment_score']['overall_score'] for item in sorted_data]
        colors = ['#2ecc71' if score >= 70 else '#f39c12' if score >= 50 else '#e74c3c' for score in scores]
        ax3.barh(tickers, scores, color=colors)
        ax3.set_xlabel('Score', fontweight='bold')
        ax3.set_title('Top 10 Stocks', fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # 4. P/E ratio comparison (middle left)
        ax4 = fig.add_subplot(gs[1, :2])
        pe_data = [(item['ticker'], item.get('pe_ratio')) for item in self.analysis_data if item.get('pe_ratio')]
        pe_data.sort(key=lambda x: x[1])
        pe_data = pe_data[:15]
        if pe_data:
            tickers, pe_ratios = zip(*pe_data)
            ax4.barh(tickers, pe_ratios, color='#3498db')
            ax4.axvline(x=15, color='green', linestyle='--', linewidth=2, label='Undervalued')
            ax4.axvline(x=25, color='red', linestyle='--', linewidth=2, label='Overvalued')
            ax4.set_xlabel('P/E Ratio', fontweight='bold')
            ax4.set_title('P/E Ratio Comparison (Lowest 15)', fontweight='bold')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        
        # 5. ROE comparison (middle right)
        ax5 = fig.add_subplot(gs[1, 2])
        roe_data = [(item['ticker'], item.get('roe')) for item in self.analysis_data if item.get('roe')]
        roe_data.sort(key=lambda x: x[1], reverse=True)
        roe_data = roe_data[:10]
        if roe_data:
            tickers, roe_ratios = zip(*roe_data)
            ax5.barh(tickers, roe_ratios, color='#2ecc71')
            ax5.axvline(x=0.15, color='green', linestyle='--', linewidth=2, label='Good')
            ax5.axvline(x=0.20, color='blue', linestyle='--', linewidth=2, label='Excellent')
            ax5.set_xlabel('ROE', fontweight='bold')
            ax5.set_title('ROE Comparison (Top 10)', fontweight='bold')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
        
        # 6. Summary statistics (bottom)
        ax6 = fig.add_subplot(gs[2, :])
        ax6.axis('off')
        
        # Calculate statistics
        total_stocks = len(self.analysis_data)
        avg_score = np.mean([item['investment_score']['overall_score'] for item in self.analysis_data])
        pe_values = [item.get('pe_ratio') for item in self.analysis_data if item.get('pe_ratio')]
        avg_pe = np.mean(pe_values) if pe_values else None
        roe_values = [item.get('roe') for item in self.analysis_data if item.get('roe')]
        avg_roe = np.mean(roe_values) if roe_values else None
        
        strong_buy = sum(1 for item in self.analysis_data if item['investment_score']['recommendation'] == 'Strong Buy')
        buy = sum(1 for item in self.analysis_data if item['investment_score']['recommendation'] == 'Buy')
        hold = sum(1 for item in self.analysis_data if item['investment_score']['recommendation'] == 'Hold')
        sell = sum(1 for item in self.analysis_data if item['investment_score']['recommendation'] == 'Sell')
        strong_sell = sum(1 for item in self.analysis_data if item['investment_score']['recommendation'] == 'Strong Sell')
        
        avg_pe_str = f"{avg_pe:.2f}" if avg_pe else "N/A"
        avg_roe_str = f"{avg_roe:.2%}" if avg_roe else "N/A"
        
        summary_text = f"""
        ANALYSIS SUMMARY
        {'=' * 80}
        Total Stocks Analyzed: {total_stocks}
        Average Investment Score: {avg_score:.2f}/100
        Average P/E Ratio: {avg_pe_str}
        Average ROE: {avg_roe_str}
        
        RECOMMENDATION BREAKDOWN:
        Strong Buy: {strong_buy} ({strong_buy/total_stocks*100:.1f}%)
        Buy: {buy} ({buy/total_stocks*100:.1f}%)
        Hold: {hold} ({hold/total_stocks*100:.1f}%)
        Sell: {sell} ({sell/total_stocks*100:.1f}%)
        Strong Sell: {strong_sell} ({strong_sell/total_stocks*100:.1f}%)
        {'=' * 80}
        """
        
        ax6.text(0.1, 0.5, summary_text, fontsize=12, family='monospace',
                verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.suptitle('Stock Valuation Analysis Dashboard', fontsize=20, fontweight='bold')
        plt.savefig(self.output_dir / 'summary_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Created summary dashboard")
    
    def create_all_visualizations(self):
        """Create all visualizations"""
        logger.info("Creating all visualizations...")
        
        self.create_recommendation_distribution()
        self.create_score_distribution()
        self.create_valuation_metrics_comparison()
        self.create_scatter_analysis()
        self.create_top_bottom_stocks()
        self.create_radar_chart()
        self.create_summary_dashboard()
        
        logger.info(f"All visualizations saved to {self.output_dir}")


def main():
    """Main execution function"""
    visualizer = StockAnalysisVisualizer()
    visualizer.create_all_visualizations()
    logger.info("Visualization creation completed")


if __name__ == "__main__":
    main()
