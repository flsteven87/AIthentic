"""
Agent API 的 Pydantic 模型

定義了 Agent API 相關的請求和響應模型。
"""
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """
    Agent 請求模型，包含用戶的查詢和可選的上下文信息。
    """
    query: str = Field(..., description="用戶的查詢或問題")
    context: Optional[Dict[str, Union[str, int, float, bool, List]]] = Field(
        default=None, description="可選的上下文信息"
    )


class AgentResponse(BaseModel):
    """
    Agent 響應模型，包含回應內容和元數據。
    """
    response: str = Field(..., description="Agent 的回應內容")
    metadata: Optional[Dict[str, Union[str, int, float, bool, List]]] = Field(
        default=None, description="回應的相關元數據"
    )


class StreamResponse(BaseModel):
    """
    流式響應的單個片段模型。
    """
    content: str = Field(..., description="響應內容片段")
    done: bool = Field(..., description="是否為最後一個片段") 