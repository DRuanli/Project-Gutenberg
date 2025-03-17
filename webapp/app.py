from flask import Flask
import os
from datetime import datetime
from webapp.routes import main
from webapp.config import Config

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure necessary directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    
    # Add context processor for current datetime
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    # Register blueprints
    app.register_blueprint(main)
    
    return app