"""
瀏覽器代理模組，提供網頁瀏覽和內容分析功能
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from langchain.schema import HumanMessage
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# 設置日誌記錄
logger = logging.getLogger(__name__)


class BrowserAgent:
    """瀏覽器代理，用於自動化網頁瀏覽和內容分析"""
    
    def __init__(
        self,
        task: str,
        llm: Any,
        headless: bool = True,
        screenshot_dir: Optional[str] = None,
    ):
        """
        初始化瀏覽器代理
        
        Args:
            task: 要執行的任務描述
            llm: 語言模型實例，用於分析網頁內容
            headless: 是否以無頭模式運行瀏覽器
            screenshot_dir: 截圖保存目錄，如果為None則不保存截圖
        """
        self.task = task
        self.llm = llm
        self.headless = headless
        self.screenshot_dir = screenshot_dir
        self.browser = None
        self.page = None
    
    async def start_browser(self):
        """啟動瀏覽器"""
        logger.info("啟動瀏覽器")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
    
    async def navigate_to(self, url: str) -> str:
        """
        導航到指定URL並返回頁面內容
        
        Args:
            url: 要訪問的URL
            
        Returns:
            頁面HTML內容
        """
        logger.info(f"導航到: {url}")
        if not self.page:
            await self.start_browser()
            
        await self.page.goto(url)
        
        # 等待頁面加載完成
        await self.page.wait_for_load_state("networkidle")
        
        # 截圖（如果啟用）
        if self.screenshot_dir:
            from aithentic.utils.file_utils import ensure_dir, clean_filename
            import os
            from datetime import datetime
            
            ensure_dir(self.screenshot_dir)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{clean_filename(url)}_{timestamp}.png"
            screenshot_path = os.path.join(self.screenshot_dir, filename)
            await self.page.screenshot(path=screenshot_path)
            logger.info(f"保存截圖: {screenshot_path}")
        
        # 獲取頁面內容
        content = await self.page.content()
        return content
    
    def extract_text_from_html(self, html: str) -> str:
        """
        從HTML中提取文本內容
        
        Args:
            html: HTML內容
            
        Returns:
            提取的文本內容
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # 移除腳本和樣式元素
        for script in soup(["script", "style"]):
            script.extract()
        
        # 獲取文本
        text = soup.get_text(separator="\n", strip=True)
        
        # 清理空行
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = "\n".join(lines)
        
        return text
    
    async def analyze_content(self, content: str) -> str:
        """
        使用LLM分析網頁內容
        
        Args:
            content: 網頁內容
            
        Returns:
            分析結果
        """
        # 確保內容不過長
        max_length = 16000  # 適當的長度限制
        if len(content) > max_length:
            content = content[:max_length] + "...(內容被截斷)"
        
        prompt = f"""
        請分析以下網頁內容，並根據任務要求提供結果。
        
        任務: {self.task}
        
        網頁內容:
        {content}
        
        請提供詳細的分析結果，並確保內容準確性。
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return response.content
    
    async def run(self) -> str:
        """
        執行瀏覽器代理任務
        
        Returns:
            任務執行結果
        """
        logger.info(f"開始執行任務: {self.task}")
        
        try:
            # 從任務描述中提取URL
            import re
            url_match = re.search(r'https?://[^\s,]+', self.task)
            if not url_match:
                return "錯誤: 無法從任務描述中提取URL"
            
            url = url_match.group(0)
            logger.info(f"提取的URL: {url}")
            
            # 導航到URL
            html_content = await self.navigate_to(url)
            
            # 提取文本內容
            text_content = self.extract_text_from_html(html_content)
            
            # 分析內容
            result = await self.analyze_content(text_content)
            
            return result
        
        except Exception as e:
            logger.exception(f"執行任務時發生錯誤: {str(e)}")
            return f"錯誤: {str(e)}"
        
        finally:
            # 關閉瀏覽器
            if self.browser:
                await self.browser.close()
                logger.info("瀏覽器已關閉")


# 兼容性別名，保持向後兼容
Agent = BrowserAgent 