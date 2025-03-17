# ------ src/preprocessor/cleaner.py ------

import re
import html
from bs4 import BeautifulSoup

def remove_html_tags(text):
    """
    Remove HTML tags from text.
    
    Args:
        text (str): Text that may contain HTML tags
        
    Returns:
        str: Clean text without HTML tags
    """
    # Use BeautifulSoup to parse and extract text without HTML
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

def remove_project_gutenberg_boilerplate(text):
    """
    Remove Project Gutenberg's header and footer boilerplate.
    
    Args:
        text (str): The full text of a book
        
    Returns:
        str: Text with boilerplate removed
    """
    # Pattern for start of actual book content (after header)
    start_patterns = [
        r"\*\*\* START OF THIS PROJECT GUTENBERG EBOOK .+? \*\*\*",
        r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK .+? \*\*\*",
        r"\*\*\* BEGIN OF THIS PROJECT GUTENBERG EBOOK .+? \*\*\*",
    ]
    
    # Pattern for end of book content (before footer)
    end_patterns = [
        r"\*\*\* END OF THIS PROJECT GUTENBERG EBOOK .+? \*\*\*",
        r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK .+? \*\*\*",
        r"\*\*\* THE END OF THIS PROJECT GUTENBERG EBOOK .+? \*\*\*",
    ]
    
    # Try each pattern
    content_text = text
    
    # Find start of content
    for pattern in start_patterns:
        match = re.search(pattern, content_text)
        if match:
            content_text = content_text[match.end():]
            break
    
    # Find end of content
    for pattern in end_patterns:
        match = re.search(pattern, content_text)
        if match:
            content_text = content_text[:match.start()]
            break
            
    return content_text.strip()

def clean_text(text):
    """
    Clean text by removing HTML, decoding entities, and normalizing whitespace.
    
    Args:
        text (str): Raw text
        
    Returns:
        str: Cleaned text
    """
    # Remove HTML tags if present
    text = remove_html_tags(text)
    
    # Remove Project Gutenberg boilerplate
    text = remove_project_gutenberg_boilerplate(text)
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Normalize whitespace (replace multiple spaces with single space)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def remove_punctuation(text):
    """
    Remove punctuation from text.
    
    Args:
        text (str): Text with punctuation
        
    Returns:
        str: Text without punctuation
    """
    # Replace punctuation with space to ensure word separation
    return re.sub(r'[^\w\s]', ' ', text)

def remove_numbers(text):
    """
    Remove numbers from text.
    
    Args:
        text (str): Text that may contain numbers
        
    Returns:
        str: Text without numbers
    """
    return re.sub(r'\d+', '', text)

def normalize_whitespace(text):
    """
    Normalize whitespace in text (newlines, tabs, multiple spaces).
    
    Args:
        text (str): Text with various whitespace
        
    Returns:
        str: Text with normalized whitespace
    """
    # Replace newlines and tabs with spaces
    text = re.sub(r'[\n\t]', ' ', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
