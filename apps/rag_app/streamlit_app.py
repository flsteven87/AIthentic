import os
import sys
import tempfile
import streamlit as st

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

# 設置頁面配置
st.set_page_config(page_title="AIthentic RAG", layout="wide")

# 初始化會話狀態
if 'rag_pipeline' not in st.session_state:
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
    st.session_state.rag_pipeline = RAGPipeline(
        document_loader=document_loader,
        text_splitter=text_splitter,
        embedder=embedder,
        vector_store=vector_store,
        retriever=retriever,
        generator=generator
    )
    
    st.session_state.documents_ingested = False
    st.session_state.chat_history = []

# 標題
st.title("AIthentic RAG 系統")

# 側邊欄 - 文檔上傳
with st.sidebar:
    st.header("文檔上傳")
    uploaded_file = st.file_uploader("上傳文本文檔", type=["txt"])
    
    if uploaded_file is not None:
        # 創建臨時文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        if st.button("處理文檔"):
            with st.spinner("處理文檔中..."):
                num_chunks = st.session_state.rag_pipeline.ingest(tmp_path)
                st.session_state.documents_ingested = True
                st.success(f"文檔已處理為 {num_chunks} 個塊")
            
            # 刪除臨時文件
            os.unlink(tmp_path)
    
    # 配置選項
    st.header("配置")
    chunk_size = st.slider("塊大小", 100, 2000, 1000, 100)
    chunk_overlap = st.slider("塊重疊", 0, 500, 200, 50)
    top_k = st.slider("結果數量", 1, 10, 5, 1)
    
    # 更新配置
    if st.button("更新配置"):
        st.session_state.rag_pipeline.text_splitter.chunk_size = chunk_size
        st.session_state.rag_pipeline.text_splitter.chunk_overlap = chunk_overlap
        st.session_state.rag_pipeline.retriever.top_k = top_k
        st.success("配置已更新")

# 主界面 - 聊天
st.header("與您的文檔對話")

# 顯示聊天歷史
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # 如果是助手回答，顯示來源
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("查看來源"):
                for i, source in enumerate(message["sources"]):
                    st.markdown(f"**來源 {i+1}:**")
                    st.markdown(f"*來自: {source.metadata.get('source', '未知')}*")
                    st.markdown(f"*塊 {source.metadata.get('chunk_index', '未知')} / {source.metadata.get('total_chunks', '未知')}*")
                    st.text(source.text)
                    st.markdown("---")

# 查詢輸入
query = st.chat_input("詢問關於您文檔的問題")

if query:
    # 添加用戶消息到歷史
    st.session_state.chat_history.append({"role": "user", "content": query})
    
    # 顯示用戶消息
    with st.chat_message("user"):
        st.write(query)
    
    # 檢查是否已導入文檔
    if not st.session_state.documents_ingested:
        with st.chat_message("assistant"):
            st.write("請先上傳並處理文檔。")
        st.session_state.chat_history.append({"role": "assistant", "content": "請先上傳並處理文檔。"})
    else:
        # 處理查詢
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                result = st.session_state.rag_pipeline.query(query)
                st.write(result["answer"])
                
                # 顯示來源
                with st.expander("查看來源"):
                    for i, source in enumerate(result["sources"]):
                        st.markdown(f"**來源 {i+1}:**")
                        st.markdown(f"*來自: {source.metadata.get('source', '未知')}*")
                        st.markdown(f"*塊 {source.metadata.get('chunk_index', '未知')} / {source.metadata.get('total_chunks', '未知')}*")
                        st.text(source.text)
                        st.markdown("---")
        
        # 添加助手消息到歷史
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": result["answer"],
            "sources": result["sources"]
        })

# 添加頁腳
st.markdown("---")
st.markdown("AIthentic RAG 系統 - 由 OpenAI 和 Streamlit 提供支持")
