"""
健康檢查 API 端點模組

本模組提供系統健康狀態的 API 端點。
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def health_check():
    """
    健康檢查端點，返回系統運行狀態。
    
    Returns:
        dict: 包含系統狀態的字典
    """
    return {
        "status": "healthy",
        "service": "AIthentic Agent API",
        "version": "0.1.0"
    } 