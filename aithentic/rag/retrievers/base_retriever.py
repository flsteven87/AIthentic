from abc import ABC, abstractmethod
from typing import List
import numpy as np

from ..models import Chunk
from ..vector_stores.base_store import BaseVectorStore

class BaseRetriever(ABC):
    """Base class for retrievers."""
    
    @abstractmethod
    def retrieve(
        self, 
        query_embedding: np.ndarray, 
        query_text: str, 
        vector_store: BaseVectorStore,
        top_k: int = 5
    ) -> List[Chunk]:
        """
        Retrieve relevant documents.
        
        Args:
            query_embedding: Query embedding vector
            query_text: Original query text
            vector_store: Vector store to search in
            top_k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        pass 