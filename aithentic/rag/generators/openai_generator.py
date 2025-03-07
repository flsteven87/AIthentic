from typing import List
import openai

from ..generators.base_generator import BaseGenerator
from ..models import Chunk

class OpenAIGenerator(BaseGenerator):
    """Generate answers using OpenAI API."""
    
    def __init__(
        self, 
        api_key: str = None, 
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        """
        Initialize the generator.
        
        Args:
            api_key: OpenAI API key (if None, will use environment variable)
            model: OpenAI model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in the response
        """
        if api_key:
            openai.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate(self, query: str, documents: List[Chunk]) -> str:
        """
        Generate an answer based on the query and retrieved documents.
        
        Args:
            query: Query text
            documents: Retrieved relevant documents
            
        Returns:
            Generated answer
        """
        # Prepare context from documents
        context = "\n\n".join([f"Document {i+1}:\n{doc.text}" for i, doc in enumerate(documents)])
        
        # Create prompt
        prompt = f"""Answer the question based on the following context:

Context:
{context}

Question: {query}

Answer:"""
        
        # Generate response
        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content 