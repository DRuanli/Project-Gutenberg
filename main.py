# ------ main.py ------

import os
import argparse
import pandas as pd
from src.scraper.gutenberg import GutenbergScraper
from src.preprocessor.cleaner import clean_text, remove_punctuation, normalize_whitespace
from src.preprocessor.tokenizer import preprocess_text
from src.analyzer.frequency import FrequencyAnalyzer
from src.visualizer.charts import plot_top_words, plot_word_frequency_histogram, plot_comparative_frequencies
from src.visualizer.wordcloud import generate_wordcloud, generate_comparative_wordcloud
from src.insights.themes import ThemeAnalyzer
from src.insights.comparisons import ComparativeAnalyzer
from config.config import (
    RAW_DATA_DIR, PROCESSED_DATA_DIR, RESULTS_DIR, 
    VISUALIZATIONS_DIR, REPORTS_DIR,
    CUSTOM_STOPWORDS, TOP_WORDS_COUNT
)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Word Frequency Analysis in Classic Novels')
    
    # Add arguments
    parser.add_argument('--download', action='store_true', 
                       help='Download books from Project Gutenberg')
    parser.add_argument('--book-ids', type=int, nargs='+', 
                       help='Book IDs to download from Project Gutenberg')
    parser.add_argument('--preprocess', action='store_true', 
                       help='Preprocess downloaded books')
    parser.add_argument('--analyze', action='store_true', 
                       help='Analyze word frequencies')
    parser.add_argument('--visualize', action='store_true', 
                       help='Generate visualizations')
    parser.add_argument('--themes', action='store_true', 
                       help='Analyze themes across novels')
    parser.add_argument('--compare', action='store_true', 
                       help='Compare multiple novels')
    parser.add_argument('--all', action='store_true', 
                       help='Run the entire pipeline')
    
    return parser.parse_args()

def download_books(book_ids):
    """Download books from Project Gutenberg."""
    print("Downloading books from Project Gutenberg...")
    
    scraper = GutenbergScraper(RAW_DATA_DIR)
    downloaded_files = scraper.download_books(book_ids)
    
    print(f"Downloaded {len(downloaded_files)} books:")
    for file in downloaded_files:
        print(f"  - {os.path.basename(file)}")
        
    return downloaded_files

def preprocess_books(book_files=None):
    """Preprocess downloaded books."""
    print("Preprocessing books...")
    
    if book_files is None:
        # If no files provided, use all files in the raw data directory
        book_files = [os.path.join(RAW_DATA_DIR, f) for f in os.listdir(RAW_DATA_DIR) 
                     if f.endswith('.txt')]
    
    processed_files = []
    
    for book_file in book_files:
        book_name = os.path.basename(book_file)
        print(f"Processing {book_name}...")
        
        # Read the book
        with open(book_file, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        
        # Clean and preprocess text
        cleaned_text = clean_text(text)
        cleaned_text = remove_punctuation(cleaned_text)
        cleaned_text = normalize_whitespace(cleaned_text)
        
        # Generate tokens
        tokens = preprocess_text(
            cleaned_text, 
            remove_stops=True, 
            lemmatize=True, 
            custom_stopwords=CUSTOM_STOPWORDS
        )
        
        # Create processed filename
        processed_name = os.path.splitext(book_name)[0] + '_processed.txt'
        processed_path = os.path.join(PROCESSED_DATA_DIR, processed_name)
        
        # Save tokens to file (one token per line)
        with open(processed_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(tokens))
            
        processed_files.append(processed_path)
        
    print(f"Preprocessed {len(processed_files)} books.")
    return processed_files

def analyze_books(processed_files=None):
    """Analyze word frequencies in preprocessed books."""
    print("Analyzing word frequencies...")
    
    if processed_files is None:
        # If no files provided, use all processed files
        processed_files = [os.path.join(PROCESSED_DATA_DIR, f) for f in os.listdir(PROCESSED_DATA_DIR) 
                          if f.endswith('_processed.txt')]
    
    analyzer = FrequencyAnalyzer()
    
    # Load processed tokens
    for processed_file in processed_files:
        book_name = os.path.basename(processed_file).replace('_processed.txt', '')
        print(f"Loading {book_name}...")
        
        with open(processed_file, 'r', encoding='utf-8') as f:
            tokens = f.read().splitlines()
            
        analyzer.add_document(book_name, tokens)
    
    # Analyze corpus frequency
    print("Analyzing corpus frequency...")
    corpus_freq = analyzer.get_corpus_frequency()
    top_words = analyzer.get_top_words_df(corpus_freq, TOP_WORDS_COUNT)
    
    # Save results
    corpus_results_path = os.path.join(RESULTS_DIR, 'corpus_frequency.csv')
    top_words.to_csv(corpus_results_path, index=False)
    print(f"Saved corpus frequency results to {corpus_results_path}")
    
    # Analyze individual documents
    for doc_name in analyzer.document_tokens.keys():
        print(f"Analyzing {doc_name}...")
        doc_freq = analyzer.get_document_frequency(doc_name)
        doc_top_words = analyzer.get_top_words_df(doc_freq, TOP_WORDS_COUNT)
        doc_stats = analyzer.get_document_statistics(doc_name)
        
        # Save results
        doc_results_path = os.path.join(RESULTS_DIR, f'{doc_name}_frequency.csv')
        doc_top_words.to_csv(doc_results_path, index=False)
        
        doc_stats_path = os.path.join(RESULTS_DIR, f'{doc_name}_statistics.csv')
        pd.DataFrame([doc_stats]).to_csv(doc_stats_path, index=False)
        
        print(f"Saved {doc_name} results")
    
    # If multiple documents, perform comparative analysis
    if len(analyzer.document_tokens) > 1:
        doc_names = list(analyzer.document_tokens.keys())
        for i in range(len(doc_names)):
            for j in range(i+1, len(doc_names)):
                doc1 = doc_names[i]
                doc2 = doc_names[j]
                print(f"Comparing {doc1} vs {doc2}...")
                
                comparison = analyzer.compare_documents(doc1, doc2, TOP_WORDS_COUNT)
                comparison_path = os.path.join(RESULTS_DIR, f'{doc1}_vs_{doc2}_comparison.csv')
                comparison.to_csv(comparison_path, index=False)
                print(f"Saved comparison to {comparison_path}")
    
    return analyzer

def generate_visualizations(analyzer):
    """Generate visualizations from analysis results."""
    print("Generating visualizations...")
    
    # Generate corpus visualizations
    print("Generating corpus visualizations...")
    corpus_freq = analyzer.get_corpus_frequency()
    
    # Word cloud
    wordcloud_path = os.path.join(VISUALIZATIONS_DIR, 'corpus_wordcloud.png')
    generate_wordcloud(corpus_freq, title='Corpus Word Cloud', output_path=wordcloud_path)
    
    # Top words bar chart
    top_words = analyzer.get_top_words_df(corpus_freq, TOP_WORDS_COUNT)
    top_words_path = os.path.join(VISUALIZATIONS_DIR, 'corpus_top_words.png')
    plot_top_words(top_words.head(20), title='Top 20 Words in Corpus', output_path=top_words_path)
    
    # Word frequency histogram
    freq_hist_path = os.path.join(VISUALIZATIONS_DIR, 'corpus_frequency_histogram.png')
    plot_word_frequency_histogram(
        list(corpus_freq.values()), 
        title='Word Frequency Distribution in Corpus',
        output_path=freq_hist_path
    )
    
    # Generate document-specific visualizations
    for doc_name in analyzer.document_tokens.keys():
        print(f"Generating visualizations for {doc_name}...")
        doc_freq = analyzer.get_document_frequency(doc_name)
        
        # Word cloud
        doc_wordcloud_path = os.path.join(VISUALIZATIONS_DIR, f'{doc_name}_wordcloud.png')
        generate_wordcloud(
            doc_freq, 
            title=f'Word Cloud: {doc_name}',
            output_path=doc_wordcloud_path
        )
        
        # Top words bar chart
        doc_top_words = analyzer.get_top_words_df(doc_freq, TOP_WORDS_COUNT)
        doc_top_words_path = os.path.join(VISUALIZATIONS_DIR, f'{doc_name}_top_words.png')
        plot_top_words(
            doc_top_words.head(20), 
            title=f'Top 20 Words in {doc_name}',
            output_path=doc_top_words_path
        )
    
    # If multiple documents, generate comparative visualizations
    if len(analyzer.document_tokens) > 1:
        doc_names = list(analyzer.document_tokens.keys())
        
        # Lexical diversity comparison
        diversity_data = {
            doc_name: analyzer.get_document_statistics(doc_name)['lexical_diversity']
            for doc_name in doc_names
        }
        
        # Compare first two documents
        doc1, doc2 = doc_names[0], doc_names[1]
        print(f"Generating comparative visualizations for {doc1} vs {doc2}...")
        
        # Comparative word cloud
        comp_wordcloud_path = os.path.join(VISUALIZATIONS_DIR, f'{doc1}_vs_{doc2}_wordcloud.png')
        generate_comparative_wordcloud(
            analyzer.get_document_frequency(doc1),
            analyzer.get_document_frequency(doc2),
            labels=(doc1, doc2),
            title=f'Word Cloud Comparison: {doc1} vs {doc2}',
            output_path=comp_wordcloud_path
        )
        
        # Comparative frequency chart
        comp_freq_path = os.path.join(VISUALIZATIONS_DIR, f'{doc1}_vs_{doc2}_frequency.png')
        comparison = analyzer.compare_documents(doc1, doc2, 20)
        plot_comparative_frequencies(
            comparison,
            title=f'Word Frequency Comparison: {doc1} vs {doc2}',
            output_path=comp_freq_path
        )
    
    print("Visualization generation complete.")

def analyze_themes(analyzer):
    """Analyze themes across novels."""
    print("Analyzing themes across novels...")
    
    # Need at least 2 documents for meaningful theme analysis
    if len(analyzer.document_tokens) < 2:
        print("Need at least 2 documents for theme analysis.")
        return
    
    # Prepare documents for theme analysis
    doc_names = list(analyzer.document_tokens.keys())
    doc_texts = []
    
    for doc_name in doc_names:
        tokens = analyzer.document_tokens[doc_name]
        doc_texts.append(' '.join(tokens))
    
    # Create and fit theme analyzer
    theme_analyzer = ThemeAnalyzer(n_topics=min(5, len(doc_names)))
    theme_analyzer.fit(doc_texts)
    
    # Get topics
    topics_df = theme_analyzer.get_topics_df()
    topics_path = os.path.join(RESULTS_DIR, 'topics.csv')
    topics_df.to_csv(topics_path, index=False)
    print(f"Saved topics to {topics_path}")
    
    # Get document-topic distribution
    doc_topics_df = theme_analyzer.get_document_topics_df(doc_names)
    doc_topics_path = os.path.join(RESULTS_DIR, 'document_topics.csv')
    doc_topics_df.to_csv(doc_topics_path)
    print(f"Saved document-topic distribution to {doc_topics_path}")
    
    # Find dominant topic for each document
    dominant_topics_df = theme_analyzer.find_dominant_topic(doc_names)
    dominant_topics_path = os.path.join(RESULTS_DIR, 'dominant_topics.csv')
    dominant_topics_df.to_csv(dominant_topics_path, index=False)
    print(f"Saved dominant topics to {dominant_topics_path}")
    
    return theme_analyzer

def compare_novels(analyzer):
    """Compare multiple novels."""
    print("Comparing novels...")
    
    # Need at least 2 documents for comparison
    if len(analyzer.document_tokens) < 2:
        print("Need at least 2 documents for comparison.")
        return
    
    # Create comparative analyzer
    comparative_analyzer = ComparativeAnalyzer(analyzer.document_tokens)
    
    # Calculate similarity matrix
    similarity_matrix = comparative_analyzer.calculate_similarity_matrix()
    similarity_path = os.path.join(RESULTS_DIR, 'similarity_matrix.csv')
    similarity_matrix.to_csv(similarity_path)
    print(f"Saved similarity matrix to {similarity_path}")
    
    # Compare first two documents in detail
    doc_names = list(analyzer.document_tokens.keys())
    doc1, doc2 = doc_names[0], doc_names[1]
    
    # Rank words by difference
    word_diff_df = comparative_analyzer.rank_words_by_difference(doc1, doc2)
    word_diff_path = os.path.join(RESULTS_DIR, f'{doc1}_vs_{doc2}_word_diff.csv')
    word_diff_df.to_csv(word_diff_path, index=False)
    print(f"Saved word difference ranking to {word_diff_path}")
    
    # Get unique words for each document
    for doc_name in doc_names:
        unique_words = comparative_analyzer.get_unique_words(doc_name)
        unique_df = pd.DataFrame(unique_words, columns=['Word', 'Frequency'])
        unique_path = os.path.join(RESULTS_DIR, f'{doc_name}_unique_words.csv')
        unique_df.to_csv(unique_path, index=False)
        print(f"Saved unique words for {doc_name} to {unique_path}")
    
    # Compare word ranks between all document pairs
    rank_correlations = []
    for i in range(len(doc_names)):
        for j in range(i+1, len(doc_names)):
            doc1, doc2 = doc_names[i], doc_names[j]
            correlation, p_value = comparative_analyzer.compare_word_ranks(doc1, doc2)
            rank_correlations.append((doc1, doc2, correlation, p_value))
    
    # Save rank correlations
    rank_df = pd.DataFrame(rank_correlations, 
                          columns=['Document 1', 'Document 2', 'Correlation', 'P-Value'])
    rank_path = os.path.join(RESULTS_DIR, 'rank_correlations.csv')
    rank_df.to_csv(rank_path, index=False)
    print(f"Saved rank correlations to {rank_path}")
    
    return comparative_analyzer

def run_pipeline(args):
    """Run the complete analysis pipeline."""
    # Download books if requested
    if args.download or args.all:
        if args.book_ids:
            book_files = download_books(args.book_ids)
        else:
            # Default books to download if none specified
            default_books = [84, 1342, 11, 1661, 98]  # Frankenstein, Pride and Prejudice, Alice in Wonderland, Sherlock Holmes, Tale of Two Cities
            book_files = download_books(default_books)
    else:
        book_files = None
    
    # Preprocess books
    if args.preprocess or args.all:
        processed_files = preprocess_books(book_files)
    else:
        processed_files = None
    
    # Analyze books
    if args.analyze or args.visualize or args.themes or args.compare or args.all:
        analyzer = analyze_books(processed_files)
    else:
        return
    
    # Generate visualizations
    if args.visualize or args.all:
        generate_visualizations(analyzer)
    
    # Analyze themes
    if args.themes or args.all:
        theme_analyzer = analyze_themes(analyzer)
    
    # Compare novels
    if args.compare or args.all:
        comparative_analyzer = compare_novels(analyzer)

if __name__ == "__main__":
    args = parse_arguments()
    run_pipeline(args)