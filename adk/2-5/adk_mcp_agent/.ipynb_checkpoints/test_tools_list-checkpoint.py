"""
google-adk-version: 1.8.0
"""

import asyncio
import os
from dotenv import load_dotenv
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

load_dotenv(override=True)


async def list_mcp_tools():
    """列出 MCP 服务器中的所有可用工具"""
    
    # 构建 MCP Server
    amap_mcp_server = MCPToolset(
        connection_params=StreamableHTTPServerParams(
            url="http://127.0.0.1:8001/mcp",  # 通过 Streamable HTTP 连接到 MCP 服务器
            timeout=10.0,  # 设置请求超时时间
            sse_read_timeout=300.0,  # 设置 SSE 读取超时时间
            terminate_on_close=True  # 设客户端关闭连接时，请求体里带 terminate=true，服务器立即回收资源，避免僵尸会话
        )
    )
    
    try:
        # 获取所有的工具列表清单
        tools = await amap_mcp_server.get_tools()
        print(f"=== 共发现 {len(tools)} 个 MCP 工具 ===\n")
        for i, tool in enumerate(tools, 1):
            print(f"{i}. 工具名称: {tool.name}")
            print(f"   描述: {tool.description}")
    finally:
        await amap_mcp_server.close()

if __name__ == "__main__":
    asyncio.run(list_mcp_tools())