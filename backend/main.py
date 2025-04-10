"""
AIthentic 主應用程序入口

本模組定義了 FastAPI 應用程序的入口點，集成了路由和中間件。
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api import api_router

# 創建 FastAPI 應用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AIthentic LLM Agent API",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# 設定 CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 註冊 API 路由
app.include_router(api_router, prefix="/api/v1")

# 健康檢查端點
@app.get("/health")
async def health_check():
    """
    健康檢查端點，用於監控應用狀態。
    """
    return {"status": "ok"}

if __name__ == "__main__":
    """啟動 FastAPI 開發伺服器"""
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    ) 