"""
日誌工具模組，提供統一的日誌記錄功能
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional


def get_logger(
    name: str,
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_to_console: bool = True,
) -> logging.Logger:
    """
    獲取配置好的Logger實例
    
    Args:
        name: Logger名稱
        log_level: 日誌級別
        log_file: 日誌文件路徑，如果為None則不記錄到文件
        log_to_console: 是否輸出到控制台
        
    Returns:
        配置好的Logger實例
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 避免重複添加Handler
    if logger.handlers:
        return logger
    
    # 創建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 添加控制台輸出
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 添加文件輸出
    if log_file:
        # 確保日誌目錄存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_execution_time(logger: logging.Logger, level: int = logging.INFO):
    """
    記錄函數執行時間的裝飾器
    
    Args:
        logger: Logger實例
        level: 日誌級別
        
    Returns:
        裝飾器函數
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            logger.log(level, f"開始執行 {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()
                execution_time = end_time - start_time
                logger.log(level, f"完成執行 {func.__name__}, 耗時: {execution_time}")
                return result
            except Exception as e:
                end_time = datetime.now()
                execution_time = end_time - start_time
                logger.exception(f"執行 {func.__name__} 時發生錯誤, 耗時: {execution_time}, 錯誤: {str(e)}")
                raise
                
        return wrapper
    return decorator 