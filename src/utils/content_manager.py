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
        print("\n[ContentManager] Initializing...")
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.content_dir = self.base_dir / "data" / "content"
        self.metadata_dir = self.base_dir / "data" / "metadata"
        self.content_file = self.content_dir / "building_code.txt"
        self.metadata_file = self.metadata_dir / "scrape_info.json"
        
        # Create directories if they don't exist
        self.content_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        print(f"[ContentManager] Content file: {self.content_file}")
        print(f"[ContentManager] Metadata file: {self.metadata_file}")
        print("[ContentManager] Initialization complete")
    
    def save_content(self, content: str) -> None:
        """
        Save scraped content to file and update metadata.
        
        Parameters
        ----------
        content : str
            The scraped content to save
        """
        print(f"\n[ContentManager] Saving content ({len(content)} characters)...")
        with open(self.content_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("[ContentManager] Content saved to file")
        
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
            print(f"[ContentManager] Loading content from {self.content_file}")
            with open(self.content_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"[ContentManager] Loaded {len(content)} characters")
            return content
        print("[ContentManager] Content file not found")
        return None
    
    def _update_metadata(self) -> None:
        """Update metadata with current timestamp."""
        print("[ContentManager] Updating metadata...")
        metadata = {
            'last_scrape': datetime.now().strftime('%Y%m%d%H%M%S'),
            'file_path': str(self.content_file.relative_to(self.base_dir))
        }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=4)
        print("[ContentManager] Metadata updated")
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Get metadata if it exists.
        
        Returns
        -------
        Optional[Dict[str, Any]]
            Metadata dictionary if file exists, None otherwise
        """
        if self.metadata_file.exists():
            print("[ContentManager] Loading metadata...")
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
            print(f"[ContentManager] Metadata loaded: {metadata}")
            return metadata
        print("[ContentManager] No metadata file found")
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
        print(f"\n[ContentManager] Checking if content needs update (threshold: {days_threshold} days)")
        metadata = self.get_metadata()
        
        if not metadata or not self.content_file.exists():
            print("[ContentManager] No metadata or content file, update needed")
            return True
            
        last_scrape = datetime.strptime(metadata['last_scrape'], '%Y%m%d%H%M%S')
        days_since_scrape = (datetime.now() - last_scrape).days
        
        needs_update = days_since_scrape >= days_threshold
        print(f"[ContentManager] Days since last scrape: {days_since_scrape}")
        print(f"[ContentManager] Needs update: {needs_update}")
        
        return needs_update
