# ------ src/scraper/utils.py ------

import os
import re

def clean_filename(filename):
    """
    Clean a string to make it suitable for use as a filename.
    
    Args:
        filename (str): The original filename
        
    Returns:
        str: A cleaned version of the filename
    """
    # Replace invalid characters with underscores
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    # Limit length
    if len(filename) > 200:
        base, ext = os.path.splitext(filename)
        filename = base[:195] + ext
    return filename

def ensure_directory_exists(directory):
    """
    Create a directory if it doesn't exist.
    
    Args:
        directory (str): Path to the directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
