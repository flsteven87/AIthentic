from typing import List

from ..text_splitters.base_splitter import BaseTextSplitter
from ..models import Document, Chunk

class CharacterTextSplitter(BaseTextSplitter):
    """Split text based on character count."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the splitter.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_documents(self, documents: List[Document]) -> List[Chunk]:
        """
        Split documents into chunks.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of Chunk objects
        """
        chunks = []
        
        for doc in documents:
            text = doc.content
            doc_chunks = self._split_text(text)
            
            for i, chunk_text in enumerate(doc_chunks):
                chunk_metadata = doc.metadata.copy()
                chunk_metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(doc_chunks)
                })
                
                chunks.append(Chunk(
                    text=chunk_text,
                    metadata=chunk_metadata,
                    doc_id=doc.doc_id
                ))
        
        return chunks
    
    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If we're not at the end of the text, try to break at a space
            if end < len(text):
                # Find the last space within the chunk
                last_space = text.rfind(' ', start, end)
                if last_space != -1:
                    end = last_space
            
            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap
        
        return chunks 