"""
Token counting utilities for text processing.

This module provides functions for counting and chunking text based on tokens
using the tiktoken library.
"""
from typing import List, Tuple
import tiktoken
from tqdm import tqdm

def get_token_encoder(model: str = "gpt-4") -> tiktoken.Encoding:
    """
    Get the token encoder for a specific model.
    
    Parameters
    ----------
    model : str, default="gpt-4"
        The model to get the encoder for
        
    Returns
    -------
    tiktoken.Encoding
        The encoder for the specified model
    """
    return tiktoken.encoding_for_model(model)

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count the number of tokens in a text string.
    
    Parameters
    ----------
    text : str
        The text to count tokens for
    model : str, default="gpt-4"
        The model to use for token counting
        
    Returns
    -------
    int
        The number of tokens in the text
    """
    encoding = get_token_encoder(model)
    return len(encoding.encode(text))

def chunk_text(text: str, max_tokens: int = 8000, overlap_tokens: int = 200, 
               model: str = "gpt-4o-mini") -> List[Tuple[str, int]]:
    """
    Chunks text into smaller segments based on token count with overlap.
    
    Parameters
    ----------
    text : str
        Input text to chunk
    max_tokens : int, default=8000
        Maximum number of tokens per chunk
    overlap_tokens : int, default=200
        Number of tokens to overlap between chunks
    model : str, default="gpt-4o-mini"
        The model to use for token counting
        
    Returns
    -------
    List[Tuple[str, int]]
        List of (chunk_text, token_count) tuples
    """
    chunks = []
    encoding = get_token_encoder(model)
    tokens = encoding.encode(text)
    
    # Safety check for overlap
    if overlap_tokens >= max_tokens:
        overlap_tokens = max_tokens // 4  # Set to 25% of max_tokens if overlap is too large
    
    # Calculate number of chunks needed
    n_tokens = len(tokens)
    step_size = max_tokens - overlap_tokens
    n_chunks = (n_tokens + step_size - 1) // step_size
    
    with tqdm(total=n_chunks, desc="Creating text chunks") as pbar:
        for i in range(n_chunks):
            start_idx = i * step_size
            end_idx = min(start_idx + max_tokens, n_tokens)
            
            chunk_tokens = tokens[start_idx:end_idx]
            chunk = encoding.decode(chunk_tokens)
            token_count = len(chunk_tokens)
            
            chunks.append((chunk, token_count))
            pbar.update(1)
            
            # Break if we've processed all tokens
            if end_idx >= n_tokens:
                break
    
    return chunks
