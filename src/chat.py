"""
Chat functionality using OpenAI's API.
"""
from openai import OpenAI
from typing import Generator, List, Dict, Optional, Tuple, Union
import os
from .scraper import WebScraper
from .database import VectorStore
from .embeddings import EmbeddingGenerator
from .utils.token_counter import count_tokens

class ChatBot:
    """Manages chat interactions using OpenAI's API."""
    
    def __init__(self, vector_store: VectorStore = None):
        """
        Initialize chat components and ensure content is up to date.
        
        Parameters
        ----------
        vector_store : VectorStore, optional
            Existing VectorStore instance to use. If None, creates a new one.
        """
        # Initialize OpenAI client with the current API key (which may have been updated during auth)
        self.client = OpenAI()
        self.model = "gpt-4o-mini"
        
        # Initialize components
        self.scraper = WebScraper("https://www.ontario.ca/laws/regulation/120332/v25")
        self.vector_store = vector_store if vector_store else VectorStore()
        self.embedding_generator = EmbeddingGenerator()
        
        # Temporary storage for latest interaction
        self.last_user_query: Optional[str] = None
        self.last_model_response: Optional[str] = None
        
        # Get content and update vector store if needed
        content = self.scraper.get_content()
        if not self.vector_store.collection.count():
            chunks = self.scraper.process_content(content)
            embeddings = self.embedding_generator.generate_embeddings([chunk[0] for chunk in chunks])
            self.vector_store.add_chunks(chunks, embeddings)
        
    def generate_system_prompt(self, context: str) -> str:
        """
        Generates the system prompt with context.
        
        Parameters
        ----------
        context : str
            Relevant context from the Building Code
            
        Returns
        -------
        str
            Formatted system prompt
        """
        return f"""You are an expert assistant for the Ontario Building Code. 
            Use the following context to answer questions about the building code. 
            If you're not sure about something, say so.

            The user is likely inquiring about something in the building code.
            You need to first determine if the user is asking anything about the building code. If they are, you need to find the best answer to their question possible and always site relevant sections, subsections, or subsections as much as you can so that they can navigate back to and check your response on the website.
            If you do have any relevant sections or subsections or tables or any kind of reference citation that you refer to in your response you must bold it using markdown bolding. Example: **Section 1.2.3**
            You ALWAYS provided citations for any information you provide. This is critical. You also ALWAYS provided a small sample of exact text, sections to look within, or tables to look within for the user to verify your response on the website.

            --------------------------------
            <|context|>
            {context}
            <|/context|>
            """.replace("    ", " ").strip()
    
    def process_message(self, user_query: str, messages: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], str]:
        """
        Process a user message with RAG and prepare for chat completion.
        
        Parameters
        ----------
        user_query : str
            The original user query
        messages : List[Dict[str, str]]
            Current message history
            
        Returns
        -------
        Tuple[List[Dict[str, str]], str]
            Processed messages with RAG context and the original query
        """
        # Store original query
        self.last_user_query = user_query
        
        # Get relevant context through RAG
        # Note: Implement your query expansion and RAG logic here
        # This is a placeholder for where you'd integrate your existing RAG implementation
        context = "Relevant building code context would be retrieved here"
        
        # Create messages with full context for model
        messages_with_context = messages.copy()
        messages_with_context[-1]['content'] = f"{user_query}\n\nRelevant Building Code Context:\n{context}"
        
        return messages_with_context, user_query
    
    def update_chat_history(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Update chat history to use minimal context.
        
        Parameters
        ----------
        messages : List[Dict[str, str]]
            Current message history
            
        Returns
        -------
        List[Dict[str, str]]
            Updated message history with minimal context
        """
        if self.last_user_query and self.last_model_response:
            # Replace the last user message with just the query
            messages[-2]['content'] = self.last_user_query
            # Replace the last assistant message with the response
            messages[-1]['content'] = self.last_model_response
            
        return messages
    
    def chat_stream(self, messages: List[Dict[str, str]]) -> Generator:
        """
        Streams the chat response from the API.
        
        Parameters
        ----------
        messages : List[Dict[str, str]]
            List of message dictionaries with 'role' and 'content'
            
        Yields
        ------
        Union[str, Dict[str, int]]
            Either:
            - Chunks of the response text
            - Final dictionary with token usage statistics (as last yield)
        """
        try:
            # Process the last user message with RAG
            if messages[-1]['role'] == 'user':
                messages, original_query = self.process_message(messages[-1]['content'], messages)
            
            # First, get token count for the input
            input_tokens = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                max_tokens=1  # Minimal completion to just get input token count
            )
            prompt_tokens = input_tokens.usage.prompt_tokens
            
            # Now stream the actual response
            response_stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=0
            )
            
            # Collect full response while streaming
            full_response = ""
            for chunk in response_stream:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content is not None:
                    full_response += delta.content
                    yield delta.content
            
            # Store the complete model response
            self.last_model_response = full_response
            
            # Get a non-streaming version of the same response to get accurate token counts
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                temperature=0
            )
            
            # Yield the token usage as the final item
            token_usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": final_response.usage.completion_tokens,
                "total_tokens": prompt_tokens + final_response.usage.completion_tokens
            }
            yield token_usage
            
            # Update chat history to use minimal context
            messages = self.update_chat_history(messages)
                    
        except Exception as e:
            yield f"Error: {str(e)}"
            yield {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
