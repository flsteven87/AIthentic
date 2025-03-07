"""
文本摘要工具模組，提供不同模型的文本摘要功能
"""

import logging
from typing import Any, Dict, List, Optional, Union

from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import BaseOutputParser

from aithentic.config import DEFAULT_OPENAI_MODEL, DEFAULT_OLLAMA_MODEL, DEFAULT_TEMPERATURE

# 設置日誌記錄
logger = logging.getLogger(__name__)


# 中文摘要模板
SUMMARY_TEMPLATE_ZH = """請為以下文本生成一個簡潔的中文摘要：

{text}

摘要:"""

# 英文摘要模板
SUMMARY_TEMPLATE_EN = """Generate a concise summary of the following text:

{text}

Summary:"""

# 中文 Markdown 摘要模板
SUMMARY_TEMPLATE_ZH_MD = """請為以下 YouTube 影片轉錄文本生成一個結構化的 Markdown 格式摘要：

{text}

請使用以下 Markdown 格式輸出摘要：
1. 使用 ## 作為主標題（影片主題）
2. 使用 ### 作為小標題（主要章節或時間點）
3. 使用 - 或 * 作為列表項目
4. 使用 > 引用重要觀點或結論
5. 適當使用 **粗體** 或 *斜體* 強調關鍵詞
6. 如果能識別出時間點，請使用 [時間點](時間點) 格式

摘要應包含：
- 影片的主要主題和目的（100-150字）
- 3-5 個關鍵點或章節，每個配有簡短描述（每點50-100字）
- 總結或結論（50-100字）

摘要總長度應在300-600字之間，根據影片內容的複雜度調整。

格式示例：
## 影片主題：[主題名稱]

### 主要內容
- **關鍵點1**：關於這個點的簡短描述...
- **關鍵點2**：關於這個點的簡短描述...

### 重要觀點
> 引用影片中的重要觀點或結論

### 總結
最終的總結或結論...

請根據以上指南生成摘要："""

# 英文 Markdown 摘要模板
SUMMARY_TEMPLATE_EN_MD = """Generate a structured Markdown summary for the following YouTube video transcript:

{text}

Please format the summary using Markdown:
1. Use ## for main title (video topic)
2. Use ### for subtitles (main sections or timestamps)
3. Use - or * for list items
4. Use > for important quotes or conclusions
5. Use **bold** or *italic* to emphasize key terms
6. If you can identify timestamps, use [timestamp](timestamp) format

The summary should include:
- The main topic and purpose of the video (100-150 words)
- 3-5 key points or sections, each with a brief description (50-100 words each)
- A conclusion or takeaway (50-100 words)

The total summary length should be between 300-600 words, adjusted based on the complexity of the video content.

Format example:
## Video Topic: [Topic Name]

### Main Content
- **Key Point 1**: Brief description about this point...
- **Key Point 2**: Brief description about this point...

### Important Insights
> Quote important viewpoints or conclusions from the video

### Conclusion
Final summary or conclusion...

Please generate the summary following the guidelines above:"""


class Summarizer:
    """文本摘要生成器"""
    
    def __init__(
        self,
        model_type: str = "openai",
        model_name: Optional[str] = None,
        temperature: float = DEFAULT_TEMPERATURE,
        language: str = "zh-tw",
        output_format: str = "text",
    ):
        """
        初始化摘要生成器
        
        Args:
            model_type: 模型類型，支持 "openai" 和 "ollama"
            model_name: 模型名稱，如果為None則使用默認模型
            temperature: 溫度參數，控制生成的隨機性
            language: 摘要語言，支持 "zh-tw"（繁體中文）和 "en"（英文）
            output_format: 輸出格式，支持 "text"（純文本）和 "markdown"（Markdown格式）
        """
        self.model_type = model_type.lower()
        self.temperature = temperature
        self.language = language.lower()
        self.output_format = output_format.lower()
        
        # 根據語言和輸出格式選擇模板
        if self.language == "zh-tw" or self.language == "zh":
            if self.output_format == "markdown":
                template = SUMMARY_TEMPLATE_ZH_MD
            else:
                template = SUMMARY_TEMPLATE_ZH
        else:
            if self.output_format == "markdown":
                template = SUMMARY_TEMPLATE_EN_MD
            else:
                template = SUMMARY_TEMPLATE_EN
        
        # 建立 prompt template 實例
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["text"]
        )
        
        # 初始化模型
        if self.model_type == "openai":
            model_name = model_name or DEFAULT_OPENAI_MODEL
            self.model = ChatOpenAI(
                model=model_name,
                temperature=temperature
            )
        elif self.model_type == "ollama":
            model_name = model_name or DEFAULT_OLLAMA_MODEL
            self.model = ChatOllama(
                model=model_name,
                temperature=temperature
            )
        else:
            raise ValueError(f"不支持的模型類型: {model_type}, 僅支持 'openai' 和 'ollama'")
        
        # 建立處理鏈
        self.chain = self.prompt | self.model | StrOutputParser()
        
        logger.info(f"初始化摘要生成器: {model_type}/{model_name}, 溫度: {temperature}, 語言: {language}, 輸出格式: {output_format}")
    
    def summarize(self, text: str) -> str:
        """
        生成文本摘要
        
        Args:
            text: 輸入文本
            
        Returns:
            生成的摘要
        """
        logger.info(f"生成摘要，文本長度: {len(text)}")
        try:
            summary = self.chain.invoke({"text": text})
            return summary.strip()
        except Exception as e:
            logger.exception(f"生成摘要時發生錯誤: {str(e)}")
            raise
    
    async def asummarize(self, text: str) -> str:
        """
        非同步生成文本摘要
        
        Args:
            text: 輸入文本
            
        Returns:
            生成的摘要
        """
        logger.info(f"非同步生成摘要，文本長度: {len(text)}")
        try:
            summary = await self.chain.ainvoke({"text": text})
            return summary.strip()
        except Exception as e:
            logger.exception(f"非同步生成摘要時發生錯誤: {str(e)}")
            raise 