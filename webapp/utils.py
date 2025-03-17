# ---- webapp/utils.py ----

import os
import sys
import json
import shutil
from flask import current_app
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Add the parent directory to the Python path to import from the existing project
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from src.scraper.gutenberg import GutenbergScraper
from src.preprocessor.cleaner import clean_text, remove_punctuation, normalize_whitespace
from src.preprocessor.tokenizer import preprocess_text
from src.analyzer.frequency import FrequencyAnalyzer
from src.visualizer.charts import plot_top_words, plot_word_frequency_histogram, plot_comparative_frequencies
from src.visualizer.wordcloud import generate_wordcloud, generate_comparative_wordcloud
from src.insights.themes import ThemeAnalyzer
from src.insights.comparisons import ComparativeAnalyzer

def download_gutenberg_books(book_ids, session_id):
    """
    Download books from Project Gutenberg.
    
    Args:
        book_ids (list): List of book IDs to download
        session_id (str): Unique session identifier
        
    Returns:
        list: Paths to downloaded book files
    """
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    scraper = GutenbergScraper(upload_dir)
    return scraper.download_books(book_ids)

def analyze_book(session_id, options):
    """
    Analyze books for the given session.
    
    Args:
        session_id (str): Session identifier
        options (dict): Analysis options
        
    Returns:
        bool: True if analysis was successful, False otherwise
    """
    try:
        # Set up directories
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], session_id)
        results_dir = os.path.join(current_app.config['RESULTS_FOLDER'], session_id)
        os.makedirs(results_dir, exist_ok=True)
        
        # Get book files
        book_files = [os.path.join(upload_dir, f) for f in os.listdir(upload_dir) 
                      if f.endswith('.txt') and f != 'options.json']
        
        if not book_files:
            return False
        
        # Process each book
        analyzer = FrequencyAnalyzer()
        book_info = []
        
        for book_file in book_files:
            book_name = os.path.basename(book_file)
            book_id = book_name.split('_')[0] if '_' in book_name else 'custom'
            
            # Read and clean text
            with open(book_file, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
            
            cleaned_text = clean_text(text)
            cleaned_text = remove_punctuation(cleaned_text)
            cleaned_text = normalize_whitespace(cleaned_text)
            
            # Tokenize and process
            tokens = preprocess_text(
                cleaned_text,
                remove_stops=options['remove_stopwords'],
                lemmatize=options['lemmatize']
            )
            
            # Add to analyzer
            analyzer.add_document(book_id, tokens)
            
            # Save book info
            book_info.append({
                'id': book_id,
                'title': book_name.replace('.txt', ''),
                'total_words': len(tokens),
                'unique_words': len(set(tokens))
            })
        
        # Create visualizations directory
        viz_dir = os.path.join(results_dir, 'visualizations')
        os.makedirs(viz_dir, exist_ok=True)
        
        # Analyze corpus
        corpus_freq = analyzer.get_corpus_frequency()
        top_words = analyzer.get_top_words_df(corpus_freq, options['top_words'])
        
        # Generate visualizations if requested
        if options['generate_wordcloud']:
            wordcloud_path = os.path.join(viz_dir, 'corpus_wordcloud.png')
            generate_wordcloud(corpus_freq, title='Corpus Word Cloud', output_path=wordcloud_path)
        
        if options['generate_charts']:
            top_words_path = os.path.join(viz_dir, 'top_words.png')
            plot_top_words(
                top_words.head(20), 
                title='Top 20 Words in Corpus', 
                output_path=top_words_path
            )
            
            freq_hist_path = os.path.join(viz_dir, 'frequency_histogram.png')
            plot_word_frequency_histogram(
                list(corpus_freq.values()),
                title='Word Frequency Distribution',
                output_path=freq_hist_path
            )
        
        # Save top words data
        top_words_data = top_words.to_dict(orient='records')
        with open(os.path.join(results_dir, 'top_words.json'), 'w') as f:
            json.dump(top_words_data, f)
        
        # Save summary data
        summary = {
            'books': book_info,
            'total_unique_words': len(corpus_freq),
            'analysis_time': str(datetime.now()),
            'options': options
        }
        
        with open(os.path.join(results_dir, 'summary.json'), 'w') as f:
            json.dump(summary, f)
        
        return True
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return False

def generate_visualizations(session_id):
    """
    Generate visualizations for the analyzed books.
    
    Args:
        session_id (str): Session identifier
        
    Returns:
        bool: True if successful, False otherwise
    """
    # This functionality is included in the analyze_book function
    # but could be separated if needed
    return True

def analyze_themes(session_id):
    """
    Perform theme analysis across books.
    
    Args:
        session_id (str): Session identifier
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        results_dir = os.path.join(current_app.config['RESULTS_FOLDER'], session_id)
        themes_dir = os.path.join(results_dir, 'themes')
        os.makedirs(themes_dir, exist_ok=True)
        
        # Load summary to get book info
        with open(os.path.join(results_dir, 'summary.json'), 'r') as f:
            summary = json.load(f)
        
        # Need at least 2 books for theme analysis
        if len(summary['books']) < 2:
            return False
        
        # Load preprocessed tokens for each book
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], session_id)
        analyzer = FrequencyAnalyzer()
        
        for book in summary['books']:
            book_file = next((os.path.join(upload_dir, f) for f in os.listdir(upload_dir)
                             if f.startswith(f"{book['id']}_")), None)
            
            if book_file:
                with open(book_file, 'r', encoding='utf-8', errors='replace') as f:
                    text = f.read()
                
                # Clean and preprocess
                cleaned_text = clean_text(text)
                cleaned_text = remove_punctuation(cleaned_text)
                cleaned_text = normalize_whitespace(cleaned_text)
                
                # Tokenize
                tokens = preprocess_text(
                    cleaned_text,
                    remove_stops=summary['options']['remove_stopwords'],
                    lemmatize=summary['options']['lemmatize']
                )
                
                analyzer.add_document(book['id'], tokens)
        
        # Prepare documents for theme analysis
        doc_names = list(analyzer.document_tokens.keys())
        doc_texts = []
        
        for doc_name in doc_names:
            tokens = analyzer.document_tokens[doc_name]
            doc_texts.append(' '.join(tokens))
        
        # Create theme analyzer with correct parameters for small document collections
        theme_analyzer = ThemeAnalyzer(
            n_topics=min(summary['options']['num_topics'], len(doc_names))
        )
        
        # Set parameters for small document collections
        theme_analyzer.vectorizer.max_df = 1.0
        theme_analyzer.vectorizer.min_df = 1
        
        # Fit the model
        theme_analyzer.fit(doc_texts)
        
        # Get topics
        topics = theme_analyzer.get_topics()
        
        # Get document-topic distribution
        doc_topic_dist = theme_analyzer.get_document_topics()
        
        # Find dominant topic for each document
        dominant_topics = theme_analyzer.find_dominant_topic(doc_names)
        
        # Convert to serializable format
        themes_data = {
            'topics': [
                {'id': i, 'words': words}
                for i, words in enumerate(topics)
            ],
            'document_topics': [
                {
                    'document': doc_name,
                    'topics': [
                        {'topic': i, 'weight': float(weight)}
                        for i, weight in enumerate(doc_topic_dist[j])
                    ]
                }
                for j, doc_name in enumerate(doc_names)
            ],
            'dominant_topics': dominant_topics.to_dict(orient='records')
        }
        
        # Save results
        with open(os.path.join(themes_dir, 'themes.json'), 'w') as f:
            json.dump(themes_data, f)
        
        return True
        
    except Exception as e:
        print(f"Theme analysis error: {e}")
        return False

def compare_books(session_id, book1_id, book2_id):
    """
    Compare two books and generate comparison visualizations.
    
    Args:
        session_id (str): Session identifier
        book1_id (str): ID of the first book
        book2_id (str): ID of the second book
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        results_dir = os.path.join(current_app.config['RESULTS_FOLDER'], session_id)
        comparison_dir = os.path.join(results_dir, 'comparisons')
        viz_dir = os.path.join(comparison_dir, 'visualizations')
        os.makedirs(comparison_dir, exist_ok=True)
        os.makedirs(viz_dir, exist_ok=True)
        
        # Load summary to get book info
        with open(os.path.join(results_dir, 'summary.json'), 'r') as f:
            summary = json.load(f)
        
        # Load preprocessed tokens for each book
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], session_id)
        analyzer = FrequencyAnalyzer()
        
        # Find the two books to compare
        for book in summary['books']:
            if book['id'] in [book1_id, book2_id]:
                book_file = next((os.path.join(upload_dir, f) for f in os.listdir(upload_dir)
                                if f.startswith(f"{book['id']}_")), None)
                
                if book_file:
                    with open(book_file, 'r', encoding='utf-8', errors='replace') as f:
                        text = f.read()
                    
                    # Clean and preprocess
                    cleaned_text = clean_text(text)
                    cleaned_text = remove_punctuation(cleaned_text)
                    cleaned_text = normalize_whitespace(cleaned_text)
                    
                    # Tokenize
                    tokens = preprocess_text(
                        cleaned_text,
                        remove_stops=summary['options']['remove_stopwords'],
                        lemmatize=summary['options']['lemmatize']
                    )
                    
                    analyzer.add_document(book['id'], tokens)
        
        # Compare the two books
        comparison = analyzer.compare_documents(book1_id, book2_id, 50)
        
        # Generate comparison visualizations
        comparison_viz_path = os.path.join(viz_dir, f'{book1_id}_vs_{book2_id}_comparison.png')
        plot_comparative_frequencies(
            comparison.head(20),
            title=f'Word Frequency Comparison',
            output_path=comparison_viz_path
        )
        
        # Generate comparative word cloud
        wordcloud_path = os.path.join(viz_dir, f'{book1_id}_vs_{book2_id}_wordcloud.png')
        generate_comparative_wordcloud(
            analyzer.get_document_frequency(book1_id),
            analyzer.get_document_frequency(book2_id),
            labels=(book1_id, book2_id),
            title='Word Cloud Comparison',
            output_path=wordcloud_path
        )
        
        # Save comparison data
        comparison_data = comparison.to_dict(orient='records')
        with open(os.path.join(comparison_dir, f'{book1_id}_vs_{book2_id}.json'), 'w') as f:
            json.dump(comparison_data, f)
        
        return True
        
    except Exception as e:
        print(f"Comparison error: {e}")
        return False

def get_available_books():
    """
    Get a list of previously analyzed books.
    
    Returns:
        list: List of dictionaries containing book information
    """
    available_books = []
    results_dir = current_app.config['RESULTS_FOLDER']
    
    if os.path.exists(results_dir):
        for session_id in os.listdir(results_dir):
            summary_path = os.path.join(results_dir, session_id, 'summary.json')
            if os.path.exists(summary_path):
                try:
                    with open(summary_path, 'r') as f:
                        summary = json.load(f)
                        for book in summary['books']:
                            book_info = {
                                'id': book['id'],
                                'title': book['title'],
                                'session_id': session_id
                            }
                            available_books.append(book_info)
                except Exception:
                    pass
    
    return available_books