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

## Project Structure

```
AIthentic/
├── aithentic/             # Core functionality modules
│   ├── agents/            # AI agent implementations
│   ├── llm/               # Language model wrappers
│   ├── tools/             # AI tools collection
│   └── utils/             # Utility functions
│
├── apps/                  # Applications directory
│   ├── youtube_summary/   # YouTube video summarization app
│   └── web_explorer/      # Web browsing and summarization app
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

## Core Modules

### Agents
Intelligent agents designed to perform complex tasks such as web browsing, content analysis, and task automation.

### LLM
Language model wrappers supporting various models including OpenAI and Ollama models.

### Tools
Various AI tools including summarization generators, speech-to-text converters, and content analyzers.

### Utils
General utility functions for file handling, logging, and other common operations.

## Applications

### YouTube Summary
An application that downloads YouTube videos, transcribes their content, and generates concise summaries.

### Web Explorer
A browser-based application for navigating websites, extracting content, and generating insights from web pages.

## Technical Requirements

- Python 3.9 or higher
- Dependencies listed in requirements.txt or pyproject.toml
- API keys for various services (OpenAI, etc.)
- FFmpeg for media processing
