from abc import ABC, abstractmethod
from typing import List

from ..models import Chunk

class BaseGenerator(ABC):
    """Base class for answer generators."""
    
    @abstractmethod
    def generate(self, query: str, documents: List[Chunk]) -> str:
        """
        Generate an answer based on the query and retrieved documents.
        
        Args:
            query: Query text
            documents: Retrieved relevant documents
            
        Returns:
            Generated answer
        """
        pass 