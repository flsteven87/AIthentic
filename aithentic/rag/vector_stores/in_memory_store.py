from typing import List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ..vector_stores.base_store import BaseVectorStore
from ..models import Chunk

class InMemoryVectorStore(BaseVectorStore):
    """Simple in-memory vector store."""
    
    def __init__(self):
        """Initialize an empty store."""
        self.embeddings = []
        self.documents = []
    
    def add_embeddings(self, embeddings: List[np.ndarray], documents: List[Chunk]):
        """
        Add embeddings and their corresponding documents to the store.
        
        Args:
            embeddings: List of embedding vectors
            documents: List of document chunks
        """
        if len(embeddings) != len(documents):
            raise ValueError("Number of embeddings must match number of documents")
        
        self.embeddings.extend(embeddings)
        self.documents.extend(documents)
    
    def similarity_search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[Chunk, float]]:
        """
        Search for similar documents based on embedding.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        if not self.embeddings:
            return []
        
        # Convert list of embeddings to a 2D array
        embeddings_array = np.vstack(self.embeddings)
        
        # Calculate cosine similarity
        similarities = cosine_similarity([query_embedding], embeddings_array)[0]
        
        # Get indices of top_k most similar documents
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return documents and their similarity scores
        results = [(self.documents[i], similarities[i]) for i in top_indices]
        
        return results 