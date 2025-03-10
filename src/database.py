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
        print("\n[VectorStore] Initializing...")
        self.db_path = Path("data/vector_db")
        self.db_path.mkdir(parents=True, exist_ok=True)
        print(f"[VectorStore] Using database path: {self.db_path}")

        self.emb_dim = 1536  # text-embedding-3-small dimension
        self.embedding_generator = EmbeddingGenerator()
        
        # Initialize ChromaDB with persistence
        print("[VectorStore] Initializing ChromaDB client...")
        self.client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(self.db_path),
                anonymized_telemetry=False
            )
        )
        print("[VectorStore] ChromaDB client initialized with persistence")
        
        # Reset existing collection if dimensions don't match
        try:
            self.collection = self.client.get_collection(name="building_code")
            print(f"[VectorStore] Found existing collection with {self.collection.count()} documents")
            # If collection exists but dimensions don't match, reset it
            if self.collection.metadata.get("dimension") != self.emb_dim:
                print("[VectorStore] Embedding dimensions don't match, resetting collection")
                self.client.delete_collection("building_code")
                self.collection = self._create_collection()
        except:
            # Collection doesn't exist, create new one
            print("[VectorStore] No existing collection found, creating new one")
            self.collection = self._create_collection()
        
        print("[VectorStore] Initialization complete")

    def _create_collection(self):
        """Creates a new collection with correct embedding dimensions."""
        collection = self.client.create_collection(
            name="building_code",
            metadata={
                "description": "Ontario Building Code content",
                "dimension": self.emb_dim  # text-embedding-3-small dimension
            }
        )
        print("[VectorStore] Created new collection")
        return collection
    
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
        print(f"\n[VectorStore] Adding {len(chunks)} chunks to database")
        documents = [chunk[0] for chunk in chunks]
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"tokens": chunk[1]} for chunk in chunks]
        
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        
        # For ChromaDB 0.3.29, persist after adding chunks
        print("[VectorStore] Persisting changes to disk...")
        self.client.persist()
        print(f"[VectorStore] Added and persisted {len(chunks)} chunks")
        print(f"[VectorStore] Total documents in collection: {self.collection.count()}")
    
    def query(self, query_texts: List[str], n_results: int = 5) -> Dict[str, Any]:
        """
        Query the collection using the same embedding model as used for storage.
        
        Parameters
        ----------
        query_texts : List[str]
            List of query texts to search for
        n_results : int, default=5
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
