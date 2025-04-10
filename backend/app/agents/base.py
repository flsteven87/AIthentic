"""
基礎 Agent 模組

定義了所有 Agent 的基礎類別和共用功能。
"""
from typing import Any, Dict, List, Optional, Union

from agno.agent import Agent as AgnoAgent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

from ..core.config import settings


class BaseAgent:
    """
    基礎 Agent 類別，負責創建和管理 Agent 實例。
    
    這個類別封裝了 agno 框架的 Agent，提供應用程序特定的配置。
    """

    def __init__(
        self,
        instructions: str,
        model_id: str = "gpt-4o-mini",
        enable_web_search: bool = True,
        markdown: bool = True,
        custom_tools: Optional[List[Any]] = None,
    ):
        """
        初始化 Agent 實例。

        Args:
            instructions: Agent 的指導指令
            model_id: 使用的 LLM 模型 ID
            enable_web_search: 是否啟用網頁搜索功能
            markdown: 是否啟用 markdown 輸出
            custom_tools: 自定義工具列表
        """
        # 設定 model
        model = OpenAIChat(
            id=model_id,
            api_key=settings.OPENAI_API_KEY,
        )
        
        # 準備工具
        tools = []
        if enable_web_search:
            tools.append(DuckDuckGoTools())
        
        if custom_tools:
            tools.extend(custom_tools)
            
        # 創建 agno Agent
        self.agent = AgnoAgent(
            model=model,
            instructions=instructions,
            tools=tools,
            markdown=markdown,
            show_tool_calls=True,
        )
    
    def run(self, prompt: str) -> str:
        """
        運行 Agent 並回應用戶的查詢。

        Args:
            prompt: 用戶的查詢提示

        Returns:
            str: Agent 的回應
        """
        response = self.agent.run(prompt)
        
        # 處理 RunResponse 對象，確保返回字符串
        if hasattr(response, 'content'):
            return str(response.content)
        elif isinstance(response, dict) and 'content' in response:
            return str(response['content'])
        
        # 如果 response 不是預期格式，將其轉換為字符串
        return str(response)
        
    def stream_run(self, prompt: str):
        """
        以流式方式運行 Agent 並回應用戶的查詢。

        Args:
            prompt: 用戶的查詢提示

        Yields:
            str: Agent 回應的片段
        """
        for chunk in self.agent.stream(prompt):
            # 確保每個 chunk 是字符串
            if hasattr(chunk, 'content'):
                yield str(chunk.content)
            elif isinstance(chunk, dict) and 'content' in chunk:
                yield str(chunk['content'])
            else:
                yield str(chunk) 