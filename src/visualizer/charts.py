# ------ src/visualizer/charts.py ------

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from src.visualizer.utils import save_figure

def plot_top_words(word_freq_df, title='Top Words', output_path=None):
    """
    Plot a bar chart of top words.
    
    Args:
        word_freq_df (DataFrame): DataFrame with 'Word' and 'Frequency' columns
        title (str): Chart title
        output_path (str): Path to save the figure
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Frequency', y='Word', data=word_freq_df, palette='viridis')
    plt.title(title, fontsize=16)
    plt.xlabel('Frequency', fontsize=14)
    plt.ylabel('Word', fontsize=14)
    plt.tight_layout()
    
    if output_path:
        save_figure(output_path)
        
    return plt.gcf()

def plot_word_frequency_histogram(frequencies, bins=50, title='Word Frequency Distribution', 
                                  output_path=None):
    """
    Plot a histogram of word frequencies.
    
    Args:
        frequencies (list): List of word frequencies
        bins (int): Number of bins for histogram
        title (str): Chart title
        output_path (str): Path to save the figure
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    plt.figure(figsize=(12, 8))
    sns.histplot(frequencies, bins=bins, kde=True)
    plt.title(title, fontsize=16)
    plt.xlabel('Frequency', fontsize=14)
    plt.ylabel('Count', fontsize=14)
    plt.tight_layout()
    
    if output_path:
        save_figure(output_path)
        
    return plt.gcf()

def plot_comparative_frequencies(comparison_df, title='Word Frequency Comparison', 
                                output_path=None):
    """
    Plot a comparison of word frequencies between two documents.
    
    Args:
        comparison_df (DataFrame): DataFrame with comparative frequencies
        title (str): Chart title
        output_path (str): Path to save the figure
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    # Extract columns for comparison
    doc1_col = comparison_df.columns[1]
    doc2_col = comparison_df.columns[2]
    
    # Create plot
    plt.figure(figsize=(14, 10))
    
    # Plot data
    plt.barh(comparison_df['Word'], comparison_df[doc1_col], color='skyblue', alpha=0.7, 
             label=doc1_col)
    plt.barh(comparison_df['Word'], -comparison_df[doc2_col], color='salmon', alpha=0.7, 
             label=doc2_col)
    
    # Add labels
    plt.title(title, fontsize=16)
    plt.xlabel('Frequency', fontsize=14)
    plt.legend(fontsize=12)
    
    # Add gridlines
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Adjust layout
    plt.tight_layout()
    
    if output_path:
        save_figure(output_path)
        
    return plt.gcf()

def plot_lexical_diversity(diversity_data, title='Lexical Diversity by Document', 
                          output_path=None):
    """
    Plot lexical diversity across documents.
    
    Args:
        diversity_data (dict): Dictionary mapping document names to diversity scores
        title (str): Chart title
        output_path (str): Path to save the figure
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    # Convert to DataFrame
    df = pd.DataFrame(list(diversity_data.items()), columns=['Document', 'Lexical Diversity'])
    
    # Create plot
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Lexical Diversity', y='Document', data=df, palette='viridis')
    
    # Add labels
    plt.title(title, fontsize=16)
    plt.xlabel('Lexical Diversity (Unique Words / Total Words)', fontsize=14)
    plt.ylabel('Document', fontsize=14)
    
    # Add gridlines
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Adjust layout
    plt.tight_layout()
    
    if output_path:
        save_figure(output_path)
        
    return plt.gcf()