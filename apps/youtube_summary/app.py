"""
YouTube影片摘要應用主程式
"""

import streamlit as st
import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


def process_youtube_video(url: str, language: str, use_local_model: bool) -> Dict:
    """
    處理YouTube視頻：下載、轉錄和摘要
    
    Args:
        url: YouTube URL
        language: 處理語言
        use_local_model: 是否使用本地模型進行轉錄
        
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
        summarizer = Summarizer(
            model_type="openai",
            language=language,
        )
        
        summary = summarizer.summarize(transcript)
        progress_bar.progress(90)
        
        # 保存結果
        result = {
            "video_id": video_id,
            "title": title,
            "url": url,
            "transcript_file": transcript_file,
            "summary": summary,
            "video_info": video_info,
            "processed_time": time.time(),
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
    
    # 顯示視頻信息
    st.write(f"## {data.get('title')}")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("### 視頻摘要")
        st.write(data.get("summary", ""))
    
    with col2:
        # 顯示視頻縮略圖
        thumbnail = data.get("video_info", {}).get("thumbnail")
        if thumbnail:
            st.image(thumbnail, use_column_width=True)
        
        # 顯示視頻信息
        st.write("### 視頻信息")
        info = data.get("video_info", {})
        st.write(f"頻道: {info.get('channel', 'Unknown')}")
        st.write(f"上傳日期: {info.get('upload_date', 'Unknown')}")
        st.write(f"觀看次數: {info.get('view_count', 'Unknown')}")
        
        # 視頻鏈接
        st.write(f"[在YouTube上觀看視頻]({data.get('url')})")
    
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
    
    # 側邊欄 - 顯示已處理的影片列表
    st.sidebar.title("已處理的影片")
    videos = get_processed_videos()
    
    if videos:
        for idx, video in enumerate(videos):
            if st.sidebar.button(f"{video.get('title', 'Unknown')[:50]}...", key=f"video_{idx}"):
                st.session_state.selected_video = video.get("video_id")
                st.rerun()
    else:
        st.sidebar.info("尚未處理任何影片")
    
    # 檢查是否有選擇的視頻
    if "selected_video" in st.session_state:
        display_video_summary(st.session_state.selected_video)
        if st.button("返回首頁"):
            del st.session_state.selected_video
            st.rerun()
        return
    
    # 主要界面 - URL輸入和參數設置
    with st.form("youtube_form"):
        url = st.text_input("輸入YouTube影片URL", "")
        
        col1, col2 = st.columns(2)
        
        with col1:
            language = st.selectbox(
                "選擇語言",
                ["zh-tw", "zh-cn", "en", "ja", "ko", "fr", "de", "es", "ru"],
                index=0
            )
        
        with col2:
            use_local_model = st.checkbox("使用本地Whisper模型", value=False)
            if use_local_model:
                st.info("使用本地模型需要安裝faster-whisper並下載模型文件")
        
        submit_button = st.form_submit_button("開始處理")
    
    if submit_button and url:
        result = process_youtube_video(url, language, use_local_model)
        
        if "error" in result:
            st.error(result["error"])
        else:
            # 處理成功後更新選擇的視頻ID並重新加載頁面
            st.session_state.selected_video = result.get("video_id")
            st.rerun()


if __name__ == "__main__":
    main() 