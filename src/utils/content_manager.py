"""
Content and metadata management for the Ontario Building Code scraper.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class ContentManager:
    """Manages content storage and metadata for scraped building code content."""
    
    def __init__(self):
        """Initialize paths and create necessary directories."""
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.content_dir = self.base_dir / "data" / "content"
        self.metadata_dir = self.base_dir / "data" / "metadata"
        self.content_file = self.content_dir / "building_code.txt"
        self.metadata_file = self.metadata_dir / "scrape_info.json"
        
        # Create directories if they don't exist
        self.content_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
    
    def save_content(self, content: str) -> None:
        """
        Save scraped content to file and update metadata.
        
        Parameters
        ----------
        content : str
            The scraped content to save
        """
        with open(self.content_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Update metadata
        self._update_metadata()
    
    def load_content(self) -> Optional[str]:
        """
        Load content from file if it exists.
        
        Returns
        -------
        Optional[str]
            The content if file exists, None otherwise
        """
        if self.content_file.exists():
            with open(self.content_file, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def _update_metadata(self) -> None:
        """Update metadata with current timestamp."""
        metadata = {
            'last_scrape': datetime.now().strftime('%Y%m%d%H%M%S'),
            'file_path': str(self.content_file.relative_to(self.base_dir))
        }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=4)
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Get metadata if it exists.
        
        Returns
        -------
        Optional[Dict[str, Any]]
            Metadata dictionary if file exists, None otherwise
        """
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return None
    
    def needs_update(self, days_threshold: int = 30) -> bool:
        """
        Check if content needs to be updated based on last scrape date.
        
        Parameters
        ----------
        days_threshold : int, default=30
            Number of days after which content should be re-scraped
            
        Returns
        -------
        bool
            True if content needs update, False otherwise
        """
        metadata = self.get_metadata()
        
        if not metadata or not self.content_file.exists():
            return True
            
        last_scrape = datetime.strptime(metadata['last_scrape'], '%Y%m%d%H%M%S')
        days_since_scrape = (datetime.now() - last_scrape).days
        
        return days_since_scrape >= days_threshold
