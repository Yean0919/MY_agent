"""MCP 客户端单元测试"""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.tools.mcp.client import MCPClient


def _make_mock_process():
    """创建一个模拟 MCP 服务器的假子进程。

    模拟的 stdout 会返回合法的 JSON-RPC initialize 响应和 tools/list 响应，
    让 MCPClient 的连接流程能正常走完。
    """
    responses = [
        # initialize 响应
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "mock-server", "version": "0.1.0"},
                },
            }
        ),
        # tools/list 响应
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "result": {
                    "tools": [
                        {"name": "mock_tool", "description": "A mock tool"},
                    ]
                },
            }
        ),
    ]

    mock_stdout = MagicMock()
    mock_stdout.readline.side_effect = [(r + "\n").encode("utf-8") for r in responses] + [
        b""
    ]  # 后续读取返回空

    mock_process = MagicMock()
    mock_process.poll.return_value = None  # 进程还在运行
    mock_process.stdin = MagicMock()
    mock_process.stdout = mock_stdout
    mock_process.stderr = MagicMock()

    return mock_process


class TestMCPClient:
    """MCP 客户端测试"""

    @pytest.mark.asyncio
    async def test_connect_disconnect(self):
        """测试连接和断开"""
        config = {"name": "test_server", "command": "python", "args": ["-m", "test"]}

        with patch("subprocess.Popen", return_value=_make_mock_process()):
            client = MCPClient(config)
            await client.connect()
            assert client.is_connected
            await client.disconnect()
            assert not client.is_connected

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """测试列出工具"""
        config = {"name": "test_server", "command": "python", "args": []}

        with patch("subprocess.Popen", return_value=_make_mock_process()):
            client = MCPClient(config)
            tools = await client.list_tools()
            assert isinstance(tools, list)
            assert len(tools) == 1
            assert tools[0]["name"] == "mock_tool"
