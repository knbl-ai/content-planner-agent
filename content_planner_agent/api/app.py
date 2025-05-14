"""
Flask application for the Content Planner Agent API.
"""
from flask import Flask
from flask_cors import CORS
from content_planner_agent.api.routes import api_bp

def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        The configured Flask application
    """
    app = Flask(__name__)
    
    # Enable CORS with more permissive settings
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    
    # Register the API blueprint
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 