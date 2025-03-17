# ------ src/preprocessor/tokenizer.py ------

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer

# Ensure NLTK resources are downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

def tokenize_text(text):
    """
    Tokenize text into words.
    
    Args:
        text (str): Text to tokenize
        
    Returns:
        list: List of tokens
    """
    return word_tokenize(text.lower())

def remove_stopwords(tokens, language='english', custom_stopwords=None):
    """
    Remove stopwords from a list of tokens.
    
    Args:
        tokens (list): List of tokens
        language (str): Language for stopwords
        custom_stopwords (list): Additional stopwords to remove
        
    Returns:
        list: Tokens with stopwords removed
    """
    stop_words = set(stopwords.words(language))
    
    if custom_stopwords:
        stop_words.update(custom_stopwords)
        
    return [token for token in tokens if token not in stop_words]

def lemmatize_tokens(tokens):
    """
    Lemmatize tokens to their base form.
    
    Args:
        tokens (list): List of tokens
        
    Returns:
        list: Lemmatized tokens
    """
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokens]

def stem_tokens(tokens):
    """
    Stem tokens to their root form.
    
    Args:
        tokens (list): List of tokens
        
    Returns:
        list: Stemmed tokens
    """
    stemmer = PorterStemmer()
    return [stemmer.stem(token) for token in tokens]

def preprocess_text(text, remove_stops=True, lemmatize=True, stem=False, custom_stopwords=None):
    """
    Complete preprocessing pipeline for text.
    
    Args:
        text (str): Raw text
        remove_stops (bool): Whether to remove stopwords
        lemmatize (bool): Whether to lemmatize tokens
        stem (bool): Whether to stem tokens
        custom_stopwords (list): Additional stopwords to remove
        
    Returns:
        list: Preprocessed tokens
    """
    tokens = tokenize_text(text)
    
    if remove_stops:
        tokens = remove_stopwords(tokens, custom_stopwords=custom_stopwords)
        
    if lemmatize:
        tokens = lemmatize_tokens(tokens)
    elif stem:
        tokens = stem_tokens(tokens)
        
    return tokens