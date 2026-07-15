"""MCP 服务器注册表"""

from typing import Any

from src.tools.mcp.client import MCPClient


class MCPServerRegistry:
    """MCP 服务器注册表，管理所有已连接的 MCP 服务器"""

    def __init__(self) -> None:
        self._servers: dict[str, MCPClient] = {}

    def register_server(self, name: str, client: MCPClient) -> None:
        """注册 MCP 服务器

        Args:
            name: 服务器名称
            client: MCP 客户端
        """
        if not name:
            raise ValueError("Server name cannot be empty")
        self._servers[name] = client

    def unregister_server(self, name: str) -> None:
        """注销 MCP 服务器

        Args:
            name: 服务器名称
        """
        if name in self._servers:
            client = self._servers[name]
            if client.is_connected:
                import asyncio

                asyncio.create_task(client.disconnect())
        self._servers.pop(name, None)

    def get_server(self, name: str) -> MCPClient | None:
        """获取 MCP 服务器

        Args:
            name: 服务器名称

        Returns:
            MCP 客户端或 None
        """
        return self._servers.get(name)

    def list_servers(self) -> list[str]:
        """列出所有已注册的服务器

        Returns:
            服务器名称列表
        """
        return list(self._servers.keys())

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """调用 MCP 工具

        Args:
            server_name: 服务器名称
            tool_name: 工具名称
            arguments: 参数

        Returns:
            工具返回结果

        Raises:
            ValueError: 服务器不存在
        """
        server = self._servers.get(server_name)
        if not server:
            raise ValueError(f"Server not found: {server_name}")
        return await server.call_tool(tool_name, arguments)

    def get_server_count(self) -> int:
        """获取服务器数量

        Returns:
            服务器数量
        """
        return len(self._servers)
