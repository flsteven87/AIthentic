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


class Summarizer:
    """文本摘要生成器"""
    
    def __init__(
        self,
        model_type: str = "openai",
        model_name: Optional[str] = None,
        temperature: float = DEFAULT_TEMPERATURE,
        language: str = "zh-tw",
    ):
        """
        初始化摘要生成器
        
        Args:
            model_type: 模型類型，支持 "openai" 和 "ollama"
            model_name: 模型名稱，如果為None則使用默認模型
            temperature: 溫度參數，控制生成的隨機性
            language: 摘要語言，支持 "zh-tw"（繁體中文）和 "en"（英文）
        """
        self.model_type = model_type.lower()
        self.temperature = temperature
        self.language = language.lower()
        
        # 根據語言選擇模板
        if self.language == "zh-tw" or self.language == "zh":
            template = SUMMARY_TEMPLATE_ZH
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
        
        logger.info(f"初始化摘要生成器: {model_type}/{model_name}, 溫度: {temperature}, 語言: {language}")
    
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