"""
API 路由集合模組

本模組定義了所有 API v1 版本的路由集合。
"""
from fastapi import APIRouter

from .endpoints import agent, health

# 創建 API 路由集合
api_router = APIRouter()

# 註冊各個端點路由
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])
api_router.include_router(health.router, prefix="/health", tags=["Health"]) 