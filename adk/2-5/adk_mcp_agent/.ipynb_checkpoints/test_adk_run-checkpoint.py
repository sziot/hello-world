from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types    
import asyncio
import os
load_dotenv(override=True)


APP_NAME = "chatbot"
USER_ID = "user_1"
SESSION_ID = "session_002"

# 配置模型
model = LiteLlm(
    model="deepseek/deepseek-chat",  
    api_base=os.getenv("DS_BASE_URL"),
    api_key=os.getenv("DS_API_KEY")
)


# 创建Agent
root_agent = LlmAgent(
    name="chatbot",  # 聊天机器人
    model=model,
    instruction="""
    你是一个聊天机器人，请根据用户的问题进行回答。
    """,
)

async def chat(session_service: InMemorySessionService, query: str):
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    runner = Runner(
        agent=root_agent, 
        app_name=APP_NAME,   
        session_service=session_service 
    )
    
    content = types.Content(role='user', parts=[types.Part(text=query)])

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID, 
        new_message=content,
    ):
        if event.content and event.content.parts:    
            if event.content.parts[0].text:
                print(f"最终响应: {event.content.parts[0].text}")


if __name__ == "__main__":
    query = "你好，请你详细的介绍一下你自己"
    asyncio.run(chat(session_service=InMemorySessionService(), query=query))

