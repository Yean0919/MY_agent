"""MCP 服务器注册表单元测试"""

from src.tools.mcp.client import MCPClient
from src.tools.mcp.server_registry import MCPServerRegistry


class TestMCPServerRegistry:
    """MCP 服务器注册表测试"""

    def test_register_unregister(self):
        """测试注册和注销"""
        registry = MCPServerRegistry()
        client = MCPClient({"name": "test"})

        registry.register_server("test", client)
        assert "test" in registry.list_servers()

        registry.unregister_server("test")
        assert "test" not in registry.list_servers()

    def test_get_server(self):
        """测试获取服务器"""
        registry = MCPServerRegistry()
        client = MCPClient({"name": "test"})

        registry.register_server("test", client)
        result = registry.get_server("test")

        assert result == client

    def test_get_nonexistent_server(self):
        """测试获取不存在的服务器"""
        registry = MCPServerRegistry()
        result = registry.get_server("nonexistent")

        assert result is None
