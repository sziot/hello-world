from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

import os
from dotenv import load_dotenv
load_dotenv(override=True)

DS_API_KEY = os.getenv("DS_API_KEY")
DS_BASE_URL = os.getenv("DS_BASE_URL")

model = LiteLlm(
    model="deepseek/deepseek-chat",  
    api_base=DS_BASE_URL,
    api_key=DS_API_KEY
)

root_agent = Agent(
    name="simple_agent",
    model=model,
    instruction="你是一个乐于助人的中文助手。",
    description="回答用户的问题。"
)