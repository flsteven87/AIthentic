"""
文件處理工具模組，提供常見的文件操作功能
"""

import os
import re
import json
import pickle
from typing import Any, Dict, List, Optional, Union


def clean_filename(filename: str) -> str:
    """
    清理檔案名稱，移除不合法字元
    
    Args:
        filename: 原始檔案名稱
        
    Returns:
        清理後的檔案名稱
    """
    # 移除不合法的檔案名稱字元
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def ensure_dir(directory: str) -> None:
    """
    確保目錄存在，如果不存在則創建
    
    Args:
        directory: 目錄路徑
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_json(data: Union[Dict, List], filepath: str, ensure_directory: bool = True) -> None:
    """
    將數據保存為JSON文件
    
    Args:
        data: 要保存的數據
        filepath: 文件路徑
        ensure_directory: 是否確保目錄存在
    """
    if ensure_directory:
        ensure_dir(os.path.dirname(filepath))
        
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(filepath: str) -> Union[Dict, List]:
    """
    從JSON文件加載數據
    
    Args:
        filepath: 文件路徑
        
    Returns:
        加載的數據
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_pickle(data: Any, filepath: str, ensure_directory: bool = True) -> None:
    """
    將數據保存為pickle文件
    
    Args:
        data: 要保存的數據
        filepath: 文件路徑
        ensure_directory: 是否確保目錄存在
    """
    if ensure_directory:
        ensure_dir(os.path.dirname(filepath))
        
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)


def load_pickle(filepath: str) -> Any:
    """
    從pickle文件加載數據
    
    Args:
        filepath: 文件路徑
        
    Returns:
        加載的數據
    """
    with open(filepath, 'rb') as f:
        return pickle.load(f) 