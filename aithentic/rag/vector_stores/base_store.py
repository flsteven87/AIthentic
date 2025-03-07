from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np

from ..models import Chunk

class BaseVectorStore(ABC):
    """Base class for vector stores."""
    
    @abstractmethod
    def add_embeddings(self, embeddings: List[np.ndarray], documents: List[Chunk]):
        """
        Add embeddings and their corresponding documents to the store.
        
        Args:
            embeddings: List of embedding vectors
            documents: List of document chunks
        """
        pass
    
    @abstractmethod
    def similarity_search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[Chunk, float]]:
        """
        Search for similar documents based on embedding.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        pass 