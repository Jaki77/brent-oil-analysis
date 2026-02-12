"""
Utility functions for the Brent Oil Price Analysis API.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Load and preprocess data for the API."""
    
    def __init__(self, data_path: str, events_path: str, change_points_path: str):
        self.data_path = data_path
        self.events_path = events_path
        self.change_points_path = change_points_path
        self.df = None
        self.events_df = None
        self.change_points = None
        
    def load_price_data(self) -> pd.DataFrame:
        """Load Brent oil price data."""
        try:
            self.df = pd.read_csv(self.data_path)
            self.df['Date'] = pd.to_datetime(self.df['Date'])
            self.df = self.df.sort_values('Date').reset_index(drop=True)
            
            # Calculate additional metrics
            self.df['Log_Price'] = np.log(self.df['Price'])
            self.df['Returns'] = self.df['Log_Price'].diff() * 100
            self.df['Volatility_30d'] = self.df['Returns'].rolling(30).std() * np.sqrt(252)
            self.df['MA_30d'] = self.df['Price'].rolling(30).mean()
            self.df['MA_90d'] = self.df['Price'].rolling(90).mean()
            
            logger.info(f"Loaded {len(self.df)} price records")
            return self.df
        except Exception as e:
            logger.error(f"Error loading price data: {e}")
            raise
    
    def load_event_data(self) -> pd.DataFrame:
        """Load historical event data."""
        try:
            self.events_df = pd.read_csv(self.events_path)
            self.events_df['event_date'] = pd.to_datetime(self.events_df['event_date'])
            logger.info(f"Loaded {len(self.events_df)} events")
            return self.events_df
        except Exception as e:
            logger.error(f"Error loading event data: {e}")
            raise
    
    def load_change_points(self) -> Dict:
        """Load detected change points from analysis."""
        try:
            with open(self.change_points_path, 'r') as f:
                self.change_points = json.load(f)
            logger.info(f"Loaded {len(self.change_points)} change points")
            return self.change_points
        except FileNotFoundError:
            # Generate sample change points if file doesn't exist
            self.change_points = self._generate_sample_change_points()
            return self.change_points
    
    def _generate_sample_change_points(self) -> Dict:
        """Generate sample change points for testing."""
        if self.df is None:
            self.load_price_data()
            
        change_points = [
            {
                'date': '1990-08-06',
                'event': 'Iraq Invasion of Kuwait',
                'probability': 0.98,
                'mean_before': 18.5,
                'mean_after': 28.3,
                'impact_pct': 53.0
            },
            {
                'date': '2008-09-15',
                'event': 'Lehman Brothers Collapse',
                'probability': 0.99,
                'mean_before': 112.5,
                'mean_after': 68.4,
                'impact_pct': -39.2
            },
            {
                'date': '2014-11-27',
                'event': 'OPEC Maintains Production',
                'probability': 0.95,
                'mean_before': 108.2,
                'mean_after': 62.5,
                'impact_pct': -42.2
            },
            {
                'date': '2020-03-09',
                'event': 'COVID-19 Pandemic',
                'probability': 0.97,
                'mean_before': 51.2,
                'mean_after': 33.8,
                'impact_pct': -34.0
            },
            {
                'date': '2022-02-24',
                'event': 'Russia-Ukraine War',
                'probability': 0.96,
                'mean_before': 92.3,
                'mean_after': 112.7,
                'impact_pct': 22.1
            }
        ]
        return change_points


class DataProcessor:
    """Process data for API responses."""
    
    @staticmethod
    def filter_by_date_range(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """Filter dataframe by date range."""
        mask = (df['Date'] >= pd.to_datetime(start_date)) & \
               (df['Date'] <= pd.to_datetime(end_date))
        return df[mask].copy()
    
    @staticmethod
    def calculate_event_impact(df: pd.DataFrame, event_date: str, 
                              window_before: int = 30, window_after: int = 30) -> Dict:
        """Calculate price impact around an event."""
        event_date = pd.to_datetime(event_date)
        
        # Get price before event
        before_mask = (df['Date'] >= event_date - timedelta(days=window_before)) & \
                     (df['Date'] < event_date)
        before_prices = df[before_mask]['Price'].values
        
        # Get price after event
        after_mask = (df['Date'] > event_date) & \
                    (df['Date'] <= event_date + timedelta(days=window_after))
        after_prices = df[after_mask]['Price'].values
        
        if len(before_prices) == 0 or len(after_prices) == 0:
            return None
        
        impact = {
            'event_date': event_date.strftime('%Y-%m-%d'),
            'price_before': float(np.mean(before_prices)),
            'price_after': float(np.mean(after_prices)),
            'price_change': float(np.mean(after_prices) - np.mean(before_prices)),
            'percent_change': float((np.mean(after_prices) - np.mean(before_prices)) / np.mean(before_prices) * 100),
            'volatility_before': float(np.std(before_prices)),
            'volatility_after': float(np.std(after_prices)),
            'max_price': float(np.max(after_prices)),
            'min_price': float(np.min(after_prices))
        }
        
        return impact
    
    @staticmethod
    def get_summary_statistics(df: pd.DataFrame) -> Dict:
        """Generate summary statistics for the dataset."""
        stats = {
            'total_days': len(df),
            'date_range': {
                'start': df['Date'].min().strftime('%Y-%m-%d'),
                'end': df['Date'].max().strftime('%Y-%m-%d')
            },
            'price': {
                'mean': float(df['Price'].mean()),
                'median': float(df['Price'].median()),
                'std': float(df['Price'].std()),
                'min': float(df['Price'].min()),
                'max': float(df['Price'].max())
            },
            'returns': {
                'mean': float(df['Returns'].mean()),
                'std': float(df['Returns'].std()),
                'skewness': float(df['Returns'].skew()),
                'kurtosis': float(df['Returns'].kurtosis())
            },
            'volatility': {
                'mean': float(df['Volatility_30d'].mean()),
                'current': float(df['Volatility_30d'].iloc[-1])
            }
        }
        return stats