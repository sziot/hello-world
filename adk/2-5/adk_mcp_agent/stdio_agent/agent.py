"""
google-adk-version: 1.8.0
"""
import os
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_toolset import StdioServerParameters, StdioConnectionParams  
load_dotenv(override=True)

# 配置模型
model = LiteLlm(
    model="deepseek/deepseek-chat",  
    api_base=os.getenv("DS_BASE_URL"),
    api_key=os.getenv("DS_API_KEY")
)

# 获取当前文件的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 提取 MCP 服务器路径
server_path = os.path.join(current_dir, "..", "..", "mcp_servers", "amap-mcp-server", "amap_mcp_server", "server.py")

# 构建 MCP Server
amap_mcp_server = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[server_path],
            encoding="utf-8",
        ),
        timeout=10.0 # 设置请求超时时间
    )
)

# 创建Agent
root_agent = LlmAgent(
    name="scenic_mcp_agent",  # 景点规划助手
    model=model,
    instruction="""
    你是一个专业的旅游规划助手，专门为用户推荐景点和制定旅游计划。
    当用户提出旅游规划需求时，你需要根据用户的需求，灵活调用`amap_mcp_server`工具来提供个性化的旅游规划服务。
    
    你的主要功能包括但不限于：
    1. 景点推荐：使用 maps_text_search 搜索和推荐合适的景点
    2. 路线规划：使用 maps_direction_* 系列工具规划路线
    3. 距离计算：使用 maps_distance 计算景点间的距离
    4. 天气查询：使用 maps_weather 查询目的地天气
    5. 详细信息：使用 maps_search_detail 获取景点详细信息
    6. 地理编码：使用 maps_geo 将地址转换为坐标
    7. 周边搜索：使用 maps_around_search 搜索周边设施
    
    工作流程：
    1. 理解用户需求（目的地、兴趣、时间等）
    2. 搜索相关景点和POI
    3. 获取景点详细信息
    4. 规划最优路线
    5. 查询天气情况
    6. 提供完整的旅游建议
    """,
    tools=[amap_mcp_server], # 接入 MCP 服务器
)