from abc import ABC, abstractmethod
from typing import List

from ..models import Document

class BaseDocumentLoader(ABC):
    """Base class for document loaders."""
    
    @abstractmethod
    def load(self, source):
        """
        Load documents from the source.
        
        Args:
            source: Source of the documents
            
        Returns:
            List of Document objects
        """
        pass 