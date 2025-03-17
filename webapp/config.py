# ---- webapp/config.py ----

import os
import secrets

class Config:
    """Configuration settings for the Flask application"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    RESULTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {'txt'}
    
    # Project Gutenberg settings
    GUTENBERG_DELAY_MIN = 1
    GUTENBERG_DELAY_MAX = 3
    
    # Analysis settings
    TOP_WORDS_COUNT = 50
    MIN_WORD_LENGTH = 3
    
    # Theme analysis settings
    DEFAULT_NUM_TOPICS = 5
    DEFAULT_WORDS_PER_TOPIC = 10