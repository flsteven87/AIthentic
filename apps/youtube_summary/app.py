"""
YouTube影片摘要應用主程式
"""

import os
from pathlib import Path
import streamlit as st
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
import inspect

from aithentic.config import DATA_DIR
from aithentic.tools.summarizer import Summarizer
from aithentic.utils.file_utils import ensure_dir, clean_filename, save_json, load_json

from apps.youtube_summary.utils import (
    extract_video_id,
    get_video_info,
    download_youtube_audio,
    transcribe_with_whisper,
)

# 設置日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 設置頁面配置 - 必須是第一個 Streamlit 命令
st.set_page_config(page_title="YouTube Video Summarizer", layout="wide")

# 確保數據目錄存在
YOUTUBE_DATA_DIR = os.path.join(DATA_DIR, "youtube_summary")
ensure_dir(YOUTUBE_DATA_DIR)


def process_youtube_video(url: str, language: str = "zh-tw", use_local_model: bool = False, use_markdown: bool = True) -> Dict:
    """
    處理YouTube視頻：下載、轉錄和摘要
    
    Args:
        url: YouTube URL
        language: 處理語言 (預設為 zh-tw)
        use_local_model: 是否使用本地模型進行轉錄 (預設為 False)
        use_markdown: 是否使用 Markdown 格式摘要 (預設為 True)
        
    Returns:
        處理結果字典
    """
    st.write("### 處理 YouTube 影片")
    
    # 提取視頻ID
    video_id = extract_video_id(url)
    if not video_id:
        st.error("無效的YouTube URL，無法提取視頻ID")
        return {"error": "無效的YouTube URL"}
    
    # 檢查是否已處理過
    result_file = os.path.join(YOUTUBE_DATA_DIR, f"{video_id}_result.json")
    if os.path.exists(result_file):
        st.info("找到已處理的結果，正在載入...")
        return load_json(result_file)
    
    # 顯示進度
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # 步驟1: 獲取視頻信息
        status_text.text("獲取視頻信息...")
        video_info = get_video_info(url)
        progress_bar.progress(10)
        
        title = video_info.get('title', 'Unknown Title')
        st.write(f"### 視頻標題: {title}")
        
        # 步驟2: 下載音頻
        status_text.text("下載音頻...")
        audio_path, clean_title = download_youtube_audio(url, YOUTUBE_DATA_DIR)
        if not audio_path:
            st.error("下載音頻失敗")
            return {"error": "下載音頻失敗"}
        progress_bar.progress(30)
        
        # 步驟3: 轉錄音頻
        status_text.text("轉錄音頻...")
        transcript = transcribe_with_whisper(
            audio_path,
            model_size="base",
            language=language[:2] if language else None,  # 取前兩個字符作為語言代碼
            local_model=use_local_model,
        )
        
        # 保存轉錄結果
        transcript_file = os.path.join(YOUTUBE_DATA_DIR, f"{video_id}_transcript.txt")
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript)
        
        progress_bar.progress(70)
        
        # 步驟4: 生成摘要
        status_text.text("生成摘要...")
        output_format = "markdown" if use_markdown else "text"
        
        # 添加調試代碼
        logger.info(f"Summarizer.__init__ 簽名: {inspect.signature(Summarizer.__init__)}")
        logger.info(f"Summarizer.__init__ 參數: {inspect.getfullargspec(Summarizer.__init__)}")
        
        try:
            summarizer = Summarizer(
                model_type="openai",
                model_name=None,
                temperature=0.3,
                language=language,
                output_format=output_format,
            )
            
            summary = summarizer.summarize(transcript)
            progress_bar.progress(90)
        except Exception as e:
            logger.exception(f"創建 Summarizer 實例時發生錯誤: {str(e)}")
            raise
        
        # 保存結果
        result = {
            "video_id": video_id,
            "title": title,
            "url": url,
            "transcript_file": transcript_file,
            "summary": summary,
            "video_info": video_info,
            "processed_time": time.time(),
            "summary_format": output_format,
            "language": language,
        }
        
        save_json(result, result_file)
        progress_bar.progress(100)
        status_text.text("處理完成！")
        
        return result
    
    except Exception as e:
        logger.exception(f"處理視頻時發生錯誤: {str(e)}")
        st.error(f"處理視頻時發生錯誤: {str(e)}")
        return {"error": str(e)}


def get_processed_videos() -> List[Dict]:
    """
    獲取已處理的視頻列表
    
    Returns:
        已處理視頻的列表
    """
    result_files = list(Path(YOUTUBE_DATA_DIR).glob("*_result.json"))
    videos = []
    
    for file in result_files:
        try:
            data = load_json(file)
            videos.append({
                "video_id": data.get("video_id"),
                "title": data.get("title"),
                "url": data.get("url"),
                "processed_time": data.get("processed_time"),
            })
        except Exception as e:
            logger.error(f"讀取結果文件時發生錯誤 {file}: {str(e)}")
    
    # 按處理時間排序
    videos.sort(key=lambda x: x.get("processed_time", 0), reverse=True)
    return videos


def display_video_summary(video_id: str):
    """
    顯示視頻摘要
    
    Args:
        video_id: 視頻ID
    """
    result_file = os.path.join(YOUTUBE_DATA_DIR, f"{video_id}_result.json")
    if not os.path.exists(result_file):
        st.error(f"找不到視頻ID {video_id} 的處理結果")
        return
    
    data = load_json(result_file)
    
    # 使用容器組織內容
    with st.container():
        # 顯示視頻信息
        st.title(data.get('title'))
        
        # 使用列佈局
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 添加重新生成摘要按鈕
            col1_1, col1_2 = st.columns([4, 1])
            with col1_1:
                st.subheader("📝 視頻摘要")
            with col1_2:
                if st.button("🔄 重新生成", key="regenerate_summary"):
                    st.info("正在重新生成摘要...")
                    # 獲取轉錄文本
                    transcript_file = data.get("transcript_file")
                    if transcript_file and os.path.exists(transcript_file):
                        with open(transcript_file, "r", encoding="utf-8") as f:
                            transcript = f.read()
                        
                        # 創建摘要生成器
                        summarizer = Summarizer(
                            model_type="openai",
                            model_name=None,
                            temperature=0.3,
                            language=data.get("language", "zh-tw"),
                            output_format="markdown",
                        )
                        
                        # 生成新摘要
                        summary = summarizer.summarize(transcript)
                        
                        # 更新數據
                        data["summary"] = summary
                        data["summary_format"] = "markdown"
                        data["updated_time"] = time.time()
                        
                        # 保存更新後的數據
                        save_json(data, result_file)
                        st.success("摘要已重新生成！")
                        st.rerun()
                    else:
                        st.error("找不到轉錄文件，無法重新生成摘要")
            
            # 檢查摘要格式，如果是 markdown 則使用 st.markdown
            if data.get("summary_format") == "markdown":
                st.markdown(data.get("summary", ""))
            else:
                st.write(data.get("summary", ""))
        
        with col2:
            # 顯示視頻縮略圖
            thumbnail = data.get("video_info", {}).get("thumbnail")
            if thumbnail:
                st.image(thumbnail, use_container_width=True)
            
            # 顯示視頻信息
            st.subheader("ℹ️ 視頻信息")
            
            info = data.get("video_info", {})
            st.write(f"📺 頻道: {info.get('channel', 'Unknown')}")
            st.write(f"📅 上傳日期: {info.get('upload_date', 'Unknown')}")
            st.write(f"👁️ 觀看次數: {info.get('view_count', 'Unknown')}")
            st.write(f"🔗 [在YouTube上觀看視頻]({data.get('url')})")
    
    # 顯示完整轉錄
    with st.expander("查看完整轉錄"):
        transcript_file = data.get("transcript_file")
        if transcript_file and os.path.exists(transcript_file):
            with open(transcript_file, "r", encoding="utf-8") as f:
                transcript = f.read()
            st.text_area("完整轉錄", transcript, height=400)
        else:
            st.warning("轉錄文件不存在或無法讀取")


def main():
    """主程序入口"""
    st.title("YouTube 影片摘要生成器")
    
    # 側邊欄 - 顯示已處理的影片列表和新增摘要按鈕
    st.sidebar.title("已處理的影片")
    
    # 新增摘要按鈕
    if st.sidebar.button("➕ 新增影片摘要", key="new_summary"):
        st.session_state.selected_video = None
        st.session_state.show_form = True
        st.rerun()
    
    st.sidebar.markdown("---")
    
    videos = get_processed_videos()
    
    if videos:
        for idx, video in enumerate(videos):
            title = video.get('title', 'Unknown')
            title_display = f"{title[:40]}..." if len(title) > 40 else title
            
            st.sidebar.write(f"**{title_display}**")
            
            if st.sidebar.button(f"查看摘要", key=f"view_{idx}"):
                st.session_state.selected_video = video.get("video_id")
                st.session_state.show_form = False
                st.rerun()
            
            st.sidebar.markdown("---")
    else:
        st.sidebar.info("尚未處理任何影片")
    
    # 檢查是否有選擇的視頻
    if "selected_video" in st.session_state and st.session_state.selected_video:
        display_video_summary(st.session_state.selected_video)
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("⬅️ 返回首頁"):
                st.session_state.selected_video = None
                st.session_state.show_form = True
                st.rerun()
        return
    
    # 主要界面 - URL輸入和參數設置
    if not "show_form" in st.session_state:
        st.session_state.show_form = True
        
    if st.session_state.show_form:
        with st.container():
            with st.form("youtube_form"):
                st.subheader("輸入YouTube影片資訊")
                
                url = st.text_input("輸入YouTube影片URL", "")
                
                # 添加高級選項
                with st.expander("⚙️ 高級選項"):
                    col1, col2 = st.columns(2)
                    with col1:
                        language = st.selectbox(
                            "處理語言",
                            options=["zh-tw", "en"],
                            index=0,
                            format_func=lambda x: "繁體中文" if x == "zh-tw" else "English"
                        )
                    with col2:
                        use_markdown = st.checkbox("使用 Markdown 格式摘要", value=True, help="生成結構化的 Markdown 格式摘要")
                
                submit_button = st.form_submit_button("🚀 開始處理")
            
            # 顯示使用說明
            with st.expander("📖 使用說明"):
                st.markdown("""
                ### 如何使用此工具:
                1. 輸入任何YouTube影片的URL
                2. 點擊「開始處理」按鈕
                3. 等待系統下載、轉錄和摘要處理
                4. 查看生成的摘要結果
                
                ### 注意事項:
                - 處理時間取決於影片長度
                - 已處理的影片會保存在側邊欄中，可隨時查看
                - 系統預設使用繁體中文(zh-tw)處理影片
                """)
    
    if "submit_button" in locals() and submit_button and url:
        # 獲取表單中的選項
        form_language = language if "language" in locals() else "zh-tw"
        form_use_markdown = use_markdown if "use_markdown" in locals() else True
        
        # 處理視頻
        result = process_youtube_video(
            url=url,
            language=form_language,
            use_local_model=False,
            use_markdown=form_use_markdown
        )
        
        if "error" in result:
            st.error(result["error"])
        else:
            # 處理成功後更新選擇的視頻ID並重新加載頁面
            st.session_state.selected_video = result.get("video_id")
            st.session_state.show_form = False
            st.rerun()


if __name__ == "__main__":
    main() 