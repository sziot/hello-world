import os
from dotenv import load_dotenv
load_dotenv(override=True)


# 检查环境变量
amap_api_key = os.getenv("AMAP_API_KEY")
print(f"1. 环境变量检查:")
print(f"   AMAP_API_KEY: {'已设置' if amap_api_key else '未设置'}")

if amap_api_key:
    print(f"   API Key 长度: {len(amap_api_key)} 字符")
    print(f"   API Key 前10位: {amap_api_key[:10]}...")

# 测试认证配置创建
print(f"\n2. 测试认证配置创建:")
try:
    from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
    
    if amap_api_key:
        # 使用 ADK 官方推荐的方式创建 API Key 认证
        auth_scheme, auth_credential = token_to_scheme_credential(
            "apikey",           # token_type: API Key 类型
            "header",            # location: 查询参数位置
            "X-API-KEY",              # name: 参数名
            amap_api_key        # credential_value: API Key 值
        )
        
        print("   使用 ADK 官方方式创建认证配置成功")
        print(f"   auth_scheme: {auth_scheme}")
        print(f"   auth_credential: {auth_credential}")
    else:
        print("   环境变量未设置，无法创建认证配置")
        
except Exception as e:
    print(f"   创建认证配置时出错: {e}")

# 测试 MCP 工具集创建
print(f"\n3. 测试 MCP 工具集创建:")
try:
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

    # 创建认证配置
    if amap_api_key:
        # 使用 ADK 官方推荐的方式创建 API Key 认证
        auth_scheme, auth_credential = token_to_scheme_credential(
            "apikey",           # token_type: API Key 类型
            "header",            # location: 查询参数位置
            "X-API-KEY",              # name: 参数名
            amap_api_key        # credential_value: API Key 值
        )
        
    else:
        auth_scheme = None
        auth_credential = None
    
    # 构建 MCP Server
    amap_mcp_server = MCPToolset(
        connection_params=StreamableHTTPServerParams(
            url="http://127.0.0.1:8000/mcp",  # 通过 Streamable HTTP 连接到 MCP 服务器
            timeout=10.0,  # 设置请求超时时间
            sse_read_timeout=300.0,  # 设置 SSE 读取超时时间
            terminate_on_close=True  # 设客户端关闭连接时，请求体里带 terminate=true，服务器立即回收资源，避免僵尸会话
        ),
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
        tool_filter=["maps_geo"]
    )
    
    print("   MCP 工具集创建成功")
    print(f"   auth_scheme: {amap_mcp_server._auth_scheme}")
    print(f"   auth_credential: {amap_mcp_server._auth_credential}")
    
except Exception as e:
    print(f"   创建 MCP 工具集时出错: {e}") 