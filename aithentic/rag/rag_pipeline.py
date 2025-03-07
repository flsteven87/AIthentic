from typing import Dict, List, Any

class RAGPipeline:
    """
    RAG Pipeline orchestrates the entire RAG process from document loading to answer generation.
    """
    
    def __init__(
        self,
        document_loader,
        text_splitter,
        embedder,
        vector_store,
        retriever,
        generator
    ):
        """
        Initialize the RAG pipeline with all necessary components.
        
        Args:
            document_loader: Component to load documents
            text_splitter: Component to split documents into chunks
            embedder: Component to create embeddings
            vector_store: Component to store and index embeddings
            retriever: Component to retrieve relevant documents
            generator: Component to generate answers
        """
        self.document_loader = document_loader
        self.text_splitter = text_splitter
        self.embedder = embedder
        self.vector_store = vector_store
        self.retriever = retriever
        self.generator = generator
        
    def ingest(self, source) -> int:
        """
        Ingest documents from the source, process them, and store in the vector store.
        
        Args:
            source: Source of the documents (file path, URL, etc.)
            
        Returns:
            Number of documents processed
        """
        # Load documents
        documents = self.document_loader.load(source)
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Create embeddings
        embeddings = self.embedder.embed_documents([chunk.text for chunk in chunks])
        
        # Store embeddings in vector store
        self.vector_store.add_embeddings(
            embeddings=embeddings,
            documents=chunks
        )
        
        return len(chunks)
    
    def query(self, query_text: str) -> Dict[str, Any]:
        """
        Process a query and generate an answer.
        
        Args:
            query_text: The query text
            
        Returns:
            Generated answer and supporting documents
        """
        # Embed the query
        query_embedding = self.embedder.embed_query(query_text)
        
        # Retrieve relevant documents
        relevant_docs = self.retriever.retrieve(
            query_embedding=query_embedding,
            query_text=query_text,
            vector_store=self.vector_store
        )
        
        # Generate answer
        answer = self.generator.generate(
            query=query_text,
            documents=relevant_docs
        )
        
        return {
            "answer": answer,
            "sources": relevant_docs
        }
