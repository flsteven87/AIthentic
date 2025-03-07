import os
from typing import List

from ..document_loaders.base_loader import BaseDocumentLoader
from ..models import Document

class TextLoader(BaseDocumentLoader):
    """Loader for plain text files."""
    
    def load(self, source: str) -> List[Document]:
        """
        Load text from a file.
        
        Args:
            source: Path to the text file
            
        Returns:
            List containing a single Document
        """
        if not os.path.exists(source):
            raise FileNotFoundError(f"File not found: {source}")
        
        with open(source, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = {
            "source": source,
            "file_type": "text",
            "file_name": os.path.basename(source)
        }
        
        return [Document(content=content, metadata=metadata)] 