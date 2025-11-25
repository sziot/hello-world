import os
from dotenv import load_dotenv 
load_dotenv(override=True)

DeepSeek_API_KEY = os.getenv("DEEPSEEK_API_KEY")
# print(DeepSeek_API_KEY)  # 可以通过打印查看

### 1. 直接使用DeepSeek的API进行网络连通性测试 ###

from openai import OpenAI

# 初始化DeepSeek的API客户端
client = OpenAI(api_key=DeepSeek_API_KEY, base_url="https://api.deepseek.com")

# 调用DeepSeek的API，生成回答
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是乐于助人的助手，请根据用户的问题给出回答"},
        {"role": "user", "content": "你好，请你介绍一下你自己。"},
    ],
)

# 打印模型最终的响应结果
print(response.choices[0].message.content)

### 2. DeepSeek接入LangChain ###
from langchain.chat_models import init_chat_model

model = init_chat_model(model="deepseek-chat", model_provider="deepseek") 
# model使用的聊天模型名称deepseek-chat，而model_provider用来指定模型提供者

question = "你好，请你介绍一下你自己。"

result = model.invoke(question)
print("--- 使用deepseek-chat模型的输出 ---")
print(result.content)

result
# 显示result的值

model = init_chat_model(model="deepseek-reasoner", model_provider="deepseek")  
# model使用的推理模型名称deepseek-reasoner

result = model.invoke(question)
print("--- 使用deepseek-reasoner模型的输出 ---")
print(result.content)

### 3. 直接使用Dashscope的API ###
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv(override=True)
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    model="qwen-plus",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你是谁？"},
    ],
)

print("--- 测试DashScope通义千问模型API的连通性 ---")
print(completion.model_dump_json())

### 4. DashScope接入LangChain ###
from langchain_community.chat_models.tongyi import ChatTongyi
model = ChatTongyi()

question = "你好，请你介绍一下你自己。"

result = model.invoke(question)
print("--- DashScope接入LangChain ---")
print(result.content)
