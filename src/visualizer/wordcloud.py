# ------ src/visualizer/wordcloud.py ------

import matplotlib.pyplot as plt
from wordcloud import WordCloud
from src.visualizer.utils import save_figure

def generate_wordcloud(word_freq, title='Word Cloud', output_path=None, 
                       width=1000, height=600, max_words=200, background_color='white'):
    """
    Generate a word cloud from word frequencies.
    
    Args:
        word_freq (dict): Dictionary mapping words to frequencies
        title (str): Chart title
        output_path (str): Path to save the figure
        width (int): Width of word cloud
        height (int): Height of word cloud
        max_words (int): Maximum number of words to include
        background_color (str): Background color
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    # Create word cloud
    wordcloud = WordCloud(
        width=width,
        height=height,
        max_words=max_words,
        background_color=background_color,
        colormap='viridis',
        random_state=42
    ).generate_from_frequencies(word_freq)
    
    # Create figure
    plt.figure(figsize=(16, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=18)
    plt.tight_layout(pad=0)
    
    if output_path:
        save_figure(output_path)
        
    return plt.gcf()

def generate_comparative_wordcloud(word_freq1, word_freq2, labels=('Document 1', 'Document 2'), 
                                  title='Comparative Word Clouds', output_path=None):
    """
    Generate comparative word clouds for two documents.
    
    Args:
        word_freq1 (dict): Word frequencies for first document
        word_freq2 (dict): Word frequencies for second document
        labels (tuple): Labels for the two documents
        title (str): Chart title
        output_path (str): Path to save the figure
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    # Create word clouds
    wordcloud1 = WordCloud(
        width=800,
        height=500,
        max_words=150,
        background_color='white',
        colormap='Blues',
        random_state=42
    ).generate_from_frequencies(word_freq1)
    
    wordcloud2 = WordCloud(
        width=800,
        height=500,
        max_words=150,
        background_color='white',
        colormap='Reds',
        random_state=42
    ).generate_from_frequencies(word_freq2)
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))
    
    # Display word clouds
    ax1.imshow(wordcloud1, interpolation='bilinear')
    ax1.axis('off')
    ax1.set_title(labels[0], fontsize=16)
    
    ax2.imshow(wordcloud2, interpolation='bilinear')
    ax2.axis('off')
    ax2.set_title(labels[1], fontsize=16)
    
    # Add overall title
    fig.suptitle(title, fontsize=20)
    plt.tight_layout(pad=2)
    
    if output_path:
        save_figure(output_path)
        
    return fig