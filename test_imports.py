#!/usr/bin/env python3
"""
Test script to verify that all imports work correctly after fixing dependencies.
This script tests the critical import chain that was failing.
"""

def test_imports():
    """Test all the imports that were causing issues."""
    print("Testing imports...")
    
    try:
        # Test the problematic firecrawl import
        print("1. Testing firecrawl import...")
        from firecrawl import FirecrawlApp
        print("   ✓ firecrawl imported successfully")
        
        # Test pydantic to ensure it's the right version
        print("2. Testing pydantic import...")
        import pydantic
        print(f"   ✓ pydantic {pydantic.VERSION} imported successfully")
        
        # Test the scraper module that was failing
        print("3. Testing scraper module...")
        from src.scraper import WebScraper
        print("   ✓ scraper module imported successfully")
        
        # Test the main chat module
        print("4. Testing chat module...")
        from src.chat import ChatBot
        print("   ✓ chat module imported successfully")
        
        # Test the main app import
        print("5. Testing main app components...")
        from src.query_expander import QueryExpander
        from src.database import VectorStore
        print("   ✓ all main components imported successfully")
        
        print("\n🎉 All imports successful! The app should now work properly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1)