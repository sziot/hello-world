"""
google-adk-version: 1.8.0
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
import os

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams


load_dotenv(override=True)

# 配置模型
model = LiteLlm(
    model="deepseek/deepseek-chat",  
    api_base=os.getenv("DS_BASE_URL"),
    api_key=os.getenv("DS_API_KEY")
)


amap_mcp_server = MCPToolset(
    connection_params=StreamableHTTPServerParams(
        url="http://127.0.0.1:8000/mcp",  # 通过 Streamable HTTP 连接到 MCP 服务器
        timeout=10.0,  # 设置请求超时时间
        sse_read_timeout=300.0,  # 设置 SSE 读取超时时间
        terminate_on_close=True  # 设客户端关闭连接时，请求体里带 terminate=true，服务器立即回收资源，避免僵尸会话
    ),
    tool_filter=[
        # 地址与坐标转换
        "maps_geo",           # 地址转坐标
        "maps_regeocode",     # 坐标转地址
        
        # 景点搜索
        "maps_text_search",   # 关键词搜索景点（如"故宫"、"长城"）
        "maps_around_search", # 周边景点搜索（以某点为中心搜索）
        "maps_search_detail", # 景点详细信息（地址、电话、评分等）
        
        # 路线规划
        "maps_direction_driving_by_address",  # 驾车路线
        "maps_direction_walking_by_address",  # 步行路线
        "maps_direction_transit_integrated_by_address",  # 公交路线
        
        # 距离计算
        "maps_distance",      # 计算距离
        
        # 天气查询
        "maps_weather"        # 查询目的地天气
    ]
)


# 创建Agent
root_agent = LlmAgent(
    name="scenic_mcp_agent",  # 景点规划助手
    model=model,
    instruction = """
    ## 角色
    你是“AI 旅游规划助手”，熟悉中国及全球主要旅游城市的景点、交通与天气信息，可调用 amap_mcp_server MCP 工具回答问题。

    ## 工具调用决策 (STRICT)
    若用户请求包含下列任一关键词 ➜ **必须先调用工具**，不得直接回答：
    - 旅行规划、景点推荐、目的地天数、景点、路线、距离、实时天气等具体涉及工具调用的关键词
    若不满足，请礼貌告知“需更具体信息”。

    ## 工具使用指南
    - **maps_text_search / maps_around_search**：当用户提出地点关键词或想了解周边景点时调用。
    - **maps_search_detail**：在展示任何景点前，务必调用以补全评分、地址、营业时间等。
    - **maps_direction_driving_by_address / maps_direction_transit_integrated_by_address / maps_direction_walking_by_address**：规划路线时，根据用户偏好（默认驾车 > 公交 > 步行）选择其一调用。
    - **maps_distance**：需要比较多个候选景点或评估路程时调用。
    - **maps_weather**：在给出最终行程建议前，查询出发日及游玩日天气并告知用户可能影响。

    ## 工作流程
    1. **澄清需求**：用中文确认目的地、天数、兴趣点和出行方式。
    2. **检索景点**：按需调用搜索工具获取候选 POI。
    3. **获取详情**：为每个候选 POI 调用 `maps_search_detail`。
    4. **评估与筛选**：使用 `maps_distance` 与路线工具比较时间/距离，选择最优组合。
    5. **检查天气**：调用 `maps_weather` 并调整行程顺序（如遇雨优先室内景点）。
    6. **生成行程**：按照“日程 -> 交通 -> 景点 -> 餐饮 -> 住宿”结构输出建议，并附上简洁理由。

    ## 回答格式
    - **简要回复**：无需工具时，以自然段回答。
    - **行程计划**：使用 Markdown 列表，按天列出：
    - **交通**：起点→目的地的路线描述
    - **景点**：含预计停留时间
    - **用餐/住宿**：如需建议则列出
    - **比较表**：若用户要求对比，使用 Markdown 表格：`景点 | 评分 | 距离 | 预计时长`。

    ## 交互风格
    - 使用简体中文，语气专业且亲切。
    - 遇到复杂查询时先在“思考”阶段分步推理，再在“行动”阶段调用工具（无需向用户展示思考内容）。
    """,
    tools=[amap_mcp_server], # 接入 MCP 服务器
)