"""
Unit tests for Brent Oil Price Analysis API.
Tests cover all endpoints, data processing, error handling, and edge cases.
"""

import unittest
import json
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from api.utils import DataLoader, DataProcessor
from config import Config


class TestConfig(Config):
    """Test configuration with test-specific settings."""
    TESTING = True
    DEBUG = True
    DATA_PATH = './test_data/test_brent_prices.csv'
    EVENTS_PATH = './test_data/test_events.csv'
    CHANGE_POINTS_PATH = './test_data/test_change_points.json'


class BaseTestCase(unittest.TestCase):
    """Base test case with common setup and utilities."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create test data
        self._create_test_data()
    
    def tearDown(self):
        """Clean up after each test."""
        self.app_context.pop()
        self._cleanup_test_data()
    
    def _create_test_data(self):
        """Create test data files."""
        os.makedirs('./test_data', exist_ok=True)
        
        # Create test price data
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        prices = 50 + np.cumsum(np.random.randn(len(dates)) * 0.5)
        prices = np.abs(prices)  # Ensure positive
        
        test_prices = pd.DataFrame({
            'Date': dates.strftime('%Y-%m-%d'),
            'Price': prices.round(2)
        })
        test_prices.to_csv('./test_data/test_brent_prices.csv', index=False)
        
        # Create test event data
        test_events = pd.DataFrame({
            'event_date': ['2020-03-11', '2022-02-24', '2020-03-06'],
            'event_name': ['COVID-19 Pandemic', 'Russia-Ukraine War', 'OPEC+ Price War'],
            'event_type': ['Global Health Crisis', 'Geopolitical Conflict', 'Policy Decision'],
            'region_org': ['Global', 'Europe', 'OPEC/Russia'],
            'expected_impact': ['Historic price drop', 'Energy crisis spike', 'Price crash'],
            'impact_direction': ['negative', 'positive', 'negative']
        })
        test_events.to_csv('./test_data/test_events.csv', index=False)
        
        # Create test change points
        test_change_points = [
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
        with open('./test_data/test_change_points.json', 'w') as f:
            json.dump(test_change_points, f)
    
    def _cleanup_test_data(self):
        """Remove test data files."""
        import shutil
        if os.path.exists('./test_data'):
            shutil.rmtree('./test_data')
    
    def assertValidResponse(self, response):
        """Assert that response is valid JSON with 200 status."""
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json)


class TestHealthEndpoint(BaseTestCase):
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test health endpoint returns correct status."""
        response = self.client.get('/api/health')
        self.assertValidResponse(response)
        
        data = response.json
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('service', data)
        self.assertIn('version', data)
        self.assertIn('timestamp', data)
    
    def test_health_check_methods(self):
        """Test health endpoint only accepts GET."""
        response = self.client.post('/api/health')
        self.assertEqual(response.status_code, 405)
        
        response = self.client.put('/api/health')
        self.assertEqual(response.status_code, 405)
        
        response = self.client.delete('/api/health')
        self.assertEqual(response.status_code, 405)


class TestPriceAPI(BaseTestCase):
    """Test price data endpoints."""
    
    def test_get_prices_default(self):
        """Test getting prices with default parameters."""
        response = self.client.get('/api/prices')
        self.assertValidResponse(response)
        
        data = response.json
        self.assertIn('dates', data)
        self.assertIn('prices', data)
        self.assertIn('returns', data)
        self.assertIn('volatility', data)
        self.assertIn('ma_30d', data)
        self.assertIn('metadata', data)
        
        # Verify data structure
        self.assertEqual(len(data['dates']), len(data['prices']))
        self.assertEqual(len(data['dates']), len(data['returns']))
        
        # Verify metadata
        self.assertEqual(data['metadata']['frequency'], 'daily')
        self.assertGreater(data['metadata']['total_points'], 0)
    
    def test_get_prices_with_date_range(self):
        """Test price filtering by date range."""
        response = self.client.get(
            '/api/prices',
            query_string={'start': '2021-01-01', 'end': '2021-12-31'}
        )
        self.assertValidResponse(response)
        
        data = response.json
        dates = pd.to_datetime(data['dates'])
        
        self.assertTrue(all(dates >= pd.Timestamp('2021-01-01')))
        self.assertTrue(all(dates <= pd.Timestamp('2021-12-31')))
        self.assertEqual(data['metadata']['date_range']['start'], '2021-01-01')
        self.assertEqual(data['metadata']['date_range']['end'], '2021-12-31')
    
    def test_get_prices_with_frequency(self):
        """Test price data resampling."""
        # Test weekly aggregation
        response = self.client.get(
            '/api/prices',
            query_string={'frequency': 'weekly'}
        )
        self.assertValidResponse(response)
        self.assertEqual(response.json['metadata']['frequency'], 'weekly')
        
        # Test monthly aggregation
        response = self.client.get(
            '/api/prices',
            query_string={'frequency': 'monthly'}
        )
        self.assertValidResponse(response)
        self.assertEqual(response.json['metadata']['frequency'], 'monthly')
    
    def test_get_prices_invalid_date(self):
        """Test handling of invalid dates."""
        response = self.client.get(
            '/api/prices',
            query_string={'start': 'invalid-date'}
        )
        self.assertEqual(response.status_code, 500)
    
    def test_get_prices_future_date(self):
        """Test requesting future dates (should return empty)."""
        response = self.client.get(
            '/api/prices',
            query_string={'start': '2025-01-01', 'end': '2025-12-31'}
        )
        self.assertValidResponse(response)
        self.assertEqual(len(response.json['dates']), 0)


class TestEventAPI(BaseTestCase):
    """Test event data endpoints."""
    
    def test_get_events_default(self):
        """Test getting all events."""
        response = self.client.get('/api/events')
        self.assertValidResponse(response)
        
        data = response.json
        self.assertIn('events', data)
        self.assertIn('total', data)
        self.assertIn('event_types', data)
        
        self.assertGreater(data['total'], 0)
        self.assertIsInstance(data['events'], list)
    
    def test_get_events_by_type(self):
        """Test filtering events by type."""
        response = self.client.get(
            '/api/events',
            query_string={'type': 'Geopolitical Conflict'}
        )
        self.assertValidResponse(response)
        
        data = response.json
        for event in data['events']:
            self.assertEqual(event['type'], 'Geopolitical Conflict')
    
    def test_get_events_by_date_range(self):
        """Test filtering events by date range."""
        response = self.client.get(
            '/api/events',
            query_string={'start': '2022-01-01', 'end': '2022-12-31'}
        )
        self.assertValidResponse(response)
        
        data = response.json
        for event in data['events']:
            event_date = pd.to_datetime(event['date'])
            self.assertGreaterEqual(event_date, pd.Timestamp('2022-01-01'))
            self.assertLessEqual(event_date, pd.Timestamp('2022-12-31'))
    
    def test_get_events_with_impact_calculation(self):
        """Test that event impacts are calculated correctly."""
        response = self.client.get('/api/events')
        self.assertValidResponse(response)
        
        for event in response.json['events']:
            if event.get('impact'):
                impact = event['impact']
                self.assertIn('price_before', impact)
                self.assertIn('price_after', impact)
                self.assertIn('percent_change', impact)
                self.assertIn('volatility_before', impact)
                self.assertIn('volatility_after', impact)
    
    def test_get_event_types(self):
        """Test event type distribution endpoint."""
        response = self.client.get('/api/event-types')
        self.assertValidResponse(response)
        
        data = response.json
        self.assertIn('types', data)
        self.assertIn('total', data)
        
        total_events = sum(t['count'] for t in data['types'])
        self.assertEqual(total_events, data['total'])
    
    def test_get_events_nonexistent_type(self):
        """Test filtering by nonexistent event type."""
        response = self.client.get(
            '/api/events',
            query_string={'type': 'Nonexistent Type'}
        )
        self.assertValidResponse(response)
        self.assertEqual(len(response.json['events']), 0)


class TestChangePointAPI(BaseTestCase):
    """Test change point endpoints."""
    
    def test_get_change_points_default(self):
        """Test getting change points with default threshold."""
        response = self.client.get('/api/change-points')
        self.assertValidResponse(response)
        
        data = response.json
        self.assertIn('change_points', data)
        self.assertIn('total', data)
        self.assertIn('probability_threshold', data)
        
        # Default threshold should be 0.8
        self.assertEqual(data['probability_threshold'], 0.8)
    
    def test_get_change_points_with_threshold(self):
        """Test filtering change points by probability threshold."""
        response = self.client.get(
            '/api/change-points',
            query_string={'min_probability': 0.9}
        )
        self.assertValidResponse(response)
        
        for cp in response.json['change_points']:
            self.assertGreaterEqual(cp['probability'], 0.9)
    
    def test_change_point_event_correlation(self):
        """Test that change points are correlated with events."""
        response = self.client.get('/api/change-points')
        self.assertValidResponse(response)
        
        for cp in response.json['change_points']:
            if cp.get('correlated_event'):
                self.assertIsNotNone(cp['correlation_days'])
                self.assertLessEqual(abs(cp['correlation_days']), 30)
    
    def test_change_point_impact_metrics(self):
        """Test that change points include impact metrics."""
        response = self.client.get('/api/change-points')
        self.assertValidResponse(response)
        
        for cp in response.json['change_points']:
            self.assertIn('mean_before', cp)
            self.assertIn('mean_after', cp)
            self.assertIn('impact_pct', cp)


class TestSummaryAPI(BaseTestCase):
    """Test summary statistics endpoints."""
    
    def test_get_summary(self):
        """Test getting summary statistics."""
        response = self.client.get('/api/summary')
        self.assertValidResponse(response)
        
        data = response.json
        self.assertIn('total_days', data)
        self.assertIn('date_range', data)
        self.assertIn('price', data)
        self.assertIn('returns', data)
        self.assertIn('volatility', data)
        self.assertIn('total_events', data)
        self.assertIn('detected_change_points', data)
        self.assertIn('volatility_regime', data)
        self.assertIn('latest', data)
        
        # Verify price statistics
        self.assertGreater(data['price']['mean'], 0)
        self.assertGreater(data['price']['max'], data['price']['min'])
        
        # Verify latest price
        self.assertIsNotNone(data['latest']['price'])
        self.assertIsNotNone(data['latest']['date'])
    
    def test_volatility_regime_detection(self):
        """Test volatility regime classification."""
        response = self.client.get('/api/summary')
        data = response.json
        
        regime = data['volatility_regime']
        self.assertIn('regime', regime)
        self.assertIn(regime['regime'], ['High', 'Normal', 'Low'])
        self.assertGreater(regime['current'], 0)
        self.assertGreater(regime['historical_avg'], 0)
    
    def test_summary_consistency(self):
        """Test that summary statistics are consistent with data."""
        response = self.client.get('/api/summary')
        summary = response.json
        
        # Get price data separately
        prices_response = self.client.get('/api/prices')
        prices_data = prices_response.json
        
        # Verify consistency
        self.assertEqual(
            summary['date_range']['start'],
            prices_data['metadata']['date_range']['start']
        )
        self.assertEqual(
            summary['total_days'],
            prices_data['metadata']['total_points']
        )


class TestVolatilityAPI(BaseTestCase):
    """Test volatility analysis endpoints."""
    
    def test_get_volatility(self):
        """Test getting volatility analysis data."""
        response = self.client.get('/api/volatility')
        self.assertValidResponse(response)
        
        data = response.json
        self.assertIn('yearly_volatility', data)
        self.assertIn('event_volatility', data)
        self.assertIn('current_volatility', data)
        self.assertIn('historical_avg_volatility', data)
        
        # Verify yearly volatility structure
        self.assertIn('years', data['yearly_volatility'])
        self.assertIn('values', data['yearly_volatility'])
        self.assertEqual(
            len(data['yearly_volatility']['years']),
            len(data['yearly_volatility']['values'])
        )
    
    def test_event_volatility_impact(self):
        """Test volatility impact by event type."""
        response = self.client.get('/api/volatility')
        data = response.json
        
        for event_vol in data['event_volatility']:
            self.assertIn('event_type', event_vol)
            self.assertIn('volatility_before', event_vol)
            self.assertIn('volatility_after', event_vol)
            self.assertIn('change', event_vol)
            self.assertIn('percent_change', event_vol)
    
    def test_volatility_values_range(self):
        """Test that volatility values are within reasonable range."""
        response = self.client.get('/api/volatility')
        data = response.json
        
        # Volatility should be between 0 and 1 (0% to 100%)
        self.assertGreaterEqual(data['current_volatility'], 0)
        self.assertLessEqual(data['current_volatility'], 1)
        
        for vol in data['yearly_volatility']['values']:
            self.assertGreaterEqual(vol, 0)
            self.assertLessEqual(vol, 1)


class TestDataProcessor(BaseTestCase):
    """Test DataProcessor utility functions."""
    
    def setUp(self):
        """Set up DataProcessor tests."""
        super().setUp()
        self.processor = DataProcessor()
        self.loader = DataLoader(
            TestConfig.DATA_PATH,
            TestConfig.EVENTS_PATH,
            TestConfig.CHANGE_POINTS_PATH
        )
        self.df = self.loader.load_price_data()
    
    def test_filter_by_date_range(self):
        """Test date range filtering."""
        filtered = self.processor.filter_by_date_range(
            self.df, '2021-01-01', '2021-12-31'
        )
        
        self.assertTrue(all(filtered['Date'] >= pd.Timestamp('2021-01-01')))
        self.assertTrue(all(filtered['Date'] <= pd.Timestamp('2021-12-31')))
    
    def test_calculate_event_impact(self):
        """Test event impact calculation."""
        impact = self.processor.calculate_event_impact(
            self.df, '2020-03-11', window_before=30, window_after=30
        )
        
        self.assertIsNotNone(impact)
        self.assertIn('event_date', impact)
        self.assertIn('price_before', impact)
        self.assertIn('price_after', impact)
        self.assertIn('percent_change', impact)
        self.assertIn('volatility_before', impact)
        self.assertIn('volatility_after', impact)
        
        # Verify calculations
        self.assertGreater(impact['price_before'], 0)
        self.assertGreater(impact['price_after'], 0)
        self.assertIsNotNone(impact['percent_change'])
    
    def test_calculate_event_impact_invalid_date(self):
        """Test event impact with invalid date."""
        impact = self.processor.calculate_event_impact(
            self.df, '1900-01-01'
        )
        self.assertIsNone(impact)
    
    def test_get_summary_statistics(self):
        """Test summary statistics calculation."""
        stats = self.processor.get_summary_statistics(self.df)
        
        self.assertIn('total_days', stats)
        self.assertIn('price', stats)
        self.assertIn('returns', stats)
        self.assertIn('volatility', stats)
        
        # Verify calculations
        self.assertEqual(stats['total_days'], len(self.df))
        self.assertGreater(stats['price']['mean'], 0)
        self.assertGreater(stats['price']['max'], stats['price']['min'])


class TestErrorHandling(BaseTestCase):
    """Test API error handling."""
    
    def test_404_handling(self):
        """Test handling of non-existent endpoints."""
        response = self.client.get('/api/nonexistent')
        self.assertEqual(response.status_code, 404)
    
    def test_method_not_allowed(self):
        """Test handling of invalid HTTP methods."""
        response = self.client.put('/api/prices')
        self.assertEqual(response.status_code, 405)
    
    def test_malformed_json(self):
        """Test handling of malformed JSON in requests."""
        # This test assumes an endpoint that accepts POST with JSON
        # Modify based on actual POST endpoints in your API
        pass
    
    @patch('api.routes.df', None)
    def test_data_not_loaded(self):
        """Test handling when data is not loaded."""
        response = self.client.get('/api/prices')
        self.assertEqual(response.status_code, 500)


class TestAPIDocumentation(BaseTestCase):
    """Test API documentation endpoint."""
    
    def test_api_docs(self):
        """Test API documentation endpoint."""
        response = self.client.get('/api/docs')
        self.assertValidResponse(response)
        
        data = response.json
        self.assertIn('service', data)
        self.assertIn('version', data)
        self.assertIn('endpoints', data)
        
        # Verify endpoint documentation
        endpoints = {e['path'] for e in data['endpoints']}
        expected_endpoints = {
            '/api/health', '/api/prices', '/api/events',
            '/api/change-points', '/api/summary', 
            '/api/event-types', '/api/volatility'
        }
        self.assertTrue(expected_endpoints.issubset(endpoints))


class TestPerformance(BaseTestCase):
    """Test API performance."""
    
    def test_response_time(self):
        """Test that API responses are timely."""
        import time
        
        start = time.time()
        response = self.client.get('/api/summary')
        end = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end - start, 0.5)  # Should respond within 500ms
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        from concurrent.futures import ThreadPoolExecutor
        
        def make_request():
            return self.client.get('/api/prices')
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [f.result() for f in futures]
        
        for response in responses:
            self.assertEqual(response.status_code, 200)


class TestDataIntegrity(BaseTestCase):
    """Test data integrity and validation."""
    
    def test_price_data_integrity(self):
        """Test that price data maintains integrity."""
        response = self.client.get('/api/prices')
        data = response.json
        
        # Check for negative prices (should not exist)
        self.assertTrue(all(p >= 0 for p in data['prices']))
        
        # Check for missing values
        self.assertEqual(len([p for p in data['prices'] if p is None]), 0)
    
    def test_date_ordering(self):
        """Test that dates are in chronological order."""
        response = self.client.get('/api/prices')
        dates = pd.to_datetime(response.json['dates'])
        
        self.assertTrue(all(dates[i] <= dates[i+1] for i in range(len(dates)-1)))
    
    def test_event_date_validation(self):
        """Test that event dates are valid."""
        response = self.client.get('/api/events')
        
        for event in response.json['events']:
            try:
                pd.to_datetime(event['date'])
            except Exception:
                self.fail(f"Invalid date format: {event['date']}")


class TestCORS(BaseTestCase):
    """Test CORS headers."""
    
    def test_cors_headers(self):
        """Test that CORS headers are set correctly."""
        response = self.client.get('/api/health', headers={
            'Origin': 'http://localhost:3000'
        })
        
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertEqual(
            response.headers['Access-Control-Allow-Origin'],
            'http://localhost:3000'
        )
    
    def test_cors_preflight(self):
        """Test CORS preflight request."""
        response = self.client.options('/api/health', headers={
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Access-Control-Allow-Methods', response.headers)


class TestEdgeCases(BaseTestCase):
    """Test edge cases and boundary conditions."""
    
    def test_empty_date_range(self):
        """Test requesting data with no matching records."""
        response = self.client.get(
            '/api/prices',
            query_string={'start': '2030-01-01', 'end': '2030-12-31'}
        )
        self.assertValidResponse(response)
        self.assertEqual(len(response.json['dates']), 0)
    
    def test_single_day_range(self):
        """Test requesting a single day of data."""
        response = self.client.get(
            '/api/prices',
            query_string={'start': '2022-01-01', 'end': '2022-01-01'}
        )
        self.assertValidResponse(response)
        self.assertEqual(len(response.json['dates']), 1)
    
    def test_inverse_date_range(self):
        """Test requesting with start > end (should handle gracefully)."""
        response = self.client.get(
            '/api/prices',
            query_string={'start': '2022-12-31', 'end': '2022-01-01'}
        )
        # API should either return 500 or handle gracefully
        self.assertIn(response.status_code, [200, 500])
    
    def test_extreme_probability_threshold(self):
        """Test change points with extreme probability thresholds."""
        # Test with threshold > 1.0
        response = self.client.get(
            '/api/change-points',
            query_string={'min_probability': 1.5}
        )
        # Should handle gracefully (either ignore or return empty)
        self.assertIn(response.status_code, [200, 400, 500])
        
        # Test with threshold < 0
        response = self.client.get(
            '/api/change-points',
            query_string={'min_probability': -0.5}
        )
        self.assertIn(response.status_code, [200, 400, 500])


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTest(unittest.makeSuite(TestHealthEndpoint))
    suite.addTest(unittest.makeSuite(TestPriceAPI))
    suite.addTest(unittest.makeSuite(TestEventAPI))
    suite.addTest(unittest.makeSuite(TestChangePointAPI))
    suite.addTest(unittest.makeSuite(TestSummaryAPI))
    suite.addTest(unittest.makeSuite(TestVolatilityAPI))
    suite.addTest(unittest.makeSuite(TestDataProcessor))
    suite.addTest(unittest.makeSuite(TestErrorHandling))
    suite.addTest(unittest.makeSuite(TestAPIDocumentation))
    suite.addTest(unittest.makeSuite(TestPerformance))
    suite.addTest(unittest.makeSuite(TestDataIntegrity))
    suite.addTest(unittest.makeSuite(TestCORS))
    suite.addTest(unittest.makeSuite(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())