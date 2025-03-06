"""
YouTube影片摘要應用的工具函數
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Union

import yt_dlp
from faster_whisper import WhisperModel
from openai import OpenAI

from aithentic.utils.file_utils import ensure_dir, clean_filename

# 設置日誌記錄
logger = logging.getLogger(__name__)


def extract_video_id(url: str) -> Optional[str]:
    """
    從YouTube URL中提取視頻ID
    
    Args:
        url: YouTube URL
        
    Returns:
        視頻ID，如果無法提取則返回None
    """
    # 嘗試匹配各種YouTube URL格式
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def get_video_info(url: str) -> Dict:
    """
    獲取YouTube視頻的基本信息
    
    Args:
        url: YouTube URL
        
    Returns:
        視頻信息字典
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'best',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
    return {
        'id': info.get('id'),
        'title': info.get('title'),
        'description': info.get('description'),
        'duration': info.get('duration'),
        'view_count': info.get('view_count'),
        'channel': info.get('channel'),
        'upload_date': info.get('upload_date'),
        'thumbnail': info.get('thumbnail'),
    }


def download_youtube_audio(url: str, output_dir: str) -> Tuple[Optional[str], Optional[str]]:
    """
    從YouTube URL下載音頻
    
    Args:
        url: YouTube URL
        output_dir: 輸出目錄
        
    Returns:
        (音頻文件路徑, 視頻標題)的元組，如果下載失敗則返回(None, None)
    """
    try:
        # 確保目錄存在
        ensure_dir(output_dir)
        
        # 獲取視頻ID和標題
        video_id = extract_video_id(url)
        if not video_id:
            logger.error(f"無法從URL提取視頻ID: {url}")
            return None, None
        
        # 設置下載選項
        output_template = os.path.join(output_dir, f"{video_id}")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'outtmpl': output_template,
            'noplaylist': True,
        }
        
        # 下載音頻
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown Title')
            clean_title = clean_filename(title)
            
            # 下載完成後的檔案路徑
            audio_path = f"{output_template}.mp3"
            
            logger.info(f"下載完成: {title}")
            logger.info(f"音頻文件: {audio_path}")
            
            return audio_path, clean_title
    
    except Exception as e:
        logger.exception(f"下載YouTube音頻時發生錯誤: {str(e)}")
        return None, None


def transcribe_with_whisper(
    audio_file_path: str,
    model_size: str = "base",
    language: Optional[str] = "zh",
    local_model: bool = True,
) -> str:
    """
    使用Whisper模型轉錄音頻
    
    Args:
        audio_file_path: 音頻文件路徑
        model_size: 模型大小，例如 "tiny", "base", "small", "medium", "large"
        language: 音頻語言，如果為None則自動檢測
        local_model: 是否使用本地模型，如果為False則使用OpenAI API
        
    Returns:
        轉錄文本
    """
    try:
        if local_model:
            # 使用本地faster-whisper模型
            logger.info(f"使用本地Whisper模型 ({model_size}) 轉錄音頻")
            
            # 初始化模型
            model = WhisperModel(model_size)
            
            # 執行轉錄
            segments, info = model.transcribe(
                audio_file_path,
                language=language,
                beam_size=5,
                vad_filter=True,
            )
            
            # 合併所有片段
            transcript = " ".join([segment.text for segment in segments])
            
            logger.info(f"轉錄完成，檢測到的語言: {info.language}")
            
            return transcript
        else:
            # 使用OpenAI Whisper API
            logger.info("使用OpenAI Whisper API轉錄音頻")
            
            client = OpenAI()
            
            with open(audio_file_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    language=language,
                )
            
            return response.text
            
    except Exception as e:
        logger.exception(f"轉錄音頻時發生錯誤: {str(e)}")
        return f"轉錄失敗: {str(e)}" 