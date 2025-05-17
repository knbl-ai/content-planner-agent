"""
Flask application for the Content Planner Agent API.
"""
import logging
from flask import Flask
from flask_cors import CORS
from content_planner_agent.api.routes import api_bp

# Set up logger
logger = logging.getLogger(__name__)

def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        A configured Flask application
    """
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Register the API blueprint
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Add a health check route
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}
    
    logger.info("Flask application created and configured")
    
    return app

# Create the app instance for direct imports
app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 