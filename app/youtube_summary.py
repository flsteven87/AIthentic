import streamlit as st
import tempfile
import os
from openai import OpenAI
import time
from dotenv import load_dotenv
import yt_dlp
import re
import requests
import json
from faster_whisper import WhisperModel

# 設置頁面配置 - 必須是第一個 Streamlit 命令
st.set_page_config(page_title="YouTube Video Summarizer", layout="wide")

# 載入環境變數
load_dotenv()

# 從環境變數獲取 OpenAI API 金鑰
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

# Ollama API 設定
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# 確保目錄存在
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# 清理檔案名稱，移除不合法字元
def clean_filename(filename):
    # 移除不合法的檔案名稱字元
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_youtube_audio(url):
    """從 YouTube 網址下載音頻"""
    try:
        # 確保目錄存在
        data_dir = os.path.join(".", "data", "youtube_summary")
        ensure_dir(data_dir)
        
        # 使用 yt-dlp 下載影片
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
        
        # 先獲取影片信息
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'YouTube Video')
            thumbnail_url = info.get('thumbnail', None)
            video_id = info.get('id', '')
        
        st.write(f"Video Title: {video_title}")
        
        # 顯示影片縮圖
        if thumbnail_url:
            st.image(thumbnail_url)
        
        # 清理檔案名稱
        clean_title = clean_filename(video_title)
        
        # 創建以影片ID為名的資料夾
        video_dir = os.path.join(data_dir, video_id)
        ensure_dir(video_dir)
        
        # 設置檔案路徑 - 使用影片ID資料夾
        audio_file = os.path.join(video_dir, f"{clean_title}.mp3")
        
        # 設置下載路徑 - 注意這裡需要去掉.mp3後綴，因為postprocessor會自動添加
        output_template = os.path.join(video_dir, f"{clean_title}")
        ydl_opts['outtmpl'] = output_template
        
        # 下載音頻
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # 確認最終的音頻檔案路徑
        final_audio_file = f"{output_template}.mp3"
        if os.path.exists(final_audio_file):
            audio_file = final_audio_file
        
        # 保存影片基本信息到JSON檔案
        video_info = {
            "title": video_title,
            "id": video_id,
            "url": url,
            "thumbnail": thumbnail_url,
            "processed_date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(os.path.join(video_dir, "info.json"), "w", encoding="utf-8") as f:
            json.dump(video_info, f, ensure_ascii=False, indent=4)
        
        return audio_file, video_title, clean_title, video_dir
    except Exception as e:
        st.error(f"Error downloading video: {str(e)}")
        st.info("Note: Please verify the URL is correct, or YouTube may have restricted this video from being downloaded.")
        return None, None, None, None

def transcribe_with_faster_whisper(audio_file_path):
    """使用 Faster Whisper 本地模型進行語音轉文字"""
    try:
        # 載入模型（可選擇不同大小：tiny、base、small、medium、large-v3）
        model = WhisperModel("medium", device="cpu", compute_type="int8")
        
        # 進行轉錄
        segments, info = model.transcribe(audio_file_path, beam_size=5)
        
        # 組合所有文字
        transcription = " ".join([segment.text for segment in segments])
        
        return transcription
            
    except Exception as e:
        raise Exception(f"使用 Faster Whisper 轉錄時發生錯誤: {str(e)}")

def transcribe_audio(audio_file_path, clean_title, data_dir, use_local_model=False):
    """進行語音轉文字，可選擇使用 OpenAI Whisper API 或本地 Ollama 模型"""
    try:
        transcription_text = None
        
        if use_local_model:
            # 使用本地 Ollama 模型
            transcription_text = transcribe_with_faster_whisper(audio_file_path)
        else:
            # 使用 OpenAI Whisper API
            with open(audio_file_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                transcription_text = transcription.text
        
        if transcription_text:
            # 將轉錄文字保存到檔案
            transcript_file = os.path.join(data_dir, "transcript.txt")
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(transcription_text)
                
            return transcription_text, transcript_file
            
        return None, None
    except Exception as e:
        st.error(f"語音轉文字時發生錯誤: {e}")
        return None, None

def generate_summary(transcript, clean_title, data_dir, language="zh-tw"):
    """使用 GPT-4o 生成摘要"""
    try:
        # 根據語言設定適當的系統提示
        system_prompt = """You are a professional video content summarization expert, skilled at transforming lengthy video transcripts into structured, informative summary reports. Please follow this format for your summary:

1. First, provide a concise yet comprehensive summary paragraph (approximately 150-200 words) covering the main points, important details, and conclusions of the video.
2. Then, identify several major topics discussed in the video and create sections for each topic with bullet points.
3. If applicable, add a "Key Conclusions" or "Recommended Actions" section at the end.

Ensure your summary is:
- Logically structured, fluent, and accurately reflects the original content
- Free from information not mentioned in the video
- Inclusive of all important data, quotes, and technical terminology
- Presented in Markdown format, using appropriate heading levels, bold text, and bullet points

The summary should enable readers to understand the core content and value of the video without watching it."""
        
        # 添加語言指示到系統提示
        if language == "zh-tw":
            system_prompt += " Please write the summary in Traditional Chinese (zh-tw)."
        elif language == "zh-cn":
            system_prompt += " Please write the summary in Simplified Chinese (zh-cn)."
        elif language == "en":
            system_prompt += " Please write the summary in English."
        # 可以根據需要添加更多語言選項
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please generate a structured summary report for the following video transcript:\n\n{transcript}"}
            ]
        )
        
        summary = response.choices[0].message.content
        
        # 將摘要保存到檔案
        summary_file = os.path.join(data_dir, "summary.txt")
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)
            
        # 保存語言信息
        with open(os.path.join(data_dir, "language.txt"), "w", encoding="utf-8") as f:
            f.write(language)
            
        return summary, summary_file
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None, None

# 獲取所有已處理的影片
def get_processed_videos():
    data_dir = os.path.join(".", "data", "youtube_summary")
    if not os.path.exists(data_dir):
        return []
    
    videos = []
    for video_id in os.listdir(data_dir):
        video_dir = os.path.join(data_dir, video_id)
        info_file = os.path.join(video_dir, "info.json")
        
        if os.path.isdir(video_dir) and os.path.exists(info_file):
            try:
                with open(info_file, "r", encoding="utf-8") as f:
                    info = json.load(f)
                videos.append(info)
            except:
                continue
    
    # 按處理日期排序，最新的在前
    videos.sort(key=lambda x: x.get("processed_date", ""), reverse=True)
    return videos

# 顯示特定影片的摘要
def display_video_summary(video_id):
    data_dir = os.path.join(".", "data", "youtube_summary")
    video_dir = os.path.join(data_dir, video_id)
    
    if not os.path.exists(video_dir):
        st.error("找不到該影片的資料")
        return
    
    # 讀取影片信息
    info_file = os.path.join(video_dir, "info.json")
    if os.path.exists(info_file):
        with open(info_file, "r", encoding="utf-8") as f:
            info = json.load(f)
        
        st.header(info["title"])
        st.write(f"YouTube URL: {info['url']}")
        
        if info.get("thumbnail"):
            st.image(info["thumbnail"])
    
    # 讀取摘要
    summary_file = os.path.join(video_dir, "summary.txt")
    if os.path.exists(summary_file):
        with open(summary_file, "r", encoding="utf-8") as f:
            summary = f.read()
        
        st.markdown(summary)
        
        # 提供下載摘要功能
        st.download_button(
            label="下載摘要",
            data=summary,
            file_name=f"{video_id}_summary.txt",
            mime="text/plain"
        )
    
    # 顯示字幕 (可折疊)
    transcript_file = os.path.join(video_dir, "transcript.txt")
    if os.path.exists(transcript_file):
        with open(transcript_file, "r", encoding="utf-8") as f:
            transcript = f.read()
        
        with st.expander("查看完整字幕"):
            st.write(transcript)
            
            # 提供下載字幕功能
            st.download_button(
                label="下載字幕",
                data=transcript,
                file_name=f"{video_id}_transcript.txt",
                mime="text/plain"
            )

# 主應用邏輯
def main():
    # 側邊欄 - 顯示已處理的影片列表
    with st.sidebar:
        st.title("已處理的影片")
        
        # 新增影片按鈕
        if st.button("新增影片摘要", key="new_video_button"):
            st.session_state["current_video"] = None
        
        # 顯示已處理的影片列表
        videos = get_processed_videos()
        if not videos:
            st.info("尚未處理任何影片")
        else:
            for video in videos:
                if st.button(f"{video['title'][:30]}...", key=f"video_{video['id']}"):
                    st.session_state["current_video"] = video["id"]
    
    # 初始化 session state
    if "current_video" not in st.session_state:
        st.session_state["current_video"] = None
    
    # 主內容區域
    if st.session_state["current_video"] is None:
        # 顯示新增影片表單
        st.title("YouTube Video Summarizer")
        st.write("輸入 YouTube 網址以獲取 AI 生成的影片摘要")
        
        youtube_url = st.text_input("輸入 YouTube 影片網址:")
        
        # 添加語言選擇選項
        language_options = {
            "繁體中文 (zh-tw)": "zh-tw",
            "簡體中文 (zh-cn)": "zh-cn",
            "英文 (en)": "en"
        }
        selected_language = st.selectbox(
            "選擇摘要語言:",
            options=list(language_options.keys()),
            index=0  # 預設選擇繁體中文
        )
        
        # 添加模型選擇選項
        use_local_model = st.checkbox("使用本地 Whisper 模型 (需要安裝 Ollama)", value=False)
        
        if st.button("生成摘要", key="generate_summary_button"):
            if not youtube_url:
                st.warning("請輸入有效的 YouTube 網址")
            else:
                with st.spinner("處理中..."):
                    # 使用 status 元素顯示處理進度
                    status_container = st.empty()
                    
                    # 步驟 1: 下載音頻
                    status_container.info("步驟 1: 正在下載 YouTube 音頻...")
                    audio_file, video_title, clean_title, video_dir = download_youtube_audio(youtube_url)
                    
                    if audio_file:
                        # 步驟 2: 轉寫音頻
                        status_container.info(f"步驟 2: 正在使用{'本地' if use_local_model else 'OpenAI'} Whisper 模型將音頻轉換為文字...")
                        transcript, transcript_file = transcribe_audio(audio_file, clean_title, video_dir, use_local_model)
                        
                        if transcript:
                            # 步驟 3: 生成摘要
                            status_container.info("步驟 3: 正在使用 GPT-4o 生成摘要...")
                            # 獲取選擇的語言代碼
                            language_code = language_options[selected_language]
                            summary, summary_file = generate_summary(transcript, clean_title, video_dir, language=language_code)
                            
                            if summary:
                                # 清除狀態訊息
                                status_container.empty()
                                
                                # 顯示摘要報告
                                st.header(video_title)
                                st.markdown(summary)
                                
                                # 提供字幕查看選項（可折疊）
                                with st.expander("查看完整字幕"):
                                    st.write(transcript)
                                    st.download_button(
                                        label="下載字幕",
                                        data=transcript,
                                        file_name=f"{clean_title}_transcript.txt",
                                        mime="text/plain"
                                    )
                                
                                # 提供下載摘要功能
                                st.download_button(
                                    label="下載摘要",
                                    data=summary,
                                    file_name=f"{clean_title}_summary.txt",
                                    mime="text/plain"
                                )
                                
                                # 顯示檔案保存位置
                                st.success(f"所有檔案已保存在: {video_dir}")
                                
                                # 處理完成後，將當前影片設置為剛處理的影片
                                import re
                                video_id = re.search(r'/([\w-]+)$', video_dir).group(1)
                                st.session_state["current_video"] = video_id
                                st.rerun()
    else:
        # 顯示已處理的影片摘要
        display_video_summary(st.session_state["current_video"])

# 執行主應用
if __name__ == "__main__":
    main()

# 添加頁腳
st.markdown("---")
st.markdown("This application uses OpenAI's Whisper API for speech-to-text and GPT-4o for summary generation.")
