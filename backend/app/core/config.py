"""
配置管理模組，負責處理環境變數和應用設定。
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 直接從 backend 目錄加載 .env 文件
backend_dir = Path(__file__).resolve().parent.parent.parent
env_path = backend_dir / ".env"
if env_path.exists():
    print(f"Loading .env from: {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    print(f"Warning: .env file not found at {env_path}")


class Settings(BaseSettings):
    """
    應用程式設定類別，負責從環境變數中加載配置。

    Attributes:
        PROJECT_NAME: 專案名稱
        DEBUG: 是否為調試模式
        API_HOST: API 主機
        API_PORT: API 端口
        BACKEND_CORS_ORIGINS: 允許的 CORS 源
        SUPABASE_URL: Supabase URL
        SUPABASE_KEY: Supabase 匿名金鑰
        SUPABASE_SECRET: Supabase 服務角色金鑰
        OPENAI_API_KEY: OpenAI API 金鑰
    """

    # 不再使用 pydantic 內建的 env_file
    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=True
    )

    PROJECT_NAME: str = "AIthentic"
    DEBUG: bool = True  # 設為 True 以顯示調試信息
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # CORS 設定
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """驗證並轉換 CORS 源設定。"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Supabase 設定
    SUPABASE_URL: Optional[str] = Field(default=None, description="Supabase URL")
    SUPABASE_KEY: Optional[str] = Field(default=None, description="Supabase 匿名金鑰")
    SUPABASE_SECRET: Optional[str] = Field(default=None, description="Supabase 服務角色金鑰")
    
    # LLM 設定
    OPENAI_API_KEY: Optional[str] = os.environ.get("OPENAI_API_KEY")


# 實例化設定
settings = Settings()

# 輸出調試信息
if settings.DEBUG:
    api_key = settings.OPENAI_API_KEY
    if api_key:
        print(f"Loaded OPENAI_API_KEY: {api_key[:5]}...{api_key[-4:]}")
    else:
        print("Warning: OPENAI_API_KEY not loaded") 