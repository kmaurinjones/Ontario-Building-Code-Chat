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
        print("\n[WebScraper] Initializing with URL:", url)
        self.url = url
        self.content_manager = ContentManager()
        
        # Load environment variables
        load_dotenv()
        api_key = os.getenv('FIRECRAWL_API_KEY')
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment variables")
            
        self.app = FirecrawlApp(api_key=api_key)
        print("[WebScraper] Initialization complete")
    
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
        print(f"\n[WebScraper] Getting content (force_update={force_update})")
        
        if not force_update and not self.content_manager.needs_update():
            print("[WebScraper] Checking cache...")
            cached_content = self.content_manager.load_content()
            if cached_content:
                content_length = len(cached_content)
                print(f"[WebScraper] Found cached content ({content_length} characters)")
                return cached_content
            print("[WebScraper] No cached content found")
        else:
            if force_update:
                print("[WebScraper] Force update requested")
            else:
                print("[WebScraper] Cache needs update")
        
        # Fetch new content if needed
        print("[WebScraper] Fetching new content from web...")
        content = self.fetch_content()
        content_length = len(content)
        print(f"[WebScraper] Fetched {content_length} characters of content")
        
        print("[WebScraper] Saving content to cache...")
        self.content_manager.save_content(content)
        print("[WebScraper] Content saved")
        
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
            print("[WebScraper] Making API request to Firecrawl...")
            response = self.app.scrape_url(
                url=self.url,
                params={'formats': ['markdown']}
            )
            
            if not response.get('markdown'):
                raise ValueError("No markdown content found in API response")
            
            content_length = len(response['markdown'])
            print(f"[WebScraper] API request successful ({content_length} characters)")
            return response['markdown']
            
        except Exception as e:
            print(f"[WebScraper] Error fetching content: {str(e)}")
            raise Exception(f"Failed to fetch content: {str(e)}")
    
    def process_content(self, text: str, max_tokens: int = 2000, overlap_tokens: int = 200) -> List[Tuple[str, int]]:
        """
        Process and chunk the content into token-sized pieces.
        
        Parameters
        ----------
        text : str
            Input text to process
        max_tokens : int, default=2000
            Maximum number of tokens per chunk
        overlap_tokens : int, default=200
            Number of tokens to overlap between chunks
            
        Returns
        -------
        List[Tuple[str, int]]
            List of (chunk_text, token_count) tuples
        """
        print(f"\n[WebScraper] Processing content into chunks (max_tokens={max_tokens}, overlap={overlap_tokens})")
        chunks = chunk_text(text, max_tokens, overlap_tokens)
        print(f"[WebScraper] Created {len(chunks)} chunks")
        
        # Print some chunk statistics
        total_tokens = sum(chunk[1] for chunk in chunks)
        avg_tokens = total_tokens / len(chunks)
        print(f"[WebScraper] Total tokens: {total_tokens}")
        print(f"[WebScraper] Average tokens per chunk: {avg_tokens:.2f}")
        
        return chunks
