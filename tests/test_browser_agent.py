"""
瀏覽器代理測試模組
"""

import os
import asyncio
import pytest
from unittest.mock import MagicMock, patch

from langchain_openai import ChatOpenAI
from aithentic.agents.browser_agent import BrowserAgent


@pytest.mark.asyncio
async def test_browser_agent_init():
    """測試瀏覽器代理初始化"""
    # 創建模擬LLM
    mock_llm = MagicMock()
    
    # 初始化代理
    agent = BrowserAgent(
        task="測試任務",
        llm=mock_llm,
        headless=True,
    )
    
    # 驗證初始化
    assert agent.task == "測試任務"
    assert agent.llm == mock_llm
    assert agent.headless == True
    assert agent.browser is None
    assert agent.page is None


@pytest.mark.asyncio
@patch("aithentic.agents.browser_agent.async_playwright")
async def test_start_browser(mock_playwright):
    """測試啟動瀏覽器"""
    # 設置模擬
    mock_playwright_instance = MagicMock()
    mock_chromium = MagicMock()
    mock_browser = MagicMock()
    mock_page = MagicMock()
    
    mock_playwright.return_value.start.return_value = mock_playwright_instance
    mock_playwright_instance.chromium = mock_chromium
    mock_chromium.launch.return_value = mock_browser
    mock_browser.new_page.return_value = mock_page
    
    # 創建代理
    agent = BrowserAgent(
        task="測試任務",
        llm=MagicMock(),
        headless=True,
    )
    
    # 調用方法
    await agent.start_browser()
    
    # 驗證
    mock_playwright.assert_called_once()
    mock_playwright.return_value.start.assert_called_once()
    mock_chromium.launch.assert_called_once_with(headless=True)
    mock_browser.new_page.assert_called_once()
    assert agent.browser == mock_browser
    assert agent.page == mock_page


@pytest.mark.asyncio
@patch("aithentic.agents.browser_agent.BeautifulSoup")
def test_extract_text_from_html(mock_bs):
    """測試從HTML提取文本"""
    # 設置模擬
    mock_soup = MagicMock()
    mock_bs.return_value = mock_soup
    mock_soup.get_text.return_value = "Line1\n\nLine2\n  Line3  \n\n"
    
    # 創建代理
    agent = BrowserAgent(
        task="測試任務",
        llm=MagicMock(),
    )
    
    # 調用方法
    result = agent.extract_text_from_html("<html><body>Test</body></html>")
    
    # 驗證
    mock_bs.assert_called_once_with("<html><body>Test</body></html>", "html.parser")
    mock_soup.get_text.assert_called_once()
    assert "Line1" in result
    assert "Line2" in result
    assert "Line3" in result


@pytest.mark.asyncio
@patch("aithentic.agents.browser_agent.BrowserAgent.navigate_to")
@patch("aithentic.agents.browser_agent.BrowserAgent.extract_text_from_html")
@patch("aithentic.agents.browser_agent.BrowserAgent.analyze_content")
async def test_run(mock_analyze, mock_extract, mock_navigate):
    """測試執行任務"""
    # 設置模擬
    mock_navigate.return_value = "<html>Test</html>"
    mock_extract.return_value = "Extracted text"
    mock_analyze.return_value = "Analysis result"
    
    # 創建代理
    agent = BrowserAgent(
        task="訪問 https://example.com 並摘要內容",
        llm=MagicMock(),
    )
    
    # 調用方法
    result = await agent.run()
    
    # 驗證
    mock_navigate.assert_called_once_with("https://example.com")
    mock_extract.assert_called_once_with("<html>Test</html>")
    mock_analyze.assert_called_once_with("Extracted text")
    assert result == "Analysis result"


if __name__ == "__main__":
    asyncio.run(pytest.main(["-xvs", __file__])) 