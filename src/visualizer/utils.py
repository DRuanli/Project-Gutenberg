# ------ src/visualizer/utils.py ------

import os
import matplotlib.pyplot as plt
from src.scraper.utils import ensure_directory_exists

def save_figure(output_path, dpi=300, bbox_inches='tight'):
    """
    Save a matplotlib figure to file.
    
    Args:
        output_path (str): Path to save the figure
        dpi (int): Resolution in dots per inch
        bbox_inches (str): Bounding box in inches
    """
    # Ensure the directory exists
    output_dir = os.path.dirname(output_path)
    ensure_directory_exists(output_dir)
    
    # Save the figure
    plt.savefig(output_path, dpi=dpi, bbox_inches=bbox_inches)
    print(f"Figure saved to {output_path}")