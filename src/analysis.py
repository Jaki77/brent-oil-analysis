"""
Statistical analysis module for Brent oil prices.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Optional
import logging
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TimeSeriesAnalyzer:
    """Performs time series analysis on Brent oil prices."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize analyzer with data.
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with Date and Price columns
        """
        self.df = df.copy()
        self.results = {}
        
    def test_stationarity(self, series: pd.Series, series_name: str = "Series") -> Dict:
        """
        Perform stationarity tests on a time series.
        
        Parameters:
        -----------
        series : pd.Series
            Time series to test
        series_name : str
            Name of the series for reporting
            
        Returns:
        --------
        dict
            Dictionary with test results
        """
        logger.info(f"Testing stationarity for {series_name}")
        
        results = {'series_name': series_name}
        
        # Remove NaN values
        clean_series = series.dropna()
        
        # ADF Test
        try:
            adf_result = adfuller(clean_series)
            results['adf'] = {
                'test_statistic': adf_result[0],
                'p_value': adf_result[1],
                'critical_values': adf_result[4],
                'is_stationary': adf_result[1] <= 0.05
            }
        except Exception as e:
            logger.error(f"ADF test failed: {e}")
            results['adf'] = None
        
        # KPSS Test
        try:
            kpss_result = kpss(clean_series, regression='c', nlags='auto')
            results['kpss'] = {
                'test_statistic': kpss_result[0],
                'p_value': kpss_result[1],
                'critical_values': kpss_result[3],
                'is_stationary': kpss_result[1] >= 0.05
            }
        except Exception as e:
            logger.error(f"KPSS test failed: {e}")
            results['kpss'] = None
        
        # Save to instance results
        self.results[f'stationarity_{series_name}'] = results
        
        return results
    
    def analyze_trends(self) -> Dict:
        """
        Analyze trends in the price data.
        
        Returns:
        --------
        dict
            Trend analysis results
        """
        logger.info("Analyzing price trends")
        
        results = {}
        
        # Linear trend
        x = np.arange(len(self.df))
        y = self.df['Price'].values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        results['linear_trend'] = {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value**2,
            'p_value': p_value,
            'std_error': std_err
        }
        
        # Decompose by year
        yearly_stats = self.df.groupby(self.df['Date'].dt.year)['Price'].agg([
            'mean', 'median', 'std', 'min', 'max'
        ]).round(2)
        
        results['yearly_stats'] = yearly_stats
        
        # Rolling statistics
        for window in [30, 90, 365]:
            col_name = f'MA_{window}'
            if col_name in self.df.columns:
                results[f'rolling_{window}_stats'] = {
                    'mean': self.df[col_name].mean(),
                    'std': self.df[col_name].std(),
                    'min': self.df[col_name].min(),
                    'max': self.df[col_name].max()
                }
        
        self.results['trend_analysis'] = results
        return results
    
    def analyze_volatility(self, window: int = 30) -> Dict:
        """
        Analyze volatility patterns.
        
        Parameters:
        -----------
        window : int
            Rolling window size for volatility calculation
            
        Returns:
        --------
        dict
            Volatility analysis results
        """
        logger.info(f"Analyzing volatility with {window}-day window")
        
        if 'Returns' not in self.df.columns:
            self.df['Returns'] = self.df['Price'].pct_change() * 100
        
        # Calculate rolling volatility
        self.df['Volatility'] = self.df['Returns'].rolling(window=window).std() * np.sqrt(252)
        
        results = {
            'mean_volatility': self.df['Volatility'].mean(),
            'median_volatility': self.df['Volatility'].median(),
            'max_volatility': self.df['Volatility'].max(),
            'min_volatility': self.df['Volatility'].min(),
            'volatility_std': self.df['Volatility'].std()
        }
        
        # Volatility clustering test (Ljung-Box on squared returns)
        from statsmodels.stats.diagnostic import acorr_ljungbox
        squared_returns = self.df['Returns'].dropna() ** 2
        
        try:
            lb_test = acorr_ljungbox(squared_returns, lags=[10], return_df=True)
            results['volatility_clustering'] = {
                'ljung_box_stat': lb_test['lb_stat'].iloc[0],
                'ljung_box_pvalue': lb_test['lb_pvalue'].iloc[0],
                'has_clustering': lb_test['lb_pvalue'].iloc[0] < 0.05
            }
        except Exception as e:
            logger.error(f"Ljung-Box test failed: {e}")
            results['volatility_clustering'] = None
        
        # Volatility by year
        yearly_vol = self.df.groupby(self.df['Date'].dt.year)['Volatility'].mean()
        results['yearly_volatility'] = yearly_vol.to_dict()
        
        self.results['volatility_analysis'] = results
        return results
    
    def analyze_distribution(self) -> Dict:
        """
        Analyze distribution of prices and returns.
        
        Returns:
        --------
        dict
            Distribution analysis results
        """
        logger.info("Analyzing price and return distributions")
        
        results = {}
        
        for col in ['Price', 'Returns']:
            if col in self.df.columns:
                data = self.df[col].dropna()
                
                # Basic statistics
                stats_dict = {
                    'mean': data.mean(),
                    'median': data.median(),
                    'std': data.std(),
                    'skewness': data.skew(),
                    'kurtosis': data.kurtosis(),
                    'jarque_bera': stats.jarque_bera(data)[1],  # p-value
                    'is_normal': stats.jarque_bera(data)[1] > 0.05
                }
                
                # Percentiles
                percentiles = np.percentile(data, [1, 5, 25, 50, 75, 95, 99])
                stats_dict['percentiles'] = {
                    'p1': percentiles[0],
                    'p5': percentiles[1],
                    'p25': percentiles[2],
                    'p50': percentiles[3],
                    'p75': percentiles[4],
                    'p95': percentiles[5],
                    'p99': percentiles[6]
                }
                
                results[col.lower()] = stats_dict
        
        self.results['distribution_analysis'] = results
        return results
    
    def create_summary_report(self) -> str:
        """
        Create a summary report of all analyses.
        
        Returns:
        --------
        str
            Formatted summary report
        """
        report_lines = []
        
        report_lines.append("="*60)
        report_lines.append("BRENT OIL PRICE ANALYSIS SUMMARY")
        report_lines.append("="*60)
        report_lines.append(f"\nData Period: {self.df['Date'].min().date()} to {self.df['Date'].max().date()}")
        report_lines.append(f"Total Observations: {len(self.df):,}")
        
        # Stationarity summary
        if 'stationarity_Price' in self.results:
            stat = self.results['stationarity_Price']
            report_lines.append("\n" + "-"*40)
            report_lines.append("STATIONARITY ANALYSIS")
            report_lines.append("-"*40)
            report_lines.append(f"Price Levels: {'STATIONARY' if stat['adf']['is_stationary'] else 'NON-STATIONARY'}")
            report_lines.append(f"ADF p-value: {stat['adf']['p_value']:.6f}")
        
        # Trend summary
        if 'trend_analysis' in self.results:
            trend = self.results['trend_analysis']
            report_lines.append("\n" + "-"*40)
            report_lines.append("TREND ANALYSIS")
            report_lines.append("-"*40)
            report_lines.append(f"Linear Trend Slope: {trend['linear_trend']['slope']:.6f} (per day)")
            report_lines.append(f"R-squared: {trend['linear_trend']['r_squared']:.4f}")
        
        # Volatility summary
        if 'volatility_analysis' in self.results:
            vol = self.results['volatility_analysis']
            report_lines.append("\n" + "-"*40)
            report_lines.append("VOLATILITY ANALYSIS")
            report_lines.append("-"*40)
            report_lines.append(f"Mean Annualized Volatility: {vol['mean_volatility']:.2%}")
            report_lines.append(f"Max Annualized Volatility: {vol['max_volatility']:.2%}")
            if vol['volatility_clustering']:
                has_clust = vol['volatility_clustering']['has_clustering']
                report_lines.append(f"Volatility Clustering: {'PRESENT' if has_clust else 'ABSENT'}")
        
        # Distribution summary
        if 'distribution_analysis' in self.results:
            dist = self.results['distribution_analysis']
            report_lines.append("\n" + "-"*40)
            report_lines.append("DISTRIBUTION ANALYSIS")
            report_lines.append("-"*40)
            if 'price' in dist:
                report_lines.append(f"Price Skewness: {dist['price']['skewness']:.4f}")
                report_lines.append(f"Price Kurtosis: {dist['price']['kurtosis']:.4f}")
                report_lines.append(f"Normality (J-B p-value): {dist['price']['jarque_bera']:.6f}")
                report_lines.append(f"Normal Distribution: {'YES' if dist['price']['is_normal'] else 'NO'}")
        
        report_lines.append("\n" + "="*60)
        
        return "\n".join(report_lines)


def plot_time_series_analysis(df: pd.DataFrame, save_path: Optional[str] = None) -> None:
    """
    Create comprehensive time series analysis plots.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with Date, Price, and Returns columns
    save_path : str, optional
        Path to save the figure
    """
    fig = plt.figure(figsize=(16, 12))
    
    # Price trend
    ax1 = plt.subplot(3, 3, 1)
    ax1.plot(df['Date'], df['Price'], linewidth=0.5, alpha=0.7)
    ax1.set_title('Brent Oil Price Trend', fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price (USD/barrel)')
    ax1.grid(True, alpha=0.3)
    
    # Returns
    ax2 = plt.subplot(3, 3, 2)
    ax2.plot(df['Date'], df['Returns'], linewidth=0.3, alpha=0.7)
    ax2.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    ax2.set_title('Daily Returns', fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Returns (%)')
    ax2.grid(True, alpha=0.3)
    
    # Histogram of returns
    ax3 = plt.subplot(3, 3, 3)
    ax3.hist(df['Returns'].dropna(), bins=100, edgecolor='black', alpha=0.7)
    ax3.set_title('Return Distribution', fontweight='bold')
    ax3.set_xlabel('Returns (%)')
    ax3.set_ylabel('Frequency')
    ax3.grid(True, alpha=0.3)
    
    # ACF of prices
    ax4 = plt.subplot(3, 3, 4)
    plot_acf(df['Price'].dropna(), lags=50, ax=ax4)
    ax4.set_title('ACF: Price Levels', fontweight='bold')
    
    # ACF of returns
    ax5 = plt.subplot(3, 3, 5)
    plot_acf(df['Returns'].dropna(), lags=50, ax=ax5)
    ax5.set_title('ACF: Returns', fontweight='bold')
    
    # PACF of returns
    ax6 = plt.subplot(3, 3, 6)
    plot_pacf(df['Returns'].dropna(), lags=50, ax=ax6)
    ax6.set_title('PACF: Returns', fontweight='bold')
    
    # QQ plot
    ax7 = plt.subplot(3, 3, 7)
    stats.probplot(df['Returns'].dropna(), dist="norm", plot=ax7)
    ax7.set_title('QQ Plot vs Normal', fontweight='bold')
    ax7.grid(True, alpha=0.3)
    
    # Rolling volatility
    ax8 = plt.subplot(3, 3, 8)
    if 'Volatility' in df.columns:
        ax8.plot(df['Date'], df['Volatility'], linewidth=0.5)
        ax8.set_title('Rolling Volatility (30-day)', fontweight='bold')
        ax8.set_xlabel('Date')
        ax8.set_ylabel('Annualized Volatility')
        ax8.grid(True, alpha=0.3)
    
    # Price by year
    ax9 = plt.subplot(3, 3, 9)
    yearly_mean = df.groupby(df['Date'].dt.year)['Price'].mean()
    ax9.bar(yearly_mean.index, yearly_mean.values)
    ax9.set_title('Average Price by Year', fontweight='bold')
    ax9.set_xlabel('Year')
    ax9.set_ylabel('Average Price')
    ax9.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Plot saved to {save_path}")
    
    plt.show()


# Example usage
if __name__ == "__main__":
    # Test the analyzer
    from data_loader import DataLoader
    
    # Load data
    loader = DataLoader()
    df = loader.load_data()
    
    # Analyze
    analyzer = TimeSeriesAnalyzer(df)
    
    # Run analyses
    stationarity = analyzer.test_stationarity(df['Price'], "Price")
    trends = analyzer.analyze_trends()
    volatility = analyzer.analyze_volatility()
    distribution = analyzer.analyze_distribution()
    
    # Print summary
    print(analyzer.create_summary_report())
    
    # Create plots
    plot_time_series_analysis(df)