"""工具路由"""

from typing import Any

from fastapi import APIRouter

from src.tools.mcp.client import MCPClient
from src.tools.mcp.server_registry import MCPServerRegistry
from src.tools.registry import ToolRegistry
from src.tools.skills.registry import SkillRegistry

router = APIRouter()

# 模块级实例
_tool_registry = ToolRegistry()
_mcp_server_registry = MCPServerRegistry()
_skill_registry = SkillRegistry()

# 让 ToolRegistry 能访问 MCP 服务器
_tool_registry.set_mcp_registry(_mcp_server_registry)


@router.post("/mcp/connect")
async def connect_mcp_server(
    name: str, command: str, args: list[str] | None = None
) -> dict[str, Any]:
    """连接 MCP 服务器

    Args:
        name: 服务器名称
        command: 启动命令
        args: 命令行参数

    Returns:
        连接结果
    """
    if args is None:
        args = []

    try:
        client = MCPClient({"name": name, "command": command, "args": args})
        await client.connect()
        _mcp_server_registry.register_server(name, client)
        return {"status": "connected", "name": name, "is_connected": client.is_connected}
    except Exception as e:
        return {"status": "error", "name": name, "error": str(e)}


@router.post("/mcp/call")
async def call_mcp_tool(
    server_name: str, tool_name: str, arguments: dict[str, Any] | None = None
) -> dict[str, Any]:
    """调用 MCP 工具

    Args:
        server_name: 服务器名称
        tool_name: 工具名称
        arguments: 工具参数

    Returns:
        工具返回结果
    """
    if arguments is None:
        arguments = {}

    try:
        result = await _mcp_server_registry.call_tool(server_name, tool_name, arguments)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


@router.get("/mcp/list")
async def list_mcp_servers() -> dict[str, Any]:
    """列出已连接的 MCP 服务器

    Returns:
        服务器列表
    """
    servers = _mcp_server_registry.list_servers()
    return {"servers": servers, "count": len(servers)}


@router.get("/skills/list")
async def list_skills() -> dict[str, list[str]]:
    """列出可用 Skill

    Returns:
        Skill 列表
    """
    _skill_registry.scan()
    skills = _skill_registry.list()
    return {"skills": [s.get("name", "") for s in skills]}


@router.post("/skills/execute")
async def execute_skill(skill_name: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """执行 Skill

    Args:
        skill_name: Skill 名称
        params: 执行参数

    Returns:
        执行结果
    """
    if params is None:
        params = {}

    _skill_registry.scan()
    skill = _skill_registry.get(skill_name)
    if not skill:
        return {"error": f"Skill not found: {skill_name}"}

    # TODO: 实现 Skill 执行
    return {"result": f"Skill {skill_name} executed with params: {params}"}


@router.get("/tools/list")
async def list_tools() -> dict[str, list[str]]:
    """列出所有可用工具

    Returns:
        工具列表
    """
    tools = _tool_registry.list_tools()
    return {"tools": [t.get("name", "") for t in tools]}


@router.post("/tools/execute")
async def execute_tool(tool_name: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """执行工具

    Args:
        tool_name: 工具名称
        params: 工具参数

    Returns:
        执行结果
    """
    if params is None:
        params = {}

    result = await _tool_registry.call_tool(tool_name, params)
    return result
