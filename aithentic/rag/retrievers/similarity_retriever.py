from typing import List
import numpy as np

from ..retrievers.base_retriever import BaseRetriever
from ..vector_stores.base_store import BaseVectorStore
from ..models import Chunk

class SimilarityRetriever(BaseRetriever):
    """Retrieve documents based on embedding similarity."""
    
    def __init__(self, top_k: int = 5):
        """
        Initialize the retriever.
        
        Args:
            top_k: Number of documents to retrieve
        """
        self.top_k = top_k
    
    def retrieve(
        self, 
        query_embedding: np.ndarray, 
        query_text: str, 
        vector_store: BaseVectorStore,
        top_k: int = None
    ) -> List[Chunk]:
        """
        Retrieve relevant documents.
        
        Args:
            query_embedding: Query embedding vector
            query_text: Original query text (not used in this retriever)
            vector_store: Vector store to search in
            top_k: Number of results to return (overrides init value if provided)
            
        Returns:
            List of relevant documents
        """
        k = top_k if top_k is not None else self.top_k
        results = vector_store.similarity_search(query_embedding, k)
        
        # Return just the documents, not the scores
        return [doc for doc, _ in results] 