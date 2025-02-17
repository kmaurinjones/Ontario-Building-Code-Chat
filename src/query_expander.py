"""
Query expansion using GPT-4o-mini for improved vector search.
"""
from openai import OpenAI
from typing import List, Dict
import json

class QueryExpander:
    """Expands user queries into multiple optimized search queries."""
    
    def __init__(self):
        """Initialize the OpenAI client."""
        self.client = OpenAI()
        self.model = "gpt-4o-mini"
    
    def generate(self, query: str, conversation_history: List[Dict[str, str]] = None, n_queries: int = 9) -> tuple[List[str], Dict[str, int]]:
        """
        Generate optimized search queries from user input.
        
        Parameters
        ----------
        query : str
            Original user query
        conversation_history : List[Dict[str, str]], optional
            List of previous messages in the conversation, each with 'role' and 'content'
        n_queries : int, default=9
            Number of queries to generate
            
        Returns
        -------
        tuple[List[str], Dict[str, int]]
            Tuple containing:
            - List of generated search queries
            - Dictionary with token usage statistics
        """
        # Format conversation history if provided
        formatted_history = ""
        if conversation_history:
            history_messages = [
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in conversation_history
            ]
            formatted_history = "\n".join(history_messages)

        system_prompt = f"""You are an expert at reformulating questions about building codes into 
optimal search queries. Generate queries that would work well with 
embedding-based similarity search. Focus on key terms and concepts. 
Generate exactly {n_queries} queries.

Format your response as a JSON list of strings. Example:
["query 1", "query 2", "query 3"]

Make queries concise and focused on different aspects of the question.
Your queries should be novel and avoid repeating topics already covered in the conversation history.
Focus primarily on the current query while being aware of the context from previous messages.

You always aim to retrieve sections, subsections, tables, or any other relevant information that can be used as a citation from the building code.

You format everything as strict JSON, without including any other text or characters. No backticks, no code blocks, no markdown.

CONVERSATION HISTORY (For Context):
{formatted_history}

CURRENT QUERY (Primary Focus):
{query}
""".strip()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt}
                ],
                temperature=1 # high randomness to generate more diverse queries
            )
            
            # Parse the JSON response
            queries = json.loads(response.choices[0].message.content)
            
            # Ensure we have exactly n_queries
            if len(queries) != n_queries:
                raise ValueError(f"Expected {n_queries} queries, got {len(queries)}")
            
            # Get token usage from response
            token_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
                
            return queries, token_usage
            
        except Exception as e:
            print(f"Error generating queries: {str(e)}")
            # Return a list with just the original query and empty token usage if generation fails
            return [query], {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
