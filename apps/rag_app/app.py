import argparse
import os
import sys

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from aithentic.config import OPENAI_API_KEY
from aithentic.rag.document_loaders.text_loader import TextLoader
from aithentic.rag.text_splitters.character_splitter import CharacterTextSplitter
from aithentic.rag.embeddings.openai_embedder import OpenAIEmbedder
from aithentic.rag.vector_stores.in_memory_store import InMemoryVectorStore
from aithentic.rag.retrievers.similarity_retriever import SimilarityRetriever
from aithentic.rag.generators.openai_generator import OpenAIGenerator
from aithentic.rag.rag_pipeline import RAGPipeline

def main():
    parser = argparse.ArgumentParser(description="Simple RAG Application")
    parser.add_argument("--ingest", help="Path to document to ingest")
    parser.add_argument("--query", help="Query to process")
    args = parser.parse_args()
    
    # 初始化組件
    document_loader = TextLoader()
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    embedder = OpenAIEmbedder(
        api_key=OPENAI_API_KEY,
        model="text-embedding-3-small"
    )
    vector_store = InMemoryVectorStore()
    retriever = SimilarityRetriever(top_k=5)
    generator = OpenAIGenerator(
        api_key=OPENAI_API_KEY,
        model="gpt-4o"
    )
    
    # 創建 RAG 管道
    rag_pipeline = RAGPipeline(
        document_loader=document_loader,
        text_splitter=text_splitter,
        embedder=embedder,
        vector_store=vector_store,
        retriever=retriever,
        generator=generator
    )
    
    # 處理命令
    if args.ingest:
        print(f"Ingesting document: {args.ingest}")
        num_chunks = rag_pipeline.ingest(args.ingest)
        print(f"Processed {num_chunks} chunks")
    
    if args.query:
        if not vector_store.documents:
            print("Error: No documents ingested. Please ingest documents first.")
            return
        
        print(f"Query: {args.query}")
        result = rag_pipeline.query(args.query)
        
        print("\nAnswer:")
        print(result["answer"])
        
        print("\nSources:")
        for i, doc in enumerate(result["sources"]):
            print(f"Source {i+1}: {doc.metadata.get('source', 'Unknown')}")
            print(f"Chunk {doc.metadata.get('chunk_index', 'Unknown')} of {doc.metadata.get('total_chunks', 'Unknown')}")
            print(f"Text: {doc.text[:100]}...")
            print()

if __name__ == "__main__":
    main()
