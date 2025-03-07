from abc import ABC, abstractmethod
from typing import List
import numpy as np

class BaseEmbedder(ABC):
    """Base class for text embedders."""
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[np.ndarray]:
        """
        Create embeddings for multiple texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embeddings (vectors)
        """
        pass
    
    @abstractmethod
    def embed_query(self, text: str) -> np.ndarray:
        """
        Create embedding for a query text.
        
        Args:
            text: Query text
            
        Returns:
            Embedding vector
        """
        pass 