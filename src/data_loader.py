
"""
Data loading and preprocessing module for Brent oil price analysis.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading and preprocessing of Brent oil price data."""
    
    def __init__(self, data_path: str = "../data/brent_oil_prices.csv"):
        """
        Initialize DataLoader.
        
        Parameters:
        -----------
        data_path : str
            Path to Brent oil price CSV file
        """
        self.data_path = data_path
        self.df = None
        
    def load_data(self) -> pd.DataFrame:
        """
        Load and preprocess Brent oil price data.
        
        Returns:
        --------
        pd.DataFrame
            Cleaned dataframe with Date and Price columns
        """
        try:
            logger.info(f"Loading data from {self.data_path}")
            self.df = pd.read_csv(self.data_path)
            
            # Basic validation
            required_columns = ['Date', 'Price']
            if not all(col in self.df.columns for col in required_columns):
                raise ValueError(f"CSV must contain columns: {required_columns}")
            
            # Preprocess data
            self._preprocess_data()
            logger.info(f"Data loaded successfully. Shape: {self.df.shape}")
            
            return self.df
            
        except FileNotFoundError:
            logger.error(f"File not found: {self.data_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def _preprocess_data(self) -> None:
        """Clean and preprocess the data."""
        # Convert Date to datetime
        self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d-%b-%y')
        
        # Sort by date
        self.df = self.df.sort_values('Date').reset_index(drop=True)
        
        # Handle missing values
        initial_rows = len(self.df)
        self.df = self.df.dropna(subset=['Date', 'Price'])
        if len(self.df) < initial_rows:
            logger.warning(f"Removed {initial_rows - len(self.df)} rows with missing values")
        
        # Ensure Price is numeric
        self.df['Price'] = pd.to_numeric(self.df['Price'], errors='coerce')
        
        # Remove duplicates
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates(subset=['Date'])
        if len(self.df) < initial_rows:
            logger.warning(f"Removed {initial_rows - len(self.df)} duplicate rows")
        
        # Create additional features
        self._create_features()
    
    def _create_features(self) -> None:
        """Create additional features for analysis."""
        # Log price and returns
        self.df['Log_Price'] = np.log(self.df['Price'])
        self.df['Returns'] = self.df['Log_Price'].diff() * 100  # Percentage returns
        
        # Rolling statistics
        for window in [30, 90, 365]:  # 30 days, 3 months, 1 year
            self.df[f'MA_{window}'] = self.df['Price'].rolling(window=window).mean()
            self.df[f'Volatility_{window}'] = (
                self.df['Returns'].rolling(window=window).std() * np.sqrt(252)
            )
        
        # Year and month features
        self.df['Year'] = self.df['Date'].dt.year
        self.df['Month'] = self.df['Date'].dt.month
        self.df['Day_of_Week'] = self.df['Date'].dt.dayofweek
    
    def get_summary_stats(self) -> dict:
        """
        Get summary statistics of the data.
        
        Returns:
        --------
        dict
            Dictionary containing summary statistics
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        summary = {
            'start_date': self.df['Date'].min(),
            'end_date': self.df['Date'].max(),
            'total_days': len(self.df),
            'mean_price': self.df['Price'].mean(),
            'median_price': self.df['Price'].median(),
            'std_price': self.df['Price'].std(),
            'min_price': self.df['Price'].min(),
            'max_price': self.df['Price'].max(),
            'missing_values': self.df.isnull().sum().to_dict(),
            'data_types': self.df.dtypes.to_dict()
        }
        
        return summary
    
    def filter_by_date(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Filter data by date range.
        
        Parameters:
        -----------
        start_date : str
            Start date in 'YYYY-MM-DD' format
        end_date : str
            End date in 'YYYY-MM-DD' format
            
        Returns:
        --------
        pd.DataFrame
            Filtered dataframe
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        mask = (self.df['Date'] >= pd.to_datetime(start_date)) & \
               (self.df['Date'] <= pd.to_datetime(end_date))
        
        filtered_df = self.df[mask].copy()
        logger.info(f"Filtered data from {start_date} to {end_date}. Shape: {filtered_df.shape}")
        
        return filtered_df


def load_event_data(event_path: str = "../data/historical_events.csv") -> pd.DataFrame:
    """
    Load historical event data.
    
    Parameters:
    -----------
    event_path : str
        Path to event CSV file
        
    Returns:
    --------
    pd.DataFrame
        Event dataframe
    """
    try:
        events_df = pd.read_csv(event_path)
        events_df['event_date'] = pd.to_datetime(events_df['event_date'])
        logger.info(f"Loaded {len(events_df)} events from {event_path}")
        return events_df
    except FileNotFoundError:
        logger.warning(f"Event file not found: {event_path}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading event data: {str(e)}")
        raise


# Example usage
if __name__ == "__main__":
    # Test the data loader
    loader = DataLoader()
    df = loader.load_data()
    
    # Print summary
    summary = loader.get_summary_stats()
    print("\n" + "="*50)
    print("DATA SUMMARY")
    print("="*50)
    for key, value in summary.items():
        if key not in ['missing_values', 'data_types']:
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    # Load event data
    events_df = load_event_data()
    if not events_df.empty:
        print(f"\nLoaded {len(events_df)} historical events")
        print(events_df[['event_date', 'event_name']].head())