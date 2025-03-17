# ------ src/insights/comparisons.py ------

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import spearmanr
from collections import defaultdict

class ComparativeAnalyzer:
    """
    Analyze and compare word usage patterns across documents.
    """
    def __init__(self, document_tokens):
        """
        Initialize with document tokens.
        
        Args:
            document_tokens (dict): Dictionary mapping document names to token lists
        """
        self.document_tokens = document_tokens
        self.document_freqs = self._calculate_document_freqs()
        
    def _calculate_document_freqs(self):
        """
        Calculate word frequency dictionaries for each document.
        
        Returns:
            dict: Dictionary mapping document names to word frequency dictionaries
        """
        document_freqs = {}
        for doc_name, tokens in self.document_tokens.items():
            freq_dict = defaultdict(int)
            for token in tokens:
                freq_dict[token] += 1
            document_freqs[doc_name] = dict(freq_dict)
        return document_freqs
    
    def get_unique_words(self, doc_name):
        """
        Get words that appear only in one document.
        
        Args:
            doc_name (str): Document name
            
        Returns:
            list: List of unique words
        """
        if doc_name not in self.document_freqs:
            raise ValueError(f"Document '{doc_name}' not found")
            
        # Get words in this document
        doc_words = set(self.document_freqs[doc_name].keys())
        
        # Get words in all other documents
        other_words = set()
        for other_doc, other_freq in self.document_freqs.items():
            if other_doc != doc_name:
                other_words.update(other_freq.keys())
                
        # Find words unique to this document
        unique_words = doc_words - other_words
        
        # Return as list with frequencies
        return [(word, self.document_freqs[doc_name][word]) for word in unique_words]
    
    def calculate_similarity_matrix(self, method='cosine'):
        """
        Calculate similarity matrix between all documents.
        
        Args:
            method (str): Similarity method ('cosine' or 'jaccard')
            
        Returns:
            DataFrame: Similarity matrix as DataFrame
        """
        doc_names = list(self.document_tokens.keys())
        n_docs = len(doc_names)
        similarity_matrix = np.zeros((n_docs, n_docs))
        
        if method == 'cosine':
            # Get all unique words across all documents
            all_words = set()
            for tokens in self.document_tokens.values():
                all_words.update(tokens)
                
            # Create feature vectors
            vectors = []
            for doc_name in doc_names:
                freq_dict = self.document_freqs[doc_name]
                vector = [freq_dict.get(word, 0) for word in all_words]
                vectors.append(vector)
                
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(vectors)
                
        elif method == 'jaccard':
            # Calculate Jaccard similarity
            for i, doc1 in enumerate(doc_names):
                for j, doc2 in enumerate(doc_names):
                    if i == j:
                        similarity_matrix[i, j] = 1.0
                    else:
                        set1 = set(self.document_tokens[doc1])
                        set2 = set(self.document_tokens[doc2])
                        intersection = len(set1.intersection(set2))
                        union = len(set1.union(set2))
                        similarity_matrix[i, j] = intersection / union if union > 0 else 0.0
        else:
            raise ValueError(f"Unknown similarity method: {method}")
            
        return pd.DataFrame(similarity_matrix, index=doc_names, columns=doc_names)
    
    def rank_words_by_difference(self, doc1, doc2, top_n=20):
        """
        Rank words by their relative frequency difference between two documents.
        
        Args:
            doc1 (str): First document name
            doc2 (str): Second document name
            top_n (int): Number of top words to return
            
        Returns:
            DataFrame: DataFrame with ranked words
        """
        if doc1 not in self.document_freqs:
            raise ValueError(f"Document '{doc1}' not found")
        if doc2 not in self.document_freqs:
            raise ValueError(f"Document '{doc2}' not found")
            
        # Get word frequencies
        freq1 = self.document_freqs[doc1]
        freq2 = self.document_freqs[doc2]
        
        # Get total word counts
        total1 = sum(freq1.values())
        total2 = sum(freq2.values())
        
        # Calculate relative frequencies and differences
        all_words = set(freq1.keys()) | set(freq2.keys())
        word_diffs = []
        
        for word in all_words:
            rel_freq1 = freq1.get(word, 0) / total1 if total1 > 0 else 0
            rel_freq2 = freq2.get(word, 0) / total2 if total2 > 0 else 0
            diff = rel_freq1 - rel_freq2
            word_diffs.append((word, rel_freq1, rel_freq2, diff))
            
        # Convert to DataFrame
        df = pd.DataFrame(word_diffs, columns=['Word', f'{doc1} Rel. Freq.', 
                                              f'{doc2} Rel. Freq.', 'Difference'])
        
        # Sort by absolute difference
        return df.sort_values(by='Difference', key=abs, ascending=False).head(top_n)
    
    def compare_word_ranks(self, doc1, doc2):
        """
        Compare word ranking between two documents using Spearman correlation.
        
        Args:
            doc1 (str): First document name
            doc2 (str): Second document name
            
        Returns:
            tuple: (correlation coefficient, p-value)
        """
        if doc1 not in self.document_freqs:
            raise ValueError(f"Document '{doc1}' not found")
        if doc2 not in self.document_freqs:
            raise ValueError(f"Document '{doc2}' not found")
            
        # Get common words
        words1 = set(self.document_freqs[doc1].keys())
        words2 = set(self.document_freqs[doc2].keys())
        common_words = words1.intersection(words2)
        
        if len(common_words) < 2:
            return (0, 1.0)  # No correlation can be calculated
            
        # Get ranks in each document
        ranks1 = []
        ranks2 = []
        
        for word in common_words:
            ranks1.append(self.document_freqs[doc1][word])
            ranks2.append(self.document_freqs[doc2][word])
            
        # Calculate Spearman correlation
        return spearmanr(ranks1, ranks2)