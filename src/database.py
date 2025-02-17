"""
Vector database management using ChromaDB.
"""
import os
import chromadb
import numpy as np
from chromadb.config import Settings
from pathlib import Path
from typing import List, Tuple, Dict, Any, Union
from .embeddings import EmbeddingGenerator

# Update ImageDType to use float64 instead of float_
ImageDType = Union[np.uint8, np.int64, np.float64]

class VectorStore:
    """Manages vector database operations using ChromaDB."""
    
    def __init__(self):
        self.db_path = Path("data/vector_db")
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.emb_dim = 1536  # text-embedding-3-small dimension
        self.embedding_generator = EmbeddingGenerator()
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                allow_reset=True,
                anonymized_telemetry=False
            )
        )
        
        # Reset existing collection if dimensions don't match
        try:
            self.collection = self.client.get_collection(name="building_code")
            # If collection exists but dimensions don't match, reset it
            if self.collection.metadata.get("dimension") != self.emb_dim:
                self.client.delete_collection("building_code")
                self.collection = self._create_collection()
        except:
            # Collection doesn't exist, create new one
            self.collection = self._create_collection()

    def _create_collection(self):
        """Creates a new collection with correct embedding dimensions."""
        return self.client.create_collection(
            name="building_code",
            metadata={
                "description": "Ontario Building Code content",
                "dimension": self.emb_dim  # text-embedding-3-small dimension
            }
        )
    
    def add_chunks(self, chunks: List[Tuple[str, int]], embeddings: List[List[float]]) -> None:
        """
        Adds text chunks and their embeddings to the database.
        
        Parameters
        ----------
        chunks : List[Tuple[str, int]]
            List of (text_chunk, token_count) tuples
        embeddings : List[List[float]]
            List of embedding vectors for each chunk
        """
        documents = [chunk[0] for chunk in chunks]
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"tokens": chunk[1]} for chunk in chunks]
        
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
    
    def query(self, query_texts: List[str], n_results: int = 3) -> Dict[str, Any]:
        """
        Query the collection using the same embedding model as used for storage.
        
        Parameters
        ----------
        query_texts : List[str]
            List of query texts to search for
        n_results : int, default=3
            Number of results to return per query
            
        Returns
        -------
        Dict[str, Any]
            Query results from ChromaDB
        """
        # Generate embeddings using the same model as storage
        query_embeddings = self.embedding_generator.generate_embeddings(query_texts)
        
        # Query the collection with the generated embeddings
        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )
