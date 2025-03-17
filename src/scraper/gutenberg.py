# ------ src/scraper/gutenberg.py ------

import os
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from src.scraper.utils import clean_filename, ensure_directory_exists

class GutenbergScraper:
    """
    A scraper for downloading books from Project Gutenberg.
    """
    BASE_URL = "https://www.gutenberg.org"
    EBOOKS_URL = urljoin(BASE_URL, "/ebooks/")
    DELAY_MIN = 1  # Minimum delay in seconds between requests
    DELAY_MAX = 3  # Maximum delay in seconds between requests
    
    def __init__(self, output_directory, language='en'):
        """
        Initialize the scraper with an output directory and language filter.
        
        Args:
            output_directory (str): Directory to save downloaded books
            language (str): Language code to filter books (e.g., 'en' for English)
        """
        self.output_directory = output_directory
        self.language = language
        ensure_directory_exists(output_directory)
        
    def get_book_url(self, book_id):
        """
        Generate the URL for a specific book based on its ID.
        
        Args:
            book_id (int): The unique identifier for the book
            
        Returns:
            str: The URL to the book page
        """
        return urljoin(self.EBOOKS_URL, str(book_id))
    
    def download_book(self, book_id):
        """
        Download a book from Project Gutenberg by its ID.
        
        Args:
            book_id (int): The unique identifier for the book
            
        Returns:
            str: Path to the saved file if successful, None otherwise
        """
        try:
            # Add a random delay to avoid overloading the server
            delay = random.uniform(self.DELAY_MIN, self.DELAY_MAX)
            time.sleep(delay)
            
            # Get the book page
            book_url = self.get_book_url(book_id)
            response = requests.get(book_url)
            response.raise_for_status()
            
            # Parse the page to find links to the text version
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find book title for filename
            title_elem = soup.find('h1', {'itemprop': 'name'})
            if title_elem:
                title = title_elem.text.strip()
            else:
                title = f"book_{book_id}"
            
            # Look for the text format link
            text_link = None
            for link in soup.find_all('a'):
                if 'Plain Text' in link.text and '.txt' in link.get('href', ''):
                    text_link = urljoin(self.BASE_URL, link['href'])
                    break
                    
            if not text_link:
                print(f"Could not find text version for book {book_id}")
                return None
            
            # Download the text version
            text_response = requests.get(text_link)
            text_response.raise_for_status()
            
            # Save to file
            filename = clean_filename(f"{book_id}_{title}.txt")
            filepath = os.path.join(self.output_directory, filename)
            
            with open(filepath, 'wb') as f:
                f.write(text_response.content)
                
            print(f"Successfully downloaded: {filename}")
            return filepath
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading book {book_id}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error downloading book {book_id}: {e}")
            return None
    
    def download_books(self, book_ids):
        """
        Download multiple books from Project Gutenberg.
        
        Args:
            book_ids (list): List of book IDs to download
            
        Returns:
            list: Paths to successfully downloaded books
        """
        downloaded_files = []
        
        for book_id in book_ids:
            filepath = self.download_book(book_id)
            if filepath:
                downloaded_files.append(filepath)
                
        return downloaded_files
        
    def search_books(self, query, max_results=10):
        """
        Search for books on Project Gutenberg.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of dictionaries containing book information
        """
        search_url = urljoin(self.BASE_URL, '/ebooks/search/')
        params = {
            'query': query,
            'language': self.language
        }
        
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Find book entries in search results
            for book_entry in soup.select('.booklink'):
                if len(results) >= max_results:
                    break
                    
                title_elem = book_entry.select_one('.title')
                author_elem = book_entry.select_one('.subtitle')
                link_elem = book_entry.select_one('a')
                
                if title_elem and link_elem:
                    # Extract book ID from the link
                    link = link_elem['href']
                    book_id = link.split('/')[-1]
                    if book_id.isdigit():
                        book_info = {
                            'id': int(book_id),
                            'title': title_elem.text.strip(),
                            'author': author_elem.text.strip() if author_elem else 'Unknown',
                            'url': urljoin(self.BASE_URL, link)
                        }
                        results.append(book_info)
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching for books: {e}")
            return []