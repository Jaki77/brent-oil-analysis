import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Data paths
    DATA_PATH = os.environ.get('DATA_PATH', './data/brent_oil_prices.csv')
    EVENTS_PATH = os.environ.get('EVENTS_PATH', './data/historical_events.csv')
    CHANGE_POINTS_PATH = os.environ.get('CHANGE_POINTS_PATH', './data/change_points.json')
    MODEL_PATH = os.environ.get('MODEL_PATH', './models/change_point_model.pkl')
    
    # API settings
    API_TITLE = 'Brent Oil Price Analysis API'
    API_VERSION = '1.0.0'
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')