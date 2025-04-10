# AIthentic Project Planning

## 專案目標
建立一個基於 agno 框架的 LLM Agent 系統，結合 Open Web UI 作為使用者介面，用於展示和測試各種 Agent 工作流程的概念驗證（POC）。

## 技術棧
- **Backend Framework**: 
  - agno (LLM Agent Framework)
  - FastAPI (REST API)
  - SQLModel (ORM)
  - Pydantic (資料驗證)

- **Frontend**:
  - Open Web UI

- **資料庫與後端服務**:
  - Supabase
    - PostgreSQL 資料庫
    - 即時訂閱
    - 身份驗證
    - Row Level Security (RLS)
    - 儲存空間

## 系統架構

### 後端架構
```
backend/
├── app/
│   ├── agents/             # Agent 定義和實現
│   │   ├── base.py        # 基礎 Agent 類別
│   │   └── workflows/     # 不同工作流程的 Agent
│   ├── api/               # API 路由
│   │   ├── v1/           # API v1 端點
│   │   └── deps.py       # 依賴注入
│   ├── core/             # 核心功能
│   │   ├── config.py     # 配置
│   │   └── security.py   # 安全相關
│   ├── db/               # 資料庫
│   │   ├── models.py     # SQLModel 模型
│   │   ├── session.py    # Supabase 連接管理
│   │   └── migrations/   # 資料庫遷移腳本
│   ├── schemas/          # Pydantic 模型
│   └── services/         # 業務邏輯
└── tests/                # 測試目錄
```

### 前端架構 (Open Web UI 整合)
```
frontend/
├── components/          # 自定義元件
├── pages/              # 頁面
└── services/           # API 服務
```

## 開發規範

### 程式碼風格
- 遵循 PEP 8 規範
- 使用 Black 進行程式碼格式化
- 所有函數都需要型別提示和 Google 風格的文檔字串
- 最大行長度：88 字元（Black 預設）

### 虛擬環境設定
- 使用 Conda 管理虛擬環境
- 環境名稱：AIthentic
- Python 版本：3.12
- 啟動命令：
  ```bash
  conda activate AIthentic
  ```
- 所有套件安裝都必須在虛擬環境中進行
- 定期更新 requirements.txt 以記錄依賴

### Git 工作流程
- 主分支：main
- 功能分支：feature/*
- 修復分支：bugfix/*
- 發布分支：release/*

### 測試規範
- 使用 Pytest 進行單元測試
- 每個新功能至少包含：
  - 基本功能測試
  - 邊界條件測試
  - 錯誤處理測試
- 目標測試覆蓋率：80%

## Agent 工作流程設計
- 每個工作流程都應該是獨立的模組
- 工作流程需要包含：
  - 明確的輸入/輸出定義
  - 錯誤處理機制
  - 中間狀態保存
  - 可視化界面配置

## 安全考量
- 使用環境變數管理敏感資訊
- 使用 Supabase 提供的身份驗證機制
- 實作 Row Level Security (RLS) 策略
- 記錄所有 Agent 操作日誌
- 實作速率限制

## 監控和日誌
- 使用結構化日誌格式
- 記錄 Agent 執行時間和資源使用
- 追蹤 API 端點性能
- 監控資料庫查詢性能

## 擴展性考量
- 模組化 Agent 設計
- 可插拔的工作流程系統
- 彈性的配置系統 