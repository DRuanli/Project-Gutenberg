# ------ config/config.py ------

import os

# Project directories
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
RESULTS_DIR = os.path.join(DATA_DIR, 'results')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
VISUALIZATIONS_DIR = os.path.join(OUTPUT_DIR, 'visualizations')
REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')

# Ensure directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, RESULTS_DIR, 
                 VISUALIZATIONS_DIR, REPORTS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Gutenberg scraper settings
GUTENBERG_DELAY_MIN = 1  # Minimum delay in seconds between requests
GUTENBERG_DELAY_MAX = 3  # Maximum delay in seconds between requests

# Text preprocessing settings
DEFAULT_LANGUAGE = 'english'
CUSTOM_STOPWORDS = ['said', 'would', 'could', 'one', 'may', 'also', 'even', 'many']

# Analysis settings
TOP_WORDS_COUNT = 50
MIN_WORD_LENGTH = 3

# Visualization settings
FIGURE_DPI = 300
DEFAULT_FIGSIZE = (12, 8)
WORDCLOUD_WIDTH = 1000
WORDCLOUD_HEIGHT = 600
WORDCLOUD_MAX_WORDS = 200

# Theme analysis settings
DEFAULT_NUM_TOPICS = 5
DEFAULT_WORDS_PER_TOPIC = 10