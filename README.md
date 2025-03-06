# AIthentic

AIthentic是一個AI功能探索和應用開發平台，集成了多種AI模型和工具，用於構建各種實用的AI應用程式。

## 專案概述

本專案旨在探索和實現各種AI功能，包括但不限於：

- 自然語言處理與對話系統
- 瀏覽器自動化與網頁內容分析
- 文本摘要與內容生成
- 影片內容轉錄與摘要
- 多模態內容處理
- AI代理與工具集成

## 專案結構

```
AIthentic/
├── aithentic/             # 核心功能模組
│   ├── agents/            # AI代理實現
│   ├── llm/               # 語言模型封裝
│   ├── tools/             # AI工具集合
│   └── utils/             # 通用工具函數
│
├── apps/                  # 應用程式目錄
│   ├── youtube_summary/   # YouTube影片摘要應用
│   └── web_explorer/      # 網頁瀏覽和摘要應用
│
├── data/                  # 資料目錄
├── docs/                  # 文檔
├── scripts/               # 實用腳本
└── tests/                 # 測試目錄
```

## 快速開始

### 環境設置

1. 克隆存儲庫:
   ```bash
   git clone https://github.com/your-username/AIthentic.git
   cd AIthentic
   ```

2. 安裝依賴:
   ```bash
   pip install -r requirements.txt
   ```

3. 配置環境變數:
   ```bash
   cp .env.example .env
   # 編輯 .env 文件，設置必要的API密鑰
   ```

### 運行應用

- 運行YouTube影片摘要應用:
  ```bash
  streamlit run apps/youtube_summary/app.py
  ```

- 運行網頁瀏覽器應用:
  ```bash
  python apps/web_explorer/app.py
  ```

## 功能模組

- **Agents**: 智能代理用於執行複雜任務，如瀏覽網頁、分析內容等
- **LLM**: 語言模型包裝器，支持OpenAI、Ollama等模型
- **Tools**: 各種AI工具，如摘要生成器、語音轉文字等
- **Utils**: 通用工具函數，包括文件處理、日誌記錄等

## 貢獻

歡迎提交問題和建議，或直接提交Pull Request。
