"""
Visualization module for Brent oil price analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Optional, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OilPriceVisualizer:
    """Creates visualizations for Brent oil price analysis."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize visualizer.
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with Date, Price, and other columns
        """
        self.df = df.copy()
        self.set_style()
    
    def set_style(self, style: str = 'seaborn-v0_8-darkgrid'):
        """Set matplotlib style."""
        plt.style.use(style)
        sns.set_palette("husl")
    
    def plot_price_timeline(self, 
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot price timeline with optional date range.
        
        Parameters:
        -----------
        start_date : str, optional
            Start date in 'YYYY-MM-DD' format
        end_date : str, optional
            End date in 'YYYY-MM-DD' format
        save_path : str, optional
            Path to save the figure
            
        Returns:
        --------
        plt.Figure
            Matplotlib figure object
        """
        # Filter data if dates provided
        plot_df = self.df.copy()
        if start_date:
            plot_df = plot_df[plot_df['Date'] >= pd.to_datetime(start_date)]
        if end_date:
            plot_df = plot_df[plot_df['Date'] <= pd.to_datetime(end_date)]
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Plot price
        ax.plot(plot_df['Date'], plot_df['Price'], 
               linewidth=0.5, alpha=0.7, label='Daily Price')
        
        # Add rolling average
        if 'MA_30' in plot_df.columns:
            ax.plot(plot_df['Date'], plot_df['MA_30'],
                   linewidth=2, color='red', alpha=0.8, label='30-day MA')
        
        # Formatting
        ax.set_title('Brent Crude Oil Price Timeline', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price (USD/barrel)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Add price range annotation
        max_price = plot_df['Price'].max()
        min_price = plot_df['Price'].min()
        ax.annotate(f'Max: ${max_price:.2f}', 
                   xy=(plot_df.loc[plot_df['Price'].idxmax(), 'Date'], max_price),
                   xytext=(10, 10), textcoords='offset points',
                   arrowprops=dict(arrowstyle='->', color='red'),
                   fontsize=10, color='red')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Timeline plot saved to {save_path}")
        
        return fig
    
    def plot_volatility_analysis(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot volatility analysis.
        
        Parameters:
        -----------
        save_path : str, optional
            Path to save the figure
            
        Returns:
        --------
        plt.Figure
            Matplotlib figure object
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Ensure volatility calculated
        if 'Volatility' not in self.df.columns:
            self.df['Returns'] = self.df['Price'].pct_change() * 100
            self.df['Volatility'] = self.df['Returns'].rolling(30).std() * np.sqrt(252)
        
        # 1. Volatility over time
        axes[0, 0].plot(self.df['Date'], self.df['Volatility'], linewidth=0.5)
        axes[0, 0].set_title('30-Day Rolling Volatility (Annualized)', fontweight='bold')
        axes[0, 0].set_xlabel('Date')
        axes[0, 0].set_ylabel('Volatility')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Volatility histogram
        axes[0, 1].hist(self.df['Volatility'].dropna(), bins=50, edgecolor='black', alpha=0.7)
        axes[0, 1].set_title('Volatility Distribution', fontweight='bold')
        axes[0, 1].set_xlabel('Volatility')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Returns vs volatility
        axes[1, 0].scatter(self.df['Returns'], self.df['Volatility'], 
                          alpha=0.3, s=1)
        axes[1, 0].set_title('Returns vs Volatility', fontweight='bold')
        axes[1, 0].set_xlabel('Daily Returns (%)')
        axes[1, 0].set_ylabel('Volatility')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Volatility by year
        yearly_vol = self.df.groupby(self.df['Date'].dt.year)['Volatility'].mean()
        axes[1, 1].bar(yearly_vol.index, yearly_vol.values)
        axes[1, 1].set_title('Average Volatility by Year', fontweight='bold')
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel('Average Volatility')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Volatility plot saved to {save_path}")
        
        return fig
    
    def plot_distribution_analysis(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot distribution analysis.
        
        Parameters:
        -----------
        save_path : str, optional
            Path to save the figure
            
        Returns:
        --------
        plt.Figure
            Matplotlib figure object
        """
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Ensure returns calculated
        if 'Returns' not in self.df.columns:
            self.df['Returns'] = self.df['Price'].pct_change() * 100
        
        # 1. Price histogram
        axes[0, 0].hist(self.df['Price'].dropna(), bins=50, edgecolor='black', alpha=0.7)
        axes[0, 0].set_title('Price Distribution', fontweight='bold')
        axes[0, 0].set_xlabel('Price (USD/barrel)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Returns histogram
        axes[0, 1].hist(self.df['Returns'].dropna(), bins=100, edgecolor='black', alpha=0.7)
        axes[0, 1].set_title('Return Distribution', fontweight='bold')
        axes[0, 1].set_xlabel('Returns (%)')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. QQ plot for returns
        from scipy import stats
        stats.probplot(self.df['Returns'].dropna(), dist="norm", plot=axes[0, 2])
        axes[0, 2].set_title('QQ Plot: Returns vs Normal', fontweight='bold')
        axes[0, 2].grid(True, alpha=0.3)
        
        # 4. Box plot by year
        yearly_data = [self.df[self.df['Date'].dt.year == year]['Price'].values 
                      for year in sorted(self.df['Date'].dt.year.unique())]
        axes[1, 0].boxplot(yearly_data, labels=sorted(self.df['Date'].dt.year.unique()))
        axes[1, 0].set_title('Price Distribution by Year', fontweight='bold')
        axes[1, 0].set_xlabel('Year')
        axes[1, 0].set_ylabel('Price')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # 5. Seasonal decomposition (simplified)
        monthly_avg = self.df.groupby(self.df['Date'].dt.month)['Price'].mean()
        axes[1, 1].bar(monthly_avg.index, monthly_avg.values)
        axes[1, 1].set_title('Average Price by Month', fontweight='bold')
        axes[1, 1].set_xlabel('Month')
        axes[1, 1].set_ylabel('Average Price')
        axes[1, 1].grid(True, alpha=0.3)
        
        # 6. Cumulative returns
        if 'Returns' in self.df.columns:
            cum_returns = (1 + self.df['Returns']/100).cumprod()
            axes[1, 2].plot(self.df['Date'], cum_returns)
            axes[1, 2].set_title('Cumulative Returns', fontweight='bold')
            axes[1, 2].set_xlabel('Date')
            axes[1, 2].set_ylabel('Cumulative Return')
            axes[1, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Distribution plot saved to {save_path}")
        
        return fig
    
    def create_interactive_timeline(self, 
                                  events_df: Optional[pd.DataFrame] = None,
                                  save_path: Optional[str] = None) -> go.Figure:
        """
        Create interactive Plotly timeline.
        
        Parameters:
        -----------
        events_df : pd.DataFrame, optional
            DataFrame with event data
        save_path : str, optional
            Path to save HTML file
            
        Returns:
        --------
        go.Figure
            Plotly figure object
        """
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Brent Oil Price Timeline', 'Daily Returns'),
            vertical_spacing=0.15,
            row_heights=[0.7, 0.3]
        )
        
        # Price trace
        fig.add_trace(
            go.Scatter(
                x=self.df['Date'],
                y=self.df['Price'],
                mode='lines',
                name='Price',
                line=dict(width=1, color='blue'),
                hovertemplate='Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Add moving average
        if 'MA_30' in self.df.columns:
            fig.add_trace(
                go.Scatter(
                    x=self.df['Date'],
                    y=self.df['MA_30'],
                    mode='lines',
                    name='30-day MA',
                    line=dict(width=2, color='red'),
                    hovertemplate='Date: %{x}<br>30-day MA: $%{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # Returns trace
        if 'Returns' in self.df.columns:
            fig.add_trace(
                go.Scatter(
                    x=self.df['Date'],
                    y=self.df['Returns'],
                    mode='lines',
                    name='Returns',
                    line=dict(width=1, color='green'),
                    hovertemplate='Date: %{x}<br>Return: %{y:.2f}%<extra></extra>'
                ),
                row=2, col=1
            )
        
        # Add events if provided
        if events_df is not None and not events_df.empty:
            for _, event in events_df.iterrows():
                fig.add_vline(
                    x=event['event_date'],
                    line_dash="dash",
                    line_color="red",
                    opacity=0.5,
                    annotation_text=event['event_name'],
                    annotation_position="top right",
                    row=1, col=1
                )
        
        # Update layout
        fig.update_layout(
            title='Brent Oil Price Analysis',
            height=800,
            showlegend=True,
            hovermode='x unified'
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price (USD/barrel)", row=1, col=1)
        fig.update_yaxes(title_text="Returns (%)", row=2, col=1)
        
        if save_path:
            fig.write_html(save_path)
            logger.info(f"Interactive plot saved to {save_path}")
        
        return fig
    
    def plot_correlation_analysis(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot correlation analysis.
        
        Parameters:
        -----------
        save_path : str, optional
            Path to save the figure
            
        Returns:
        --------
        plt.Figure
            Matplotlib figure object
        """
        # Prepare features for correlation
        features_df = self.df.copy()
        
        # Ensure we have necessary features
        if 'Returns' not in features_df.columns:
            features_df['Returns'] = features_df['Price'].pct_change() * 100
        
        if 'Volatility' not in features_df.columns:
            features_df['Volatility'] = features_df['Returns'].rolling(30).std() * np.sqrt(252)
        
        # Create lagged features
        for lag in [1, 5, 10]:
            features_df[f'Returns_lag{lag}'] = features_df['Returns'].shift(lag)
            features_df[f'Price_lag{lag}'] = features_df['Price'].shift(lag)
        
        # Calculate correlation matrix
        corr_cols = ['Price', 'Returns', 'Volatility'] + \
                   [col for col in features_df.columns if 'lag' in col]
        corr_matrix = features_df[corr_cols].corr()
        
        # Plot
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Heatmap
        im = axes[0].imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        axes[0].set_title('Correlation Matrix Heatmap', fontweight='bold')
        axes[0].set_xticks(range(len(corr_cols)))
        axes[0].set_xticklabels(corr_cols, rotation=45, ha='right')
        axes[0].set_yticks(range(len(corr_cols)))
        axes[0].set_yticklabels(corr_cols)
        plt.colorbar(im, ax=axes[0])
        
        # Add correlation values
        for i in range(len(corr_cols)):
            for j in range(len(corr_cols)):
                axes[0].text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                           ha="center", va="center", color="white" if abs(corr_matrix.iloc[i, j]) > 0.5 else "black",
                           fontsize=8)
        
        # Autocorrelation plot
        from statsmodels.graphics.tsaplots import plot_acf
        if 'Returns' in features_df.columns:
            plot_acf(features_df['Returns'].dropna(), lags=50, ax=axes[1])
            axes[1].set_title('Autocorrelation Function (Returns)', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Correlation plot saved to {save_path}")
        
        return fig


# Example usage
if __name__ == "__main__":
    # Test the visualizer
    from data_loader import DataLoader
    
    # Load data
    loader = DataLoader()
    df = loader.load_data()
    
    # Create visualizations
    viz = OilPriceVisualizer(df)
    
    # Create plots
    viz.plot_price_timeline(save_path="../reports/price_timeline.png")
    viz.plot_volatility_analysis(save_path="../reports/volatility_analysis.png")
    viz.plot_distribution_analysis(save_path="../reports/distribution_analysis.png")
    viz.plot_correlation_analysis(save_path="../reports/correlation_analysis.png")
    
    # Create interactive plot
    events_df = pd.read_csv("../data/historical_events.csv")
    events_df['event_date'] = pd.to_datetime(events_df['event_date'])
    fig = viz.create_interactive_timeline(events_df, save_path="../reports/interactive_timeline.html")
    
    print("All visualizations created successfully!")