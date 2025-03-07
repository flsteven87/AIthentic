from abc import ABC, abstractmethod
from typing import List

from ..models import Document, Chunk

class BaseTextSplitter(ABC):
    """Base class for text splitters."""
    
    @abstractmethod
    def split_documents(self, documents: List[Document]) -> List[Chunk]:
        """
        Split documents into chunks.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of Chunk objects
        """
        pass 