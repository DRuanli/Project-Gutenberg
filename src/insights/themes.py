# ------ src/insights/themes.py ------

import pandas as pd
import numpy as np
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

class ThemeAnalyzer:
    """
    Analyze themes in texts using topic modeling.
    """
    def __init__(self, n_topics=5, n_top_words=10):
        """
        Initialize the theme analyzer.
        
        Args:
            n_topics (int): Number of topics to extract
            n_top_words (int): Number of top words per topic
        """
        self.n_topics = n_topics
        self.n_top_words = n_top_words
        self.vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
        self.lda = LatentDirichletAllocation(
            n_components=n_topics,
            max_iter=10,
            learning_method='online',
            random_state=42
        )
        
    def fit(self, documents):
        """
        Fit the topic model to documents.
        
        Args:
            documents (list): List of preprocessed document texts
            
        Returns:
            self: The fitted model
        """
        self.doc_term_matrix = self.vectorizer.fit_transform(documents)
        self.lda.fit(self.doc_term_matrix)
        return self
    
    def get_topics(self):
        """
        Get the top words for each topic.
        
        Returns:
            list: List of topic word lists
        """
        feature_names = self.vectorizer.get_feature_names_out()
        topics = []
        
        for topic_idx, topic in enumerate(self.lda.components_):
            top_words_idx = topic.argsort()[:-self.n_top_words-1:-1]
            top_words = [feature_names[i] for i in top_words_idx]
            topics.append(top_words)
            
        return topics
    
    def get_topics_df(self):
        """
        Get topics as a DataFrame.
        
        Returns:
            DataFrame: DataFrame with topic words
        """
        topics = self.get_topics()
        df = pd.DataFrame()
        
        for i, topic_words in enumerate(topics):
            df[f'Topic {i+1}'] = topic_words
            
        return df
    
    def get_document_topics(self, documents=None):
        """
        Get topic distribution for documents.
        
        Args:
            documents (list): List of document texts (if None, use fitted documents)
            
        Returns:
            array: Document-topic distribution matrix
        """
        if documents is None:
            return self.lda.transform(self.doc_term_matrix)
        else:
            doc_term_matrix = self.vectorizer.transform(documents)
            return self.lda.transform(doc_term_matrix)
            
    def get_document_topics_df(self, doc_names, documents=None):
        """
        Get document-topic distribution as a DataFrame.
        
        Args:
            doc_names (list): List of document names
            documents (list): List of document texts (if None, use fitted documents)
            
        Returns:
            DataFrame: DataFrame with document-topic distributions
        """
        doc_topic_dist = self.get_document_topics(documents)
        
        # Create column names for topics
        topic_cols = [f'Topic {i+1}' for i in range(self.n_topics)]
        
        # Create DataFrame
        df = pd.DataFrame(doc_topic_dist, index=doc_names, columns=topic_cols)
        
        return df
    
    def find_dominant_topic(self, doc_names, documents=None):
        """
        Find the dominant topic for each document.
        
        Args:
            doc_names (list): List of document names
            documents (list): List of document texts (if None, use fitted documents)
            
        Returns:
            DataFrame: DataFrame with dominant topics
        """
        doc_topic_dist = self.get_document_topics(documents)
        
        # Find dominant topic for each document
        dominant_topics = np.argmax(doc_topic_dist, axis=1)
        dominant_probs = np.max(doc_topic_dist, axis=1)
        
        # Get topic words
        topics = self.get_topics()
        
        # Create DataFrame
        data = []
        for i, (doc_name, topic_idx, prob) in enumerate(zip(doc_names, dominant_topics, dominant_probs)):
            topic_words = ', '.join(topics[topic_idx][:5])  # Top 5 words
            data.append((doc_name, int(topic_idx), float(prob), topic_words))
            
        df = pd.DataFrame(data, columns=['Document', 'Dominant Topic', 'Topic Probability', 'Topic Words'])
        
        return df.sort_values(by='Dominant Topic')