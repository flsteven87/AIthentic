# AIthentic

AIthentic is an AI exploration and application development platform that integrates various AI models and tools for building practical AI applications.

## Project Overview

This project aims to explore and implement various AI capabilities, including but not limited to:

- Natural Language Processing and Conversational Systems
- Browser Automation and Web Content Analysis
- Text Summarization and Content Generation
- Video Transcription and Summarization
- Multimodal Content Processing
- AI Agents and Tool Integration
- Retrieval-Augmented Generation (RAG) Systems

## Project Structure

```
AIthentic/
├── aithentic/             # Core functionality modules
│   ├── agents/            # AI agent implementations
│   ├── llm/               # Language model wrappers
│   ├── rag/               # Retrieval-Augmented Generation components
│   │   ├── document_loaders/  # Document loading utilities
│   │   ├── text_splitters/    # Text chunking strategies
│   │   ├── embeddings/        # Embedding models
│   │   ├── vector_stores/     # Vector storage implementations
│   │   ├── retrievers/        # Document retrieval components
│   │   └── generators/        # Answer generation components
│   ├── tools/             # AI tools collection
│   └── utils/             # Utility functions
│
├── apps/                  # Applications directory
│   ├── youtube_summary/   # YouTube video summarization app
│   ├── web_explorer/      # Web browsing and summarization app
│   └── rag_app/           # RAG-based document Q&A application
│
├── data/                  # Data directory
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── tests/                 # Test directory
```

## Getting Started

### Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/AIthentic.git
   cd AIthentic
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Alternatively, if you use Poetry:
   ```bash
   poetry install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit the .env file to set necessary API keys
   ```

### Running Applications

- Run the YouTube video summarization app:
  ```bash
  streamlit run apps/youtube_summary/app.py
  ```

- Run the web browser application:
  ```bash
  python apps/web_explorer/app.py
  ```

- Run the RAG document Q&A application:
  ```bash
  streamlit run apps/rag_app/streamlit_app.py
  ```

## Core Modules

### Agents
Intelligent agents designed to perform complex tasks such as web browsing, content analysis, and task automation.

### LLM
Language model wrappers supporting various models including OpenAI and Ollama models.

### RAG (Retrieval-Augmented Generation)
A modular system for building document-based question answering applications:
- **Document Loaders**: Components for loading documents from various sources
- **Text Splitters**: Strategies for chunking documents into manageable pieces
- **Embeddings**: Models for converting text into vector representations
- **Vector Stores**: Storage solutions for document embeddings
- **Retrievers**: Components for retrieving relevant documents based on queries
- **Generators**: Models for generating answers based on retrieved documents

### Tools
Various AI tools including summarization generators, speech-to-text converters, and content analyzers.

### Utils
General utility functions for file handling, logging, and other common operations.

## Applications

### YouTube Summary
An application that downloads YouTube videos, transcribes their content, and generates concise summaries.

### Web Explorer
A browser-based application for navigating websites, extracting content, and generating insights from web pages.

### RAG Document Q&A
An interactive application that allows users to upload documents, process them using RAG techniques, and ask questions about their content. The application retrieves relevant information from the documents and generates accurate answers.

## Technical Requirements

- Python 3.9 or higher
- Dependencies listed in requirements.txt or pyproject.toml
- API keys for various services (OpenAI, etc.)
- FFmpeg for media processing
