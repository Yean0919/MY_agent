"""工具注册表 - 统一管理所有可用工具"""

from typing import Any

from src.tools.builtin.bash import BashTool
from src.tools.builtin.edit import EditTool
from src.tools.builtin.read import ReadTool
from src.tools.builtin.search import SearchTool
from src.tools.builtin.write import WriteTool
from src.tools.mcp.server_registry import MCPServerRegistry


class ToolRegistry:
    """工具注册表，管理内置工具、MCP 工具和 Skill 工具"""

    def __init__(self) -> None:
        self._builtin_tools: dict[str, Any] = {}
        self._mcp_registry: MCPServerRegistry | None = None
        self._init_builtin_tools()

    def _init_builtin_tools(self) -> None:
        """初始化内置工具"""
        self._builtin_tools = {
            "read": ReadTool(),
            "write": WriteTool(),
            "edit": EditTool(),
            "bash": BashTool(timeout=60),
            "search": SearchTool(),
        }

    def set_mcp_registry(self, registry: MCPServerRegistry) -> None:
        """设置 MCP 服务器注册表

        Args:
            registry: MCP 服务器注册表
        """
        self._mcp_registry = registry

    def list_tools(self) -> list[dict[str, Any]]:
        """列出所有可用工具

        Returns:
            工具描述列表，每项包含 name, description, parameters
        """
        tools: list[dict[str, Any]] = []

        # 内置工具
        builtin_descriptions = {
            "read": {
                "name": "read",
                "description": "Read the contents of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the file"},
                        "encoding": {
                            "type": "string",
                            "description": "File encoding",
                            "default": "utf-8",
                        },
                    },
                    "required": ["file_path"],
                },
            },
            "write": {
                "name": "write",
                "description": "Write content to a file (creates directories if needed)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the file"},
                        "content": {"type": "string", "description": "Content to write"},
                        "encoding": {
                            "type": "string",
                            "description": "File encoding",
                            "default": "utf-8",
                        },
                    },
                    "required": ["file_path", "content"],
                },
            },
            "edit": {
                "name": "edit",
                "description": "Edit a file by replacing text",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the file"},
                        "old_string": {"type": "string", "description": "Text to find and replace"},
                        "new_string": {"type": "string", "description": "Replacement text"},
                        "encoding": {
                            "type": "string",
                            "description": "File encoding",
                            "default": "utf-8",
                        },
                    },
                    "required": ["file_path", "old_string", "new_string"],
                },
            },
            "bash": {
                "name": "bash",
                "description": "Execute a shell command",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell command to execute"},
                        "cwd": {"type": "string", "description": "Working directory (optional)"},
                    },
                    "required": ["command"],
                },
            },
            "search": {
                "name": "search",
                "description": "Search for text in files",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Text pattern to search for"},
                        "path": {
                            "type": "string",
                            "description": "Directory to search in",
                            "default": ".",
                        },
                        "file_pattern": {
                            "type": "string",
                            "description": "File glob pattern",
                            "default": "*",
                        },
                        "context": {
                            "type": "integer",
                            "description": "Lines of context",
                            "default": 0,
                        },
                    },
                    "required": ["pattern"],
                },
            },
        }

        tools.extend(builtin_descriptions.values())

        # MCP 工具
        if self._mcp_registry:
            for server_name in self._mcp_registry.list_servers():
                server = self._mcp_registry.get_server(server_name)
                if server and server.is_connected:
                    try:
                        import asyncio

                        mcp_tools = asyncio.run(server.list_tools())
                        for tool in mcp_tools:
                            tool["name"] = f"mcp:{server_name}:{tool.get('name', '')}"
                            tools.append(tool)
                    except Exception:
                        pass

        return tools

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """调用工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        # MCP 工具
        if tool_name.startswith("mcp:"):
            parts = tool_name.split(":", 2)
            if len(parts) == 3 and self._mcp_registry:
                server_name = parts[1]
                mcp_tool_name = parts[2]
                try:
                    result = await self._mcp_registry.call_tool(
                        server_name, mcp_tool_name, arguments
                    )
                    return {"success": True, "result": result}
                except Exception as e:
                    return {"success": False, "error": str(e)}
            return {"success": False, "error": f"Invalid MCP tool name: {tool_name}"}

        # 内置工具
        tool = self._builtin_tools.get(tool_name)
        if not tool:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        try:
            result = await tool.execute(**arguments)
            return {"success": True, "tool": tool_name, "result": result}
        except Exception as e:
            return {"success": False, "tool": tool_name, "error": str(e)}

    def get_builtin_tool_names(self) -> list[str]:
        """获取内置工具名称列表

        Returns:
            工具名称列表
        """
        return list(self._builtin_tools.keys())
