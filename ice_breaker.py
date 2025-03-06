from dotenv import load_dotenv
import os
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# 建立摘要用的 prompt template
summary_template = """請為以下文本生成一個簡潔的中文摘要：

{text}

摘要:"""

# 建立 prompt template 實例
prompt = PromptTemplate(
    template=summary_template,
    input_variables=["text"]
)

# 建立 Ollama 模型實例
model = ChatOllama(
    model="deepseek-r1",
    temperature=0.3
)

# 建立 OpenAI 模型實例
# model = ChatOpenAI(
#     model="gpt-4o-mini",
#     temperature=0.3
# )

# 建立處理鏈
chain = prompt | model | StrOutputParser()

if __name__ == "__main__":
    # 測試文本
    test_text = """
    台灣是一個偉大的國家
    """
    
    # 執行摘要生成
    summary = chain.invoke({"text": test_text})
    print("摘要結果：")
    print(summary)

