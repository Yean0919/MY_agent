"""MCP 客户端 - 使用 stdio 协议连接 MCP 服务器"""

import asyncio
import contextlib
import json
import subprocess
from typing import Any, cast


class MCPClient:
    """MCP 客户端，通过 stdio 协议连接 MCP 服务器"""

    def __init__(self, server_config: dict[str, Any]):
        self.server_config = server_config
        self._process: subprocess.Popen[bytes] | None = None
        self._connected = False
        self._request_id = 0
        self._tools_cache: list[dict[str, Any]] = []

    async def connect(self) -> None:
        """连接 MCP 服务器"""
        command = self.server_config.get("command", "")
        args = self.server_config.get("args", [])
        env = self.server_config.get("env", {})

        if not command:
            raise ValueError("MCP server command is required")

        # 构建环境变量
        full_env = dict(__import__("os").environ)
        full_env.update(env)
        # MCP 协议要求设置 MCP 相关环境变量
        full_env["PYTHONUNBUFFERED"] = "1"

        # 启动子进程
        self._process = subprocess.Popen(
            [command] + args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=full_env,
        )

        if not self._process or self._process.poll() is not None:
            raise RuntimeError(f"Failed to start MCP server: {command}")

        # 发送 initialize 请求
        await self._send_jsonrpc(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "tca-client", "version": "0.1.0"},
            },
        )

        # 等待 initialize 响应
        response = await self._receive_jsonrpc(timeout=10.0)
        if response and "error" not in response:
            # 发送 initialized 通知
            await self._send_notification("notifications/initialized", {})
            self._connected = True

            # 获取工具列表
            await self._fetch_tools()
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            self._disconnect_process()
            raise RuntimeError(f"MCP initialization failed: {error_msg}")

    async def _fetch_tools(self) -> None:
        """获取服务器工具列表"""
        try:
            await self._send_jsonrpc("tools/list", {})
            response = await self._receive_jsonrpc(timeout=10.0)
            if response and "result" in response:
                self._tools_cache = response["result"].get("tools", [])
        except Exception:
            # 工具列表获取失败，使用空列表
            self._tools_cache = []

    async def _send_jsonrpc(self, method: str, params: dict[str, Any]) -> None:
        """发送 JSON-RPC 请求"""
        self._request_id += 1
        message = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params,
        }
        await self._write_line(message)

    async def _send_notification(self, method: str, params: dict[str, Any]) -> None:
        """发送 JSON-RPC 通知（无 id）"""
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }
        await self._write_line(message)

    async def _write_line(self, message: dict[str, Any]) -> None:
        """写入一行 JSON 消息到 stdin"""
        if not self._process or self._process.stdin is None:
            raise RuntimeError("MCP process not available")

        line = json.dumps(message, ensure_ascii=False) + "\n"
        self._process.stdin.write(line.encode("utf-8"))
        self._process.stdin.flush()

    async def _receive_jsonrpc(self, timeout: float = 30.0) -> dict[str, Any] | None:
        """接收一行 JSON-RPC 消息"""
        if not self._process or self._process.stdout is None:
            return None

        try:
            # 使用 asyncio 包装同步读取
            line_bytes = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._process.stdout.readline(),  # type: ignore[union-attr]
                ),
                timeout=timeout,
            )
            if not line_bytes:
                return None

            line = line_bytes.decode("utf-8").strip()
            if not line:
                return None

            return cast(dict[str, Any], json.loads(line))
        except asyncio.TimeoutError:
            return None
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    async def disconnect(self) -> None:
        """断开连接"""
        self._disconnect_process()
        self._connected = False
        self._tools_cache = []

    def _disconnect_process(self) -> None:
        """关闭子进程"""
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except Exception:
                with contextlib.suppress(Exception):
                    self._process.kill()
            self._process = None

    async def list_tools(self) -> list[dict[str, Any]]:
        """列出可用工具

        Returns:
            工具列表
        """
        if not self._connected:
            await self.connect()

        # 刷新工具列表
        await self._fetch_tools()
        return self._tools_cache

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """调用工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具返回结果
        """
        if not self._connected:
            await self.connect()

        # 发送 tools/call 请求
        await self._send_jsonrpc(
            "tools/call",
            {"name": tool_name, "arguments": arguments},
        )

        # 等待响应
        response = await self._receive_jsonrpc(timeout=60.0)
        if not response:
            raise RuntimeError(f"Tool call timed out: {tool_name}")

        if "error" in response:
            raise RuntimeError(f"Tool call error: {response['error']}")

        return response.get("result", {})

    @property
    def is_connected(self) -> bool:
        """检查是否已连接

        Returns:
            是否已连接
        """
        if not self._connected:
            return False
        if self._process and self._process.poll() is not None:
            self._connected = False
            return False
        return True
