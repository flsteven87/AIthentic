"""
研究型 Agent 工作流模組

實現了一個專注於資訊搜索和整理的 Agent 工作流。
"""
from textwrap import dedent

from ..base import BaseAgent


class ResearchAgent(BaseAgent):
    """
    研究型 Agent，專注於資訊搜索、整理和總結。
    
    這個 Agent 能夠搜索網絡上的資訊，整理並將多個來源的信息進行比較和總結。
    """
    
    def __init__(self):
        """
        初始化研究型 Agent，設定特定的指令和功能。
        """
        instructions = dedent("""
            你是一個專業的研究助手，專注於為用戶提供高質量的資訊搜索和整理服務。
            
            請遵循以下指南：
            
            1. 當用戶提出問題時，使用網頁搜索工具獲取最相關、最新的資訊
            2. 整理來自多個來源的資訊，確保全面性和準確性
            3. 重點關注：
               - 資訊的時效性和可靠性
               - 數據的準確性和來源
               - 不同觀點的平衡呈現
            4. 回應應該結構良好，使用標題和分點列表增強可讀性
            5. 適當引用資訊來源，讓用戶能夠進一步了解
            6. 如果搜索結果有限或不夠新，請明確說明
            
            回應格式：
            1. 簡短摘要（1-2 句話總結發現）
            2. 主要發現（使用小標題和列表）
            3. 結論或建議（基於整合的資訊）
            4. 使用的資訊來源（適當列出）
        """)
        
        super().__init__(
            instructions=instructions,
            model_id="gpt-4o",
            enable_web_search=True,
            markdown=True
        ) 