"""
Main API server for Ash-Thrash testing system

Provides REST API endpoints for testing operations, results retrieval,
and integration with external systems.
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import json
import threading
import subprocess
from datetime import datetime
import glob
import logging
from typing import Dict, Any

from .routes.health import health_bp
from .routes.testing import testing_bp
from .routes.results import results_bp


def create_app(config: Dict[str, Any] = None) -> Flask:
    """
    Create and configure Flask application
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    
    # Default configuration
    app.config.update({
        'HOST': os.environ.get('API_HOST', '0.0.0.0'),
        'PORT': int(os.environ.get('API_PORT', 8884)),
        'DEBUG': os.environ.get('API_DEBUG', 'false').lower() == 'true',
        'NLP_SERVER_URL': os.environ.get('NLP_SERVER_URL', 'http://10.20.30.253:8881'),
        'RESULTS_DIR': os.environ.get('RESULTS_DIR', 'results'),
        'MAX_WORKERS': int(os.environ.get('MAX_WORKERS', 5)),
        'TESTING_TIMEOUT': int(os.environ.get('TESTING_TIMEOUT', 300))
    })
    
    # Update with provided config
    if config:
        app.config.update(config)
    
    # Enable CORS
    CORS(app)
    
    # Setup logging
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(testing_bp, url_prefix='/api/test')
    app.register_blueprint(results_bp, url_prefix='/api/results')
    
    # Root endpoint
    @app.route('/')
    def root():
        """API root endpoint with service information"""
        return jsonify({
            'service': 'ash-thrash-api',
            'status': 'running',
            'version': '1.0.0',
            'description': 'Ash Crisis Detection Testing API',
            'repository': 'https://github.com/The-Alphabet-Cartel/ash-thrash',
            'discord': 'https://discord.gg/alphabetcartel',
            'endpoints': {
                'health': '/health',
                'testing': '/api/test/*',
                'results': '/api/results/*',
                'docs': '/api/docs'
            },
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/docs')
    def api_docs():
        """API documentation endpoint"""
        return jsonify({
            'title': 'Ash-Thrash Testing API',
            'version': '1.0.0',
            'description': 'API for testing Ash Crisis Detection System',
            'endpoints': {
                'GET /health': 'Service health check',
                'GET /health/detailed': 'Detailed health information',
                'GET /api/test/status': 'Current testing status',
                'POST /api/test/run': 'Start new test run',
                'GET /api/test/stop': 'Stop current test',
                'GET /api/results/latest': 'Latest test results',
                'GET /api/results/history': 'Historical test data',
                'GET /api/results/download/<test_id>': 'Download specific results'
            },
            'repository': 'https://github.com/The-Alphabet-Cartel/ash-thrash',
            'discord': 'https://discord.gg/alphabetcartel'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'message': 'The requested endpoint does not exist',
            'available_endpoints': [
                '/health',
                '/api/test/status',
                '/api/test/run', 
                '/api/results/latest',
                '/api/docs'
            ]
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad request',
            'message': 'Invalid request format or parameters',
            'timestamp': datetime.now().isoformat()
        }), 400
    
    return app


def run_server():
    """Run the Flask server"""
    app = create_app()
    
    host = app.config['HOST']
    port = app.config['PORT']
    debug = app.config['DEBUG']
    
    print(f"🌐 Starting Ash-Thrash API Server")
    print(f"📊 Server URL: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/api/docs")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    print(f"🧪 Testing Status: http://{host}:{port}/api/test/status")
    print("")
    
    try:
        app.run(host=host, port=port, debug=debug, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")


if __name__ == '__main__':
    run_server()


def main():
    """Main entry point for module execution"""
    run_server()


# Support for python -m execution
if __name__ == '__main__':
    main()