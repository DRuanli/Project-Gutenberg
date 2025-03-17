# ------ src/analyzer/frequency.py ------

from collections import Counter
import pandas as pd
import numpy as np
from src.analyzer.statistics import calculate_tfidf

class FrequencyAnalyzer:
    """
    Analyze word frequencies in texts.
    """
    def __init__(self):
        self.document_tokens = {}  # Dictionary mapping document names to token lists
        
    def add_document(self, name, tokens):
        """
        Add a document's tokens to the analyzer.
        
        Args:
            name (str): Document name or identifier
            tokens (list): List of tokens from the document
        """
        self.document_tokens[name] = tokens
        
    def get_frequency_distribution(self, tokens):
        """
        Get the frequency distribution of tokens.
        
        Args:
            tokens (list): List of tokens
            
        Returns:
            Counter: Token frequency distribution
        """
        return Counter(tokens)
    
    def get_document_frequency(self, document_name):
        """
        Get the frequency distribution for a specific document.
        
        Args:
            document_name (str): Name of the document
            
        Returns:
            Counter: Token frequency distribution for the document
        """
        if document_name not in self.document_tokens:
            raise ValueError(f"Document '{document_name}' not found")
            
        return self.get_frequency_distribution(self.document_tokens[document_name])
    
    def get_corpus_frequency(self):
        """
        Get the frequency distribution across all documents.
        
        Returns:
            Counter: Token frequency distribution for the entire corpus
        """
        all_tokens = []
        for tokens in self.document_tokens.values():
            all_tokens.extend(tokens)
            
        return self.get_frequency_distribution(all_tokens)
    
    def get_top_words(self, frequency_dist, n=10):
        """
        Get the top N most frequent words.
        
        Args:
            frequency_dist (Counter): Frequency distribution
            n (int): Number of top words to return
            
        Returns:
            list: List of (word, count) tuples
        """
        return frequency_dist.most_common(n)
    
    def get_top_words_df(self, frequency_dist, n=10):
        """
        Get the top N most frequent words as a DataFrame.
        
        Args:
            frequency_dist (Counter): Frequency distribution
            n (int): Number of top words to return
            
        Returns:
            DataFrame: DataFrame with words and their frequencies
        """
        top_words = self.get_top_words(frequency_dist, n)
        return pd.DataFrame(top_words, columns=['Word', 'Frequency'])
    
    def compare_documents(self, doc_name1, doc_name2, n=10):
        """
        Compare word frequencies between two documents.
        
        Args:
            doc_name1 (str): First document name
            doc_name2 (str): Second document name
            n (int): Number of top words to compare
            
        Returns:
            DataFrame: DataFrame with comparative frequencies
        """
        if doc_name1 not in self.document_tokens:
            raise ValueError(f"Document '{doc_name1}' not found")
        if doc_name2 not in self.document_tokens:
            raise ValueError(f"Document '{doc_name2}' not found")
            
        freq1 = self.get_document_frequency(doc_name1)
        freq2 = self.get_document_frequency(doc_name2)
        
        # Get unique words from both documents
        all_words = set(freq1.keys()) | set(freq2.keys())
        
        # Create comparison data
        comparison_data = []
        for word in all_words:
            count1 = freq1.get(word, 0)
            count2 = freq2.get(word, 0)
            diff = count1 - count2
            comparison_data.append((word, count1, count2, diff))
            
        # Convert to DataFrame
        df = pd.DataFrame(comparison_data, 
                          columns=['Word', f'{doc_name1} Frequency', 
                                  f'{doc_name2} Frequency', 'Difference'])
        
        # Sort by absolute difference
        return df.sort_values(by='Difference', key=abs, ascending=False).head(n)
    
    def calculate_document_tfidf(self):
        """
        Calculate TF-IDF scores for all words in all documents.
        
        Returns:
            dict: Dictionary mapping document names to word:tfidf dictionaries
        """
        return calculate_tfidf(self.document_tokens)
    
    def get_rare_words(self, frequency_dist, threshold=1):
        """
        Get words that appear less than or equal to a threshold.
        
        Args:
            frequency_dist (Counter): Frequency distribution
            threshold (int): Maximum count to be considered rare
            
        Returns:
            list: List of rare words and their counts
        """
        return [(word, count) for word, count in frequency_dist.items() if count <= threshold]
    
    def get_document_statistics(self, document_name):
        """
        Get basic statistics about a document's vocabulary.
        
        Args:
            document_name (str): Name of the document
            
        Returns:
            dict: Dictionary of statistics
        """
        if document_name not in self.document_tokens:
            raise ValueError(f"Document '{document_name}' not found")
            
        tokens = self.document_tokens[document_name]
        freq_dist = self.get_frequency_distribution(tokens)
        
        return {
            'total_words': len(tokens),
            'unique_words': len(freq_dist),
            'lexical_diversity': len(freq_dist) / len(tokens) if tokens else 0,
            'hapax_legomena': len([word for word, count in freq_dist.items() if count == 1]),
            'average_word_length': np.mean([len(word) for word in tokens]) if tokens else 0
        }