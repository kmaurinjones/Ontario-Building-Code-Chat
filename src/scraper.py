"""
Web scraper and text processor for Ontario Building Code.

This module handles the fetching and initial processing of content from the Ontario Building Code website
using the Firecrawl API.
"""
import os
from pathlib import Path
from typing import List, Tuple
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from tqdm import tqdm
from .utils.token_counter import chunk_text
from .utils.content_manager import ContentManager

class WebScraper:
    """Handles web scraping and text processing for the Ontario Building Code."""
    
    def __init__(self, url: str):
        """
        Initialize the scraper with the target URL.
        
        Parameters
        ----------
        url : str
            The URL to scrape
        """
        self.url = url
        self.content_manager = ContentManager()
        
        # Load environment variables
        load_dotenv()
        api_key = os.getenv('FIRECRAWL_API_KEY')
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment variables")
            
        self.app = FirecrawlApp(api_key=api_key)
    
    def get_content(self, force_update: bool = False) -> str:
        """
        Get content either from cache or by fetching from web.
        
        Parameters
        ----------
        force_update : bool, default=False
            If True, forces a new fetch regardless of cache state
            
        Returns
        -------
        str
            Building code content
        """
        if not force_update and not self.content_manager.needs_update():
            cached_content = self.content_manager.load_content()
            if cached_content:
                return cached_content
        
        # Fetch new content if needed
        content = self.fetch_content()
        self.content_manager.save_content(content)
        return content
    
    def fetch_content(self) -> str:
        """
        Fetches content from the Ontario Building Code webpage using Firecrawl API.
        
        Returns
        -------
        str
            Markdown content from the webpage
            
        Raises
        ------
        Exception
            If the API request fails or returns an error
        """
        try:
            response = self.app.scrape_url(
                url=self.url,
                params={'formats': ['markdown']}
            )
            
            if not response.get('markdown'):
                raise ValueError("No markdown content found in API response")
                
            return response['markdown']
            
        except Exception as e:
            raise Exception(f"Failed to fetch content: {str(e)}")
    
    def process_content(self, text: str, max_tokens: int = 8000, overlap_tokens: int = 200) -> List[Tuple[str, int]]:
        """
        Process and chunk the content into token-sized pieces.
        
        Parameters
        ----------
        text : str
            Input text to process
        max_tokens : int, default=8000
            Maximum number of tokens per chunk
        overlap_tokens : int, default=200
            Number of tokens to overlap between chunks
            
        Returns
        -------
        List[Tuple[str, int]]
            List of (chunk_text, token_count) tuples
        """
        return chunk_text(text, max_tokens, overlap_tokens)

# Sample code to test the scraper
if __name__ == "__main__":
    scraper = WebScraper("https://www.ontario.ca/laws/regulation/120332/v25")
    
    print("Getting content...")
    content = scraper.get_content()
    print(f"\nContent length: {len(content)}")
    
    print("\nFirst 500 characters of content:")
    print("-" * 80)
    print(content[:500])
    print("-" * 80)
    
    chunks = scraper.process_content(
        text=content,
        max_tokens=8000,
        overlap_tokens=200
    )
    
    print(f"\nTotal chunks: {len(chunks)}")
    total_tokens = sum(chunk[1] for chunk in chunks)
    print(f"Total tokens: {total_tokens:,}")
