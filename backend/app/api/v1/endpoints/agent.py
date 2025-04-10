"""
Agent API 端點模組

提供與 Agent 交互的 API 端點。
"""
import time
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
import json

from ....agents.workflows.research_agent import ResearchAgent
from ....schemas.agent import AgentRequest, AgentResponse

router = APIRouter()

# 創建 Agent 實例 (在實際系統中可能會使用工廠模式或依賴注入)
research_agent = ResearchAgent()


@router.post("/query", response_model=AgentResponse)
async def query_agent(request: AgentRequest):
    """
    查詢 Agent 的同步端點。
    
    發送查詢到研究型 Agent 並等待完整回應。
    
    Args:
        request: 包含查詢和上下文的 AgentRequest 對象
        
    Returns:
        AgentResponse: 包含 Agent 回應的對象
    """
    try:
        start_time = time.time()
        
        # 運行 Agent
        response = research_agent.run(request.query)
        
        # 組裝元數據
        processing_time = time.time() - start_time
        metadata = {
            "processing_time": processing_time,
            "timestamp": time.time(),
            "agent_type": "research",
        }
        
        return AgentResponse(
            response=response,
            metadata=metadata
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent 處理錯誤: {str(e)}"
        )


@router.post("/stream")
async def stream_agent_response(request: AgentRequest):
    """
    查詢 Agent 的流式端點。
    
    發送查詢到研究型 Agent 並流式返回回應。
    
    Args:
        request: 包含查詢和上下文的 AgentRequest 對象
        
    Returns:
        StreamingResponse: 包含 Agent 流式回應的對象
    """
    try:
        async def generate():
            for chunk in research_agent.stream_run(request.query):
                # 格式化為 SSE 格式
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
            
            # 發送最後一個訊息表明完成
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Content-Disposition": "inline",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent 流處理錯誤: {str(e)}"
        ) 