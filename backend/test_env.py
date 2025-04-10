"""
測試環境變數加載
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 嘗試從項目根目錄加載 .env
print("當前工作目錄:", os.getcwd())

# 直接從根目錄加載
root_env = Path(__file__).resolve().parent.parent / ".env"
print(f".env 文件路徑: {root_env}")
print(f".env 文件存在: {root_env.exists()}")

# 嘗試加載
print("嘗試加載 .env 文件...")
load_dotenv(dotenv_path=root_env)

# 檢查 OPENAI_API_KEY
openai_key = os.environ.get("OPENAI_API_KEY")
if openai_key:
    key_first_5 = openai_key[:5]
    key_last_4 = openai_key[-4:]
    print(f"OPENAI_API_KEY: {key_first_5}...{key_last_4}")
else:
    print("OPENAI_API_KEY 未設置")

# 顯示所有加載的環境變數
print("\n所有環境變數:")
for key, value in os.environ.items():
    if any(keyword in key.lower() for keyword in ["openai", "api", "key", "supabase"]):
        # 對於敏感信息只顯示部分
        if len(value) > 10:
            value = value[:5] + "..." + value[-4:]
        print(f"{key}: {value}") 