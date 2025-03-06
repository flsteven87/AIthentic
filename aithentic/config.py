"""
配置管理模組，用於加載和訪問應用程序配置
"""

import os
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

# API 金鑰
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")

# 模型配置
DEFAULT_OPENAI_MODEL = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4o")
DEFAULT_OLLAMA_MODEL = os.getenv("DEFAULT_OLLAMA_MODEL", "deepseek-r1")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.3"))

# 數據目錄
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

# 確保目錄存在
def ensure_dirs():
    """確保所有必要的數據目錄存在"""
    for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)

# 初始化目錄
ensure_dirs() 