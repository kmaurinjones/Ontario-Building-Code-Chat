"""
Query expansion using GPT-4o-mini for improved vector search.
"""
from openai import OpenAI
from typing import List
import json

class QueryExpander:
    """Expands user queries into multiple optimized search queries."""
    
    def __init__(self):
        """Initialize the OpenAI client."""
        self.client = OpenAI()
        self.model = "gpt-4o-mini"
    
    def generate(self, query: str, n_queries: int = 5) -> List[str]:
        """
        Generate optimized search queries from user input.
        
        Parameters
        ----------
        query : str
            Original user query
        n_queries : int, default=5
            Number of queries to generate
            
        Returns
        -------
        List[str]
            List of generated search queries
        """
        system_prompt = f"""You are an expert at reformulating questions about building codes into 
optimal search queries. Generate queries that would work well with 
embedding-based similarity search. Focus on key terms and concepts. 
Generate exactly {n_queries} queries.

Format your response as a JSON list of strings. Example:
["query 1", "query 2", "query 3"]

Make queries concise and focused on different aspects of the question, as well as potentially reasonably related to the original query.

You always aim to retrieve sections, subsections, tables, or any other relevant information that can be used as a citation from the building code, in addition to the original query.

You format everything as strict JSON, without including any other text or characters. No backticks, no code blocks, no markdown.
""".strip()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.7
            )
            
            # Parse the JSON response
            queries = json.loads(response.choices[0].message.content)
            
            # Ensure we have exactly n_queries
            if len(queries) != n_queries:
                raise ValueError(f"Expected {n_queries} queries, got {len(queries)}")
                
            return queries
            
        except Exception as e:
            print(f"Error generating queries: {str(e)}")
            # Return a list with just the original query if generation fails
            return [query]
