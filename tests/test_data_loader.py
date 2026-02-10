"""
Tests for data_loader module.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_loader import DataLoader, load_event_data


class TestDataLoader(unittest.TestCase):
    """Test cases for DataLoader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = DataLoader('data/brent_oil_prices.csv')
    
    def test_load_data(self):
        """Test data loading functionality."""
        df = self.loader.load_data()
        
        # Check DataFrame is not empty
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        
        # Check required columns exist
        required_columns = ['Date', 'Price']
        for col in required_columns:
            self.assertIn(col, df.columns)
        
        # Check Date is datetime
        self.assertEqual(df['Date'].dtype, 'datetime64[ns]')
        
        # Check Price is numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(df['Price']))
    
    def test_get_summary_stats(self):
        """Test summary statistics generation."""
        df = self.loader.load_data()
        stats = self.loader.get_summary_stats()
        
        # Check stats dictionary has required keys
        required_keys = ['start_date', 'end_date', 'total_days', 'mean_price']
        for key in required_keys:
            self.assertIn(key, stats)
        
        # Check data types in stats
        self.assertIsInstance(stats['total_days'], int)
        self.assertIsInstance(stats['mean_price'], float)
    
    def test_filter_by_date(self):
        """Test date filtering functionality."""
        df = self.loader.load_data()
        
        # Test filtering
        filtered = self.loader.filter_by_date('2000-01-01', '2000-12-31')
        
        # Check filtered DataFrame
        self.assertIsNotNone(filtered)
        self.assertGreater(len(filtered), 0)
        
        # Check date range
        self.assertTrue(all(filtered['Date'] >= pd.Timestamp('2000-01-01')))
        self.assertTrue(all(filtered['Date'] <= pd.Timestamp('2000-12-31')))
    
    def test_event_data_loading(self):
        """Test event data loading."""
        events_df = load_event_data('data/historical_events.csv')
        
        # Check events DataFrame
        self.assertIsNotNone(events_df)
        self.assertGreater(len(events_df), 0)
        
        # Check required columns
        required_columns = ['event_date', 'event_name', 'event_type']
        for col in required_columns:
            self.assertIn(col, events_df.columns)


class TestDataQuality(unittest.TestCase):
    """Test data quality checks."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = DataLoader('data/brent_oil_prices.csv')
        self.df = self.loader.load_data()
    
    def test_no_duplicate_dates(self):
        """Test that there are no duplicate dates."""
        duplicates = self.df['Date'].duplicated().sum()
        self.assertEqual(duplicates, 0, f"Found {duplicates} duplicate dates")
    
    def test_no_missing_prices(self):
        """Test that there are no missing prices."""
        missing_prices = self.df['Price'].isnull().sum()
        self.assertEqual(missing_prices, 0, f"Found {missing_prices} missing prices")
    
    def test_price_positive(self):
        """Test that all prices are positive."""
        negative_prices = (self.df['Price'] <= 0).sum()
        self.assertEqual(negative_prices, 0, f"Found {negative_prices} non-positive prices")
    
    def test_chronological_order(self):
        """Test that dates are in chronological order."""
        is_sorted = self.df['Date'].is_monotonic_increasing
        self.assertTrue(is_sorted, "Dates are not in chronological order")


if __name__ == '__main__':
    unittest.main()