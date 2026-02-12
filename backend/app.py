"""
Flask application for Brent Oil Price Analysis Dashboard.
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_restful import Api
from config import Config
from api.routes import api_bp
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """Application factory pattern."""
    
    app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    api = Api(app)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Serve React app
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/api/docs')
    def api_docs():
        """API documentation endpoint."""
        return {
            'service': app.config['API_TITLE'],
            'version': app.config['API_VERSION'],
            'endpoints': [
                {
                    'path': '/api/health',
                    'method': 'GET',
                    'description': 'Health check'
                },
                {
                    'path': '/api/prices',
                    'method': 'GET',
                    'description': 'Get historical price data',
                    'parameters': ['start', 'end', 'frequency']
                },
                {
                    'path': '/api/events',
                    'method': 'GET',
                    'description': 'Get historical events',
                    'parameters': ['type', 'start', 'end']
                },
                {
                    'path': '/api/change-points',
                    'method': 'GET',
                    'description': 'Get detected change points',
                    'parameters': ['min_probability']
                },
                {
                    'path': '/api/summary',
                    'method': 'GET',
                    'description': 'Get summary statistics'
                },
                {
                    'path': '/api/event-types',
                    'method': 'GET',
                    'description': 'Get event type distribution'
                },
                {
                    'path': '/api/volatility',
                    'method': 'GET',
                    'description': 'Get volatility analysis'
                }
            ]
        }
    
    logger.info(f"Application created with config: {app.config['ENV']}")
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])