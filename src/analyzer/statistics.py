# ------ src/analyzer/statistics.py ------

import math
from collections import Counter

def calculate_tfidf(document_tokens):
    """
    Calculate TF-IDF (Term Frequency-Inverse Document Frequency) scores.
    
    Args:
        document_tokens (dict): Dictionary mapping document names to token lists
        
    Returns:
        dict: Dictionary mapping document names to word:tfidf dictionaries
    """
    # Calculate document frequencies (how many documents contain each word)
    document_freq = Counter()
    for tokens in document_tokens.values():
        # Count each word only once per document
        document_freq.update(set(tokens))
    
    # Total number of documents
    n_documents = len(document_tokens)
    
    # Calculate TF-IDF for each word in each document
    tfidf_scores = {}
    
    for doc_name, tokens in document_tokens.items():
        # Calculate term frequencies for this document
        term_freq = Counter(tokens)
        total_terms = len(tokens)
        
        # Calculate TF-IDF for each term
        doc_tfidf = {}
        for term, tf in term_freq.items():
            # Normalized term frequency
            normalized_tf = tf / total_terms
            
            # Inverse document frequency
            idf = math.log(n_documents / document_freq[term])
            
            # TF-IDF score
            doc_tfidf[term] = normalized_tf * idf
            
        tfidf_scores[doc_name] = doc_tfidf
        
    return tfidf_scores

def calculate_lexical_diversity(tokens):
    """
    Calculate lexical diversity (unique words / total words).
    
    Args:
        tokens (list): List of tokens
        
    Returns:
        float: Lexical diversity score
    """
    if not tokens:
        return 0
    return len(set(tokens)) / len(tokens)

def calculate_readability_metrics(text):
    """
    Calculate various readability metrics for text.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Dictionary of readability metrics
    """
    # Count sentences, words, and syllables
    sentences = len([s for s in text.split('.') if s.strip()])
    words = len(text.split())
    
    if sentences == 0 or words == 0:
        return {
            'flesch_kincaid_grade': None,
            'flesch_reading_ease': None,
            'average_words_per_sentence': None
        }
    
    # Approximate syllable count (not perfect but a reasonable estimate)
    def count_syllables(word):
        word = word.lower()
        if len(word) <= 3:
            return 1
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for i in range(1, len(word)):
            if word[i] in vowels and word[i-1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
            count += 1
        if count == 0:
            count = 1
        return count
    
    syllables = sum(count_syllables(word) for word in text.split())
    
    # Calculate metrics
    avg_words_per_sentence = words / sentences
    flesch_reading_ease = 206.835 - 1.015 * avg_words_per_sentence - 84.6 * (syllables / words)
    flesch_kincaid_grade = 0.39 * avg_words_per_sentence + 11.8 * (syllables / words) - 15.59
    
    return {
        'flesch_kincaid_grade': flesch_kincaid_grade,
        'flesch_reading_ease': flesch_reading_ease,
        'average_words_per_sentence': avg_words_per_sentence
    }

def similarity_score(doc1_tokens, doc2_tokens):
    """
    Calculate similarity between two documents using Jaccard similarity.
    
    Args:
        doc1_tokens (list): Tokens from first document
        doc2_tokens (list): Tokens from second document
        
    Returns:
        float: Similarity score between 0 and 1
    """
    set1 = set(doc1_tokens)
    set2 = set(doc2_tokens)
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    if union == 0:
        return 0
    
    return intersection / union