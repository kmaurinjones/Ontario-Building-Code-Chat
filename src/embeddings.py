"""
Text embedding generation using OpenAI's API.
"""
from openai import OpenAI
from typing import List, Union
import os

class EmbeddingGenerator:
    """Handles the generation of embeddings using OpenAI's API."""
    
    def __init__(self):
        # Initialize OpenAI client with the current API key (which may have been updated during auth)
        self.client = OpenAI()
        self.model = "text-embedding-3-small"
    
    def generate_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        Generates embeddings for given text(s).
        
        Parameters
        ----------
        texts : Union[str, List[str]]
            Single text string or list of text strings to embed
            
        Returns
        -------
        List[List[float]]
            List of embedding vectors
        """
        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]
            
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [data.embedding for data in response.data]
            
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
