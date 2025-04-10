"""
數據庫會話模塊，負責管理與 Supabase 的連接。
"""
from typing import Dict, Any, AsyncGenerator, Optional

from supabase import create_client, Client
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from ..core.config import settings


class SupabaseClient:
    """
    Supabase 客戶端管理類。

    負責創建和管理與 Supabase 的連接。
    """

    _instance: "SupabaseClient" = None
    _client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            if settings.SUPABASE_URL and settings.SUPABASE_KEY:
                cls._client = create_client(
                    settings.SUPABASE_URL, settings.SUPABASE_KEY
                )
            else:
                cls._client = None
        return cls._instance

    @property
    def client(self) -> Optional[Client]:
        """獲取 Supabase 客戶端實例，如果未配置則返回 None。"""
        return self._client


# 創建 PostgreSQL 連接 URL (僅在 Supabase 配置可用時)
ASYNC_DATABASE_URL = None
async_engine = None
AsyncSessionLocal = None

if settings.SUPABASE_URL and settings.SUPABASE_SECRET:
    ASYNC_DATABASE_URL = f"postgresql+asyncpg://{settings.SUPABASE_URL.split('//')[1].split('.')[0]}:{settings.SUPABASE_SECRET}@db.{settings.SUPABASE_URL.split('//')[1]}/postgres"
    
    # 創建異步引擎
    async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=settings.DEBUG)
    
    # 創建異步會話工廠
    AsyncSessionLocal = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    獲取資料庫會話的依賴函數。

    Yields:
        AsyncSession: 數據庫會話，或者在未配置 Supabase 時為 None
    """
    if AsyncSessionLocal is None:
        return None
        
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# 創建 Supabase 客戶端實例
supabase = SupabaseClient().client 