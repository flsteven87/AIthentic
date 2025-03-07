from typing import List
import numpy as np
import openai

from ..embeddings.base_embedder import BaseEmbedder

class OpenAIEmbedder(BaseEmbedder):
    """Create embeddings using OpenAI API."""
    
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        """
        Initialize the embedder.
        
        Args:
            api_key: OpenAI API key (if None, will use environment variable)
            model: OpenAI embedding model to use
        """
        if api_key:
            openai.api_key = api_key
        self.model = model
    
    def embed_documents(self, texts: List[str]) -> List[np.ndarray]:
        """
        Create embeddings for multiple texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        # Process in batches to avoid API limits
        batch_size = 100
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = openai.embeddings.create(
                model=self.model,
                input=batch
            )
            batch_embeddings = [np.array(item.embedding) for item in response.data]
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def embed_query(self, text: str) -> np.ndarray:
        """
        Create embedding for a query text.
        
        Args:
            text: Query text
            
        Returns:
            Embedding vector
        """
        response = openai.embeddings.create(
            model=self.model,
            input=[text]
        )
        return np.array(response.data[0].embedding) 