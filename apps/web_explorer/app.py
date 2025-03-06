"""
網頁瀏覽和摘要應用主程式
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from langchain_openai import ChatOpenAI
import streamlit as st

from aithentic.agents.browser_agent import BrowserAgent
from aithentic.config import DATA_DIR, DEFAULT_OPENAI_MODEL
from aithentic.utils.file_utils import ensure_dir, clean_filename, save_json, load_json

# 設置日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 設置頁面配置
st.set_page_config(page_title="Web Explorer", layout="wide")

# 確保數據目錄存在
WEB_DATA_DIR = os.path.join(DATA_DIR, "web_explorer")
SCREENSHOT_DIR = os.path.join(WEB_DATA_DIR, "screenshots")
ensure_dir(WEB_DATA_DIR)
ensure_dir(SCREENSHOT_DIR)


async def browse_website(url: str, task: str, model_name: str) -> Dict:
    """
    瀏覽網站並執行任務
    
    Args:
        url: 網站URL
        task: 要執行的任務
        model_name: 使用的模型名稱
        
    Returns:
        處理結果字典
    """
    # 創建任務描述
    full_task = f"""瀏覽網站 {url} 並{task}"""
    
    # 檢查是否有緩存的結果
    cache_key = clean_filename(f"{url}_{task}_{model_name}")
    cache_file = os.path.join(WEB_DATA_DIR, f"{cache_key}.json")
    
    if os.path.exists(cache_file):
        st.info("找到緩存的結果，正在載入...")
        return load_json(cache_file)
    
    # 顯示進度
    progress_placeholder = st.empty()
    progress_placeholder.info("正在啟動瀏覽器...")
    
    try:
        # 創建LLM實例
        llm = ChatOpenAI(model=model_name)
        
        # 創建瀏覽器代理
        agent = BrowserAgent(
            task=full_task,
            llm=llm,
            headless=True,
            screenshot_dir=SCREENSHOT_DIR,
        )
        
        # 執行任務
        progress_placeholder.info("正在瀏覽網站並處理內容...")
        result = await agent.run()
        
        # 保存結果
        timestamp = datetime.now().isoformat()
        output = {
            "url": url,
            "task": task,
            "model": model_name,
            "result": result,
            "timestamp": timestamp,
        }
        
        save_json(output, cache_file)
        progress_placeholder.success("處理完成！")
        
        return output
    
    except Exception as e:
        logger.exception(f"執行任務時發生錯誤: {str(e)}")
        progress_placeholder.error(f"執行任務時發生錯誤: {str(e)}")
        return {"error": str(e)}


def get_recent_explorations() -> List[Dict]:
    """
    獲取最近的網頁探索記錄
    
    Returns:
        最近的網頁探索記錄列表
    """
    result_files = [f for f in os.listdir(WEB_DATA_DIR) if f.endswith('.json')]
    results = []
    
    for file in result_files:
        try:
            data = load_json(os.path.join(WEB_DATA_DIR, file))
            results.append({
                "url": data.get("url", "未知URL"),
                "task": data.get("task", "未知任務"),
                "timestamp": data.get("timestamp", ""),
                "file": file,
            })
        except Exception as e:
            logger.error(f"讀取結果文件時發生錯誤 {file}: {str(e)}")
    
    # 按時間戳排序
    results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return results


def display_exploration_result(file_name: str):
    """
    顯示網頁探索結果
    
    Args:
        file_name: 結果文件名稱
    """
    result_file = os.path.join(WEB_DATA_DIR, file_name)
    if not os.path.exists(result_file):
        st.error(f"找不到結果文件: {file_name}")
        return
    
    data = load_json(result_file)
    
    # 顯示頁面標題
    st.write(f"## 瀏覽結果: {data.get('url')}")
    
    # 顯示結果
    st.write("### 任務")
    st.write(data.get("task", ""))
    
    st.write("### 結果")
    st.write(data.get("result", ""))
    
    # 顯示截圖
    st.write("### 截圖")
    screenshots = [f for f in os.listdir(SCREENSHOT_DIR) if data.get("url", "") in f]
    
    if screenshots:
        screenshot_path = os.path.join(SCREENSHOT_DIR, screenshots[0])
        st.image(screenshot_path)
    else:
        st.info("沒有可用的截圖")
    
    # 顯示元數據
    st.write("### 元數據")
    st.write(f"URL: {data.get('url')}")
    st.write(f"模型: {data.get('model')}")
    st.write(f"處理時間: {data.get('timestamp')}")


def main():
    """主程序入口"""
    st.title("網頁瀏覽與摘要工具")
    
    # 側邊欄 - 顯示最近的探索記錄
    st.sidebar.title("最近的探索")
    recent_explorations = get_recent_explorations()
    
    if recent_explorations:
        for idx, exploration in enumerate(recent_explorations):
            url_display = exploration.get("url", "")
            if len(url_display) > 40:
                url_display = url_display[:37] + "..."
            
            if st.sidebar.button(f"{url_display}", key=f"exp_{idx}"):
                st.session_state.selected_exploration = exploration.get("file")
                st.rerun()
    else:
        st.sidebar.info("尚無探索記錄")
    
    # 檢查是否有選擇的探索記錄
    if "selected_exploration" in st.session_state:
        display_exploration_result(st.session_state.selected_exploration)
        if st.button("返回首頁"):
            del st.session_state.selected_exploration
            st.rerun()
        return
    
    # 主要界面 - URL輸入和任務設置
    with st.form("web_form"):
        url = st.text_input("輸入網站URL", "")
        
        task_options = [
            "生成網頁內容摘要",
            "提取關鍵信息",
            "回答關於網頁內容的問題",
            "分析網頁結構",
            "自定義任務"
        ]
        
        task_type = st.selectbox("選擇任務類型", task_options)
        
        if task_type == "自定義任務":
            task = st.text_area("輸入自定義任務描述", "")
        elif task_type == "回答關於網頁內容的問題":
            question = st.text_input("輸入您的問題")
            task = f"回答以下問題: {question}"
        else:
            task = task_type
        
        model_name = st.selectbox(
            "選擇模型",
            [DEFAULT_OPENAI_MODEL, "gpt-4", "gpt-4o-mini", "gpt-3.5-turbo"],
            index=0
        )
        
        submit_button = st.form_submit_button("開始瀏覽")
    
    if submit_button and url and task:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # 執行瀏覽任務
        result = asyncio.run(browse_website(url, task, model_name))
        
        if "error" in result:
            st.error(result["error"])
        else:
            # 創建一個唯一的識別碼用於重新訪問此結果
            cache_key = clean_filename(f"{url}_{task}_{model_name}")
            cache_file = f"{cache_key}.json"
            
            # 將識別碼存儲在session_state中並重新加載頁面
            st.session_state.selected_exploration = cache_file
            st.rerun()


if __name__ == "__main__":
    main() 